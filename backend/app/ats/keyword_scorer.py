"""ATS keyword scorer with keyword-stuffing detection."""

from __future__ import annotations

_STUFFING_RATIO_THRESHOLD = 3.0
_MAX_STUFFING_PENALTY = 20.0


def calculate_keyword_score(
    skill_match_score: float,
    resume_skill_count: int = 0,
    jd_skill_count: int = 0,
) -> float:
    score = float(skill_match_score)

    if jd_skill_count > 0 and resume_skill_count > 0:
        ratio = resume_skill_count / jd_skill_count
        if ratio > _STUFFING_RATIO_THRESHOLD:
            excess = ratio - _STUFFING_RATIO_THRESHOLD
            penalty = min(
                _MAX_STUFFING_PENALTY,
                (excess / _STUFFING_RATIO_THRESHOLD) * _MAX_STUFFING_PENALTY,
            )
            score = max(0.0, score - penalty)

    return round(min(100.0, max(0.0, score)), 2)
