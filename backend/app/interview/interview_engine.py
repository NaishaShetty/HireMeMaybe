"""Interview Preparation Engine — Stage 9.

Given a resume and a job description, generates:

1. **Likely interview questions** — drawn from overlap between resume claims
   and JD requirements, each annotated with the reason it was surfaced.
2. **Weakness questions** — probing questions for skills the resume lacks
   that the JD requires.
3. **STAR answer drafts** — structured Situation / Task / Action / Result
   answer skeletons built *exclusively* from content found in the resume
   (no hallucination).

The engine delegates generation to the same LLM infrastructure used by the
RewriteEngine (OpenAI / Gemini / Anthropic), with a full runtime fallback
chain so that if one provider returns a 429 / quota error another is tried.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = (
    "You are an expert interview coach who prepares candidates for job interviews. "
    "You only use facts that appear explicitly in the candidate's resume — you never "
    "invent experience, companies, skills, or achievements. "
    "Return valid JSON only, no markdown fences, no commentary."
)

_QUESTIONS_PROMPT = """\
You are preparing a candidate for a job interview.

=== RESUME ===
{resume_text}

=== JOB DESCRIPTION ===
{jd_text}

=== MATCHED SKILLS ===
{matched_skills}

=== MISSING SKILLS ===
{missing_skills}

Generate two lists of interview questions and STAR answer drafts in this exact JSON structure:
{{
  "likely_questions": [
    {{
      "question": "Tell me about your experience with <skill>.",
      "reason": "Skill appears in both resume and JD",
      "category": "technical|behavioural|situational"
    }}
  ],
  "weakness_questions": [
    {{
      "question": "Do you have experience with <missing skill>?",
      "reason": "Required in JD but not found in resume",
      "how_to_handle": "Brief advice for answering this question honestly"
    }}
  ],
  "star_answers": [
    {{
      "question": "Tell me about a time you <achievement>.",
      "situation": "Context from resume",
      "task": "What you were responsible for",
      "action": "What you did (from resume only)",
      "result": "Outcome or impact mentioned in resume",
      "source": "Which resume section this is drawn from"
    }}
  ]
}}

