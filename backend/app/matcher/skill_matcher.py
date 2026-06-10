"""Skill matcher with embedding-based semantic matching.

Matching tiers (in order):
1. Exact lowercase match
2. Substring match (resume contains JD skill as a word boundary)
3. Semantic embedding similarity via sentence-transformers (cosine >= EMBED_THRESHOLD)
"""

from __future__ import annotations

import re
import numpy as np

EMBED_THRESHOLD = 0.72  # cosine similarity threshold for semantic match


def _normalize(skill: str) -> str:
    return skill.lower().strip()


def _is_substring_match(skill: str, resume_text: str) -> bool:
    pattern = r"\b" + re.escape(skill) + r"\b"
    return bool(re.search(pattern, resume_text, re.IGNORECASE))


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


def get_matched_skills(
    resume_skills: list,
    jd_skills: list,
    resume_text: str = "",
) -> list:
    from app.similarity.model_loader import get_model  # lazy import to avoid circular deps

    resume_lower = [_normalize(s) for s in resume_skills]
    resume_set = set(resume_lower)
    resume_full_text = resume_text.lower()

    matched = []

    # Pre-compute embeddings for all resume skills (batch for speed)
    model = get_model()
    resume_embeddings: list[np.ndarray] | None = None

    for jd_skill in jd_skills:
        norm_jd = _normalize(jd_skill)

        # Tier 1: exact match
        if norm_jd in resume_set:
            matched.append(jd_skill)
            continue

        # Tier 2: substring match in raw resume text
        if resume_full_text and _is_substring_match(norm_jd, resume_full_text):
            matched.append(jd_skill)
            continue

        # Tier 3: semantic embedding similarity
        if resume_lower:
            # Lazy-init batch embeddings on first Tier-3 hit
            if resume_embeddings is None:
                resume_embeddings = model.encode(
                    resume_lower, convert_to_numpy=True, batch_size=64
                )

            jd_emb = model.encode(norm_jd, convert_to_numpy=True)
            for res_emb in resume_embeddings:
                if _cosine(jd_emb, res_emb) >= EMBED_THRESHOLD:
                    matched.append(jd_skill)
                    break

    return matched
