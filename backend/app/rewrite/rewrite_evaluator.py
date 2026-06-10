"""Multi-metric rewrite evaluation engine.

Evaluates a rewritten resume across five dimensions and produces a
composite ``rewrite_quality`` score that replaces the previous ATS-only
acceptance criterion.

Score formula
-------------
rewrite_quality =
    ATS             * 0.35
  + Readability     * 0.20
  + Semantic        * 0.20
  + SectionQuality  * 0.15
  + KeywordDensity  * 0.10

All component scores are on a 0–100 scale.
"""

from __future__ import annotations

import re
import string
from dataclasses import dataclass, field
from typing import Any

# ---------------------------------------------------------------------------
# Score weights
# ---------------------------------------------------------------------------

_WEIGHTS: dict[str, float] = {
    "ats_score": 0.35,
    "readability": 0.20,
    "semantic_similarity": 0.20,
    "section_quality": 0.15,
    "keyword_density": 0.10,
}

_OPTIMAL_KW_DENSITY = 0.03   # 3 % keyword density is the sweet-spot target
_KW_DENSITY_TOLERANCE = 0.02  # ±2 % around optimal scores 100


# ---------------------------------------------------------------------------
# Public result dataclass
# ---------------------------------------------------------------------------


@dataclass
class EvaluationResult:
    """Scores for one candidate resume."""

    ats_score: float
    semantic_similarity: float
    readability: float
    keyword_density: float
    section_quality: float
    hallucination_risk: float
    rewrite_quality: float = field(init=False)

    def __post_init__(self) -> None:
        self.rewrite_quality = round(
            self.ats_score * _WEIGHTS["ats_score"]
            + self.readability * _WEIGHTS["readability"]
            + self.semantic_similarity * _WEIGHTS["semantic_similarity"]
            + self.section_quality * _WEIGHTS["section_quality"]
            + self.keyword_density * _WEIGHTS["keyword_density"],
            2,
        )

    def to_dict(self) -> dict[str, float]:
        return {
            "ats_score": round(self.ats_score, 2),
            "semantic_similarity": round(self.semantic_similarity, 4),
            "readability": round(self.readability, 2),
            "keyword_density": round(self.keyword_density, 2),
            "section_quality": round(self.section_quality, 2),
            "hallucination_risk": round(self.hallucination_risk, 2),
            "rewrite_quality": self.rewrite_quality,
        }


# ---------------------------------------------------------------------------
# Component scorers
# ---------------------------------------------------------------------------


def _count_syllables(word: str) -> int:
    """Rough syllable count for one lowercase English word."""
    word = word.lower().strip(string.punctuation)
    if not word:
        return 0
    # Vowel-cluster heuristic
    count = len(re.findall(r"[aeiouy]+", word))
    # Trailing silent -e
    if word.endswith("e") and count > 1:
        count -= 1
    return max(1, count)


def _readability_score(text: str) -> float:
    """Simplified Flesch Reading Ease mapped to 0–100 (higher = more readable).

    Flesch RE = 206.835 − 1.015 × (words/sentences) − 84.6 × (syllables/words)
    Standard scale: 0–30 very hard, 60–70 standard, 90–100 very easy.
    We clamp and return it directly on 0–100.
    """
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    words = [w for w in re.split(r"\s+", text) if w.strip()]
    if not sentences or not words:
        return 50.0
    n_sentences = max(1, len(sentences))
    n_words = max(1, len(words))
    n_syllables = sum(_count_syllables(w) for w in words)
    fre = 206.835 - 1.015 * (n_words / n_sentences) - 84.6 * (n_syllables / n_words)
    return round(max(0.0, min(100.0, fre)), 2)


def _keyword_density_score(resume_text: str, jd_keywords: list[str]) -> float:
    """Score keyword density: 100 when density ≈ optimal, tapers off above/below.

    Density = (# keyword occurrences) / (# resume words).
    Penalise both under-use (<1 %) and stuffing (>6 %).
    """
    if not jd_keywords:
        return 75.0
    lower_text = resume_text.lower()
    words = re.split(r"\s+", lower_text)
    n_words = max(1, len(words))
    hits = sum(lower_text.count(kw.lower()) for kw in jd_keywords)
    density = hits / n_words
    distance = abs(density - _OPTIMAL_KW_DENSITY)
    if distance <= _KW_DENSITY_TOLERANCE:
        score = 100.0
    else:
        # Linear decay: at 3× tolerance → score = 50
        decay = max(0.0, 1.0 - (distance - _KW_DENSITY_TOLERANCE) / (_KW_DENSITY_TOLERANCE * 2))
        score = 50.0 + 50.0 * decay
    return round(score, 2)