Rules:
- Generate 5–8 likely_questions covering technical depth, behavioural, and situational areas
- Generate 3–5 weakness_questions for the most critical missing skills
- Generate 3–5 star_answers using only facts from the resume
- how_to_handle should give practical, honest advice (e.g. "Acknowledge the gap and mention your plan to learn it")
- Do NOT invent any facts, companies, tools, or achievements
- Return ONLY valid JSON, no preamble, no fences
"""


# ---------------------------------------------------------------------------
# Provider record
# ---------------------------------------------------------------------------

@dataclass
class _Provider:
    name: str
    client: Any
    model: str


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclass
class InterviewPrepResult:
    likely_questions: list[dict[str, Any]] = field(default_factory=list)
    weakness_questions: list[dict[str, Any]] = field(default_factory=list)
    star_answers: list[dict[str, Any]] = field(default_factory=list)
    matched_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "likely_questions": self.likely_questions,
            "weakness_questions": self.weakness_questions,
            "star_answers": self.star_answers,
            "matched_skills": self.matched_skills,
            "missing_skills": self.missing_skills,
        }


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


class InterviewEngine:
    """Generate interview preparation content from a resume and job description."""

    def __init__(self) -> None:
        self._providers: list[_Provider] = []
        self._init_providers()

    # ------------------------------------------------------------------
    # Provider initialisation — build ordered list of all available providers
    # ------------------------------------------------------------------

    def _init_providers(self) -> None:
        preferred = os.getenv("REWRITE_PROVIDER", "OPENAI").upper()
        order = [preferred.lower()] + [p for p in ("openai", "gemini", "anthropic") if p != preferred.lower()]
        for name in order:
            p = getattr(self, f"_try_init_{name}")()
            if p:
                self._providers.append(p)

        if not self._providers:
            logger.warning(
                "InterviewEngine: no LLM provider available. "
                "Set OPENAI_API_KEY, GEMINI_API_KEY, or ANTHROPIC_API_KEY."
            )
        else:
            logger.info("InterviewEngine providers: %s", [p.name for p in self._providers])

    def _try_init_openai(self) -> "_Provider | None":
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            return None
        try:
            from openai import OpenAI  # type: ignore[import]
            client = OpenAI(api_key=api_key)
            return _Provider("openai", client, os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
        except ImportError:
            return None

    def _try_init_gemini(self) -> "_Provider | None":
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            return None
        try:
            from google import genai  # type: ignore[import]
            client = genai.Client(api_key=api_key)
            return _Provider("gemini", client, os.getenv("GEMINI_MODEL", "gemini-2.0-flash"))
        except ImportError:
            return None

    def _try_init_anthropic(self) -> "_Provider | None":
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            return None
        try:
            import anthropic  # type: ignore[import]
            client = anthropic.Anthropic(api_key=api_key)
            return _Provider("anthropic", client, os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022"))
        except ImportError:
            return None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(
        self,
        *,
        resume_text: str,
        jd_text: str,
        matched_skills: list[str] | None = None,
        missing_skills: list[str] | None = None,
    ) -> InterviewPrepResult:
        """Generate interview prep content with runtime provider fallback."""
        matched = matched_skills or []
        missing = missing_skills or []

        prompt = _QUESTIONS_PROMPT.format(
            resume_text=resume_text[:4000],
            jd_text=jd_text[:2000],
            matched_skills=", ".join(matched[:20]) if matched else "none listed",
            missing_skills=", ".join(missing[:20]) if missing else "none identified",
        )

        raw_json: dict[str, Any] = {}
        for provider in self._providers:
            try:
                raw_text = self._call_provider(provider, prompt)
                raw_json = self._parse_json(raw_text)
                if raw_json:
                    logger.info("InterviewEngine used provider: %s", provider.name)
                    break
            except Exception as exc:
                logger.warning("InterviewEngine provider %s failed: %s", provider.name, exc)
                continue

        if not raw_json:
            logger.info("InterviewEngine falling back to rule-based generation")
            raw_json = self._rule_based_fallback(matched, missing)

        return InterviewPrepResult(
            likely_questions=raw_json.get("likely_questions", []),
            weakness_questions=raw_json.get("weakness_questions", []),
            star_answers=raw_json.get("star_answers", []),
            matched_skills=matched,
            missing_skills=missing,
        )

    # ------------------------------------------------------------------
    # LLM call dispatch
    # ------------------------------------------------------------------

    def _call_provider(self, provider: _Provider, prompt: str) -> str:
        if provider.name == "openai":
            response = provider.client.chat.completions.create(
                model=provider.model,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=2000,
                temperature=0.3,
            )
            return response.choices[0].message.content or ""

        if provider.name == "gemini":
            full_prompt = f"{_SYSTEM_PROMPT}\n\n{prompt}"
            response = provider.client.models.generate_content(
                model=provider.model, contents=full_prompt
            )
            return response.text or ""

        if provider.name == "anthropic":
            response = provider.client.messages.create(
                model=provider.model,
                max_tokens=2000,
                system=_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text if response.content else ""

        raise RuntimeError(f"Unknown provider: {provider.name}")

    # ------------------------------------------------------------------
    # JSON parsing
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_json(text: str) -> dict[str, Any]:
        """Extract JSON from LLM response, stripping markdown fences if present."""
        cleaned = text.strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                return json.loads(match.group())
            raise

    # ------------------------------------------------------------------
    # Rule-based fallback (no LLM)
    # ------------------------------------------------------------------

    @staticmethod
    def _rule_based_fallback(
        matched_skills: list[str],
        missing_skills: list[str],
    ) -> dict[str, Any]:
        likely: list[dict[str, Any]] = []
        for skill in matched_skills[:5]:
            likely.append({
                "question": f"Tell me about your experience with {skill}.",
                "reason": f"{skill} appears in both your resume and the job description.",
                "category": "technical",
            })
        likely.append({
            "question": "Describe a challenging project and how you overcame obstacles.",
            "reason": "Standard behavioural question for all roles.",
            "category": "behavioural",
        })

        weakness: list[dict[str, Any]] = []
        for skill in missing_skills[:5]:
            weakness.append({
                "question": f"Do you have experience with {skill}?",
                "reason": f"{skill} is required in the job description but was not found in your resume.",
                "how_to_handle": (
                    f"Be honest about your current level with {skill}. "
                    "Mention any adjacent experience or your willingness to learn quickly."
                ),
            })

        return {
            "likely_questions": likely,
            "weakness_questions": weakness,
            "star_answers": [],
        }
