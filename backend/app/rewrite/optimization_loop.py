"""Optimization Loop V2 — multi-candidate rewrite selection (Stage 7 / Stage 8)."""
from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Any, Sequence

from app.ats.ats_scorer import calculate_ats_score
from app.matcher.match_engine import match_resume_to_jd
from app.parsers.contact_parser import extract_email, extract_phone
from app.parsers.section_parser import extract_sections
from app.parsers.skill_parser import extract_skills
from app.rewrite.prompt_builder import PromptBuilder
from app.rewrite.rewrite_engine import RewriteEngine
from app.rewrite.rewrite_evaluator import EvaluationResult, RewriteEvaluator
from app.services.resume_builder import build_resume_json
from app.similarity.similarity_engine import calculate_similarity

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CandidateResult:
    attempt: int
    resume_text: str
    ats_score: float
    rewrite_quality: float
    evaluation: dict

    def to_dict(self):
        return {
            "attempt": self.attempt,
            "ats_score": round(self.ats_score, 2),
            "rewrite_quality": round(self.rewrite_quality, 2),
            "evaluation": self.evaluation,
        }


@dataclass(frozen=True)
class OptimizationResult:
    before_score: float
    after_score: float
    improvement: float
    accepted: bool
    candidate_resume: str
    optimized_resume: str
    attempts: list
    changes: list
    evaluation: dict

    def to_dict(self):
        return {
            "before_score": self.before_score,
            "after_score": self.after_score,
            "improvement": self.improvement,
            "accepted": self.accepted,
            "candidate_resume": self.candidate_resume,
            "optimized_resume": self.optimized_resume,
            "attempts": self.attempts,
            "changes": self.changes,
            "evaluation": self.evaluation,
        }


@dataclass(frozen=True)
class OptimizationDebugResult:
    original_resume: str
    candidate_resume: str
    parsed_original_resume: dict
    parsed_candidate_resume: dict
    original_ats_score: float
    candidate_ats_score: float
    accepted: bool
    reason: str

    def to_dict(self):
        return {
            "original_resume": self.original_resume,
            "candidate_resume": self.candidate_resume,
            "parsed_original_resume": self.parsed_original_resume,
            "parsed_candidate_resume": self.parsed_candidate_resume,
            "original_ats_score": self.original_ats_score,
            "candidate_ats_score": self.candidate_ats_score,
            "accepted": self.accepted,
            "reason": self.reason,
        }