def _section_quality_score(resume: dict[str, Any]) -> float:
    """Evaluate structural completeness of a parsed resume (0–100).

    Checks: experience with bullet points, skills list, education, projects/certs.
    """
    score = 0.0
    max_score = 100.0

    # --- Contact info (10 pts) ---
    if resume.get("email") or resume.get("phone"):
        score += 10.0

    # --- Skills (20 pts) ---
    skills = resume.get("skills", [])
    if len(skills) >= 10:
        score += 20.0
    elif len(skills) >= 5:
        score += 12.0
    elif skills:
        score += 5.0

    # --- Experience (35 pts) ---
    experience = resume.get("experience", [])
    if experience:
        score += 10.0
        # Each role with ≥3 bullets earns extra credit (up to 25 pts)
        bullet_bonus = 0.0
        for role in experience:
            bullets = role.get("bullets", []) or role.get("responsibilities", [])
            if len(bullets) >= 3:
                bullet_bonus += 5.0
        score += min(25.0, bullet_bonus)

    # --- Education (15 pts) ---
    education = resume.get("education", [])
    if education:
        score += 15.0

    # --- Projects / certifications (20 pts) ---
    projects = resume.get("projects", [])
    certs = resume.get("certifications", [])
    if projects:
        score += 10.0
    if certs:
        score += 10.0

    return round(min(score, max_score), 2)


def _hallucination_risk_score(
    original_text: str,
    rewritten_text: str,
    jd_text: str = "",
) -> float:
    """Compute a 0–100 trust score using the HallucinationGuard.

    Delegates to :mod:`app.rewrite.hallucination_guard` which performs
    fact-level verification: skills, certifications, degrees, numeric
    claims, and proper nouns are each checked independently.

    100 = no invented facts detected; 0 = heavily hallucinated.
    """
    from app.rewrite.hallucination_guard import compute_hallucination_trust_score
    return compute_hallucination_trust_score(original_text, rewritten_text, jd_text)


# ---------------------------------------------------------------------------
# Main evaluator
# ---------------------------------------------------------------------------


class RewriteEvaluator:
    """Evaluate a rewritten resume against the original and the job description."""

    def evaluate(
        self,
        *,
        original_text: str,
        rewritten_text: str,
        rewritten_resume: dict[str, Any],
        ats_score: float,
        semantic_similarity: float,
        jd_keywords: list[str] | None = None,
        jd_text: str = "",
    ) -> EvaluationResult:
        """Return a fully-populated :class:`EvaluationResult`.

        Parameters
        ----------
        original_text:
            Plain-text of the original (pre-rewrite) resume.
        rewritten_text:
            Plain-text of the candidate rewritten resume.
        rewritten_resume:
            Parsed JSON structure of *rewritten_text* (from ``build_resume_json``).
        ats_score:
            ATS compatibility score (0–100) already computed by the ATS engine.
        semantic_similarity:
            Cosine similarity (0–1) from the embedding engine; multiplied by 100
            internally to put it on the same scale as the other metrics.
        jd_keywords:
            Optional list of keywords extracted from the job description.
        jd_text:
            Raw job description text used by the hallucination guard to allow
            JD-mirrored language without penalising it.
        """
        sem_pct = float(semantic_similarity) * 100.0

        readability = _readability_score(rewritten_text)
        kw_density = _keyword_density_score(rewritten_text, jd_keywords or [])
        section_quality = _section_quality_score(rewritten_resume)
        hallucination_risk = _hallucination_risk_score(original_text, rewritten_text, jd_text)

        return EvaluationResult(
            ats_score=float(ats_score),
            semantic_similarity=sem_pct,
            readability=readability,
            keyword_density=kw_density,
            section_quality=section_quality,
            hallucination_risk=hallucination_risk,
        )