class OptimizationLoop:
    """Rewrite a resume N times, evaluate each with multi-metric scoring, keep the best."""

    def __init__(self, max_passes=1, num_candidates=None, rewrite_engine=None):
        passes = num_candidates if num_candidates is not None else max_passes
        self.max_passes = max(1, int(passes))
        self.rewrite_engine = rewrite_engine or RewriteEngine()
        self._evaluator = RewriteEvaluator()

    def optimize(self, *, resume, jd, resume_text, jd_text, recommendations=None):
        result, _debug = self._run(resume=resume, jd=jd, resume_text=resume_text, jd_text=jd_text, recommendations=recommendations)
        return result.to_dict()

    def optimize_with_debug(self, *, resume, jd, resume_text, jd_text, recommendations=None):
        result, debug_result = self._run(resume=resume, jd=jd, resume_text=resume_text, jd_text=jd_text, recommendations=recommendations)
        return {"result": result.to_dict(), "debug": debug_result.to_dict()}

    def _run(self, *, resume, jd, resume_text, jd_text, recommendations=None):
        original_ats = self._ats_score(resume, jd)
        original_semantic = float(calculate_similarity(resume_text, jd_text))
        jd_keywords = self._extract_jd_keywords(jd)
        original_eval = self._evaluator.evaluate(
            original_text=resume_text, rewritten_text=resume_text, rewritten_resume=resume,
            ats_score=original_ats, semantic_similarity=original_semantic, jd_keywords=jd_keywords,
        )
        baseline_quality = original_eval.rewrite_quality

        original_snapshot = self._parse_resume_text(resume_text)
        original_skill_count = len(original_snapshot.get("skills", []))
        original_section_count = self._section_count(original_snapshot)
        recommendation_list = list(recommendations or [])
        candidates = []
        candidate_text = resume_text
        last_candidate_parsed = original_snapshot
        last_candidate_resume = resume_text

        logger.info("Optimization start — baseline ATS: %.1f  baseline quality: %.1f  passes: %d",
                    original_ats, baseline_quality, self.max_passes)

        for attempt_index in range(self.max_passes):
            prompt = PromptBuilder.build(resume_text=candidate_text, jd_text=jd_text, recommendations=recommendation_list)
            try:
                rewritten_text = self.rewrite_engine.rewrite(prompt)
            except Exception as exc:
                logger.warning("Rewrite attempt %d failed: %s", attempt_index + 1, exc)
                break

            if not isinstance(rewritten_text, str) or not rewritten_text.strip():
                logger.warning("Rewrite attempt %d returned empty; skipping", attempt_index + 1)
                break

            rewritten_resume = self._parse_resume_text(rewritten_text)
            rewritten_ats = self._ats_score(rewritten_resume, jd)
            rewritten_semantic = float(calculate_similarity(rewritten_text, jd_text))

            self._log_parser_health(
                original_snapshot=original_snapshot, candidate_snapshot=rewritten_resume,
                original_skill_count=original_skill_count, original_section_count=original_section_count,
            )

            eval_result = self._evaluator.evaluate(
                original_text=resume_text, rewritten_text=rewritten_text, rewritten_resume=rewritten_resume,
                ats_score=rewritten_ats, semantic_similarity=rewritten_semantic, jd_keywords=jd_keywords,
            )

            candidate = CandidateResult(
                attempt=attempt_index + 1,
                resume_text=rewritten_text,
                ats_score=rewritten_ats,
                rewrite_quality=eval_result.rewrite_quality,
                evaluation=eval_result.to_dict(),
            )
            candidates.append(candidate)
            last_candidate_parsed = rewritten_resume
            last_candidate_resume = rewritten_text

            logger.info("Candidate %d — ATS: %.1f  quality: %.1f", attempt_index + 1, rewritten_ats, eval_result.rewrite_quality)
            candidate_text = rewritten_text

        best_candidate = None
        if candidates:
            best_candidate = max(candidates, key=lambda c: c.rewrite_quality)

        accepted = (best_candidate is not None and best_candidate.rewrite_quality >= baseline_quality)

        if accepted and best_candidate is not None:
            selected_text = best_candidate.resume_text
            selected_quality = best_candidate.rewrite_quality
            selected_ats = best_candidate.ats_score
            selected_eval = best_candidate.evaluation
        else:
            selected_text = resume_text
            selected_quality = baseline_quality
            selected_ats = original_ats
            selected_eval = original_eval.to_dict()

        logger.info("Selected: %s (quality %.1f vs baseline %.1f)",
                    "rewritten" if accepted else "original", selected_quality, baseline_quality)

        attempts_list = [c.to_dict() for c in candidates]
        if accepted and best_candidate is not None:
            for item in attempts_list:
                if item["attempt"] == best_candidate.attempt:
                    item["selected"] = True

        changes = ["Selected rewritten resume" if selected_text != resume_text else "Kept original resume"]

        debug_result = OptimizationDebugResult(
            original_resume=resume_text,
            candidate_resume=last_candidate_resume,
            parsed_original_resume=original_snapshot,
            parsed_candidate_resume=last_candidate_parsed,
            original_ats_score=round(float(original_ats), 2),
            candidate_ats_score=round(float(selected_ats), 2),
            accepted=accepted,
            reason=(
                f"Candidate quality ({selected_quality:.1f}) >= baseline ({baseline_quality:.1f})"
                if accepted
                else f"No candidate improved on baseline quality ({baseline_quality:.1f})"
            ),
        )

        result = OptimizationResult(
            before_score=round(float(original_ats), 2),
            after_score=round(float(selected_ats), 2),
            improvement=round(float(selected_ats - original_ats), 2),
            accepted=accepted,
            candidate_resume=last_candidate_resume,
            optimized_resume=selected_text,
            attempts=attempts_list,
            changes=changes,
            evaluation=selected_eval,
        )
        return result, debug_result

    def _ats_score(self, resume, jd):
        match_result = match_resume_to_jd(resume, jd)
        return calculate_ats_score(resume, jd, match_result)

    def _parse_resume_text(self, text):
        email = extract_email(text)
        phone = extract_phone(text)
        skills = extract_skills(text)
        sections = extract_sections(text)
        return build_resume_json(email=email, phone=phone, skills=skills, sections=sections)

    @staticmethod
    def _extract_jd_keywords(jd):
        keywords = []
        for field in ("required_skills", "preferred_skills", "technologies", "keywords"):
            value = jd.get(field, [])
            if isinstance(value, list):
                keywords.extend(str(v) for v in value if v)
        return list(dict.fromkeys(keywords))

    @staticmethod
    def _section_count(resume):
        return sum(1 for name in ("education", "experience", "projects", "certifications") if resume.get(name))

    def _log_parser_health(self, *, original_snapshot, candidate_snapshot, original_skill_count, original_section_count):
        candidate_skill_count = len(candidate_snapshot.get("skills", []))
        candidate_section_count = self._section_count(candidate_snapshot)
        if candidate_skill_count < original_skill_count:
            logger.warning("Skill extraction dropped from %s to %s skills", original_skill_count, candidate_skill_count)
        if candidate_section_count < original_section_count:
            logger.warning("Section extraction dropped from %s to %s sections", original_section_count, candidate_section_count)
