"""Post-generation hallucination guard for resume rewrites.

Performs output-level verification by comparing the rewritten resume
against a factual inventory extracted from the original.

Checks:
  1. Skills — no new skills may appear that weren't in the original
  2. Proper nouns — companies, universities, tool names, certifications
  3. Numeric claims — years of experience, percentages, dollar amounts
  4. Degree keywords — no invented qualifications

Returns a ``HallucinationReport`` with a 0–100 trust score and a list
of specific violations so callers can decide whether to reject the rewrite.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Sequence

from app.parsers.skill_parser import extract_skills


# ---------------------------------------------------------------------------
# Patterns for extracting factual entities
# ---------------------------------------------------------------------------

_DEGREE_KEYWORDS = {
    "bachelor", "master", "phd", "doctorate", "b.s", "b.e", "m.s", "m.e",
    "mba", "b.tech", "m.tech", "b.sc", "m.sc", "associate", "diploma",
    "b.a", "m.a", "llb", "llm", "b.com", "m.com",
}

_CERT_PATTERNS = re.compile(
    r"\b(?:AWS|GCP|Azure|PMP|CPA|CFA|CISSP|CEH|CISM|CISA|CCNA|CCNP|"
    r"CompTIA|ITIL|Scrum|CKA|CKAD|Terraform|Google Cloud|Oracle|Salesforce)"
    r"[^\n,;]{0,40}\b",
    re.IGNORECASE,
)

_METRIC_PATTERN = re.compile(
    r"(?:\d+\s*%|\$\s*\d[\d,]*(?:\.\d+)?[kmb]?|\d+\+?\s*(?:years?|yrs?|months?))",
    re.IGNORECASE,
)

_PROPER_NOUN_PATTERN = re.compile(
    r"\b[A-Z][a-zA-Z0-9+#.\-]{1,}(?:\s+[A-Z][a-zA-Z0-9+#.\-]{1,}){0,3}\b"
)

_NOISE_WORDS = {
    "i", "the", "a", "an", "and", "or", "in", "at", "for", "of", "on",
    "to", "by", "as", "is", "was", "are", "were", "be", "been",
    "experience", "skills", "resume", "work", "background", "profile",
    "summary", "objective", "education", "projects", "certifications",
    "responsibilities", "achievements", "january", "february", "march",
    "april", "may", "june", "july", "august", "september", "october",
    "november", "december", "present", "current", "remote", "hybrid",
    "full-time", "part-time", "intern", "senior", "junior", "lead",
    "engineer", "developer", "manager", "analyst", "designer",
}


# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------

def _extract_proper_nouns(text: str) -> set[str]:
    tokens = _PROPER_NOUN_PATTERN.findall(text)
    result: set[str] = set()
    for tok in tokens:
        lower = tok.strip().lower()
        if len(lower) > 2 and lower not in _NOISE_WORDS:
            result.add(lower)
    return result


def _extract_metrics(text: str) -> set[str]:
    return {m.strip().lower() for m in _METRIC_PATTERN.findall(text)}


def _extract_degrees(text: str) -> set[str]:
    found: set[str] = set()
    lower = text.lower()
    for kw in _DEGREE_KEYWORDS:
        if re.search(r"\b" + re.escape(kw) + r"\b", lower):
            found.add(kw)
    return found


def _extract_certs(text: str) -> set[str]:
    return {m.strip().lower() for m in _CERT_PATTERNS.findall(text)}


# ---------------------------------------------------------------------------
# Report dataclass
# ---------------------------------------------------------------------------

@dataclass
class HallucinationReport:
    """Result of the hallucination verification pass."""

    trust_score: float          # 0–100 (100 = clean, 0 = heavily hallucinated)
    violations: list[str] = field(default_factory=list)
    new_skills: list[str] = field(default_factory=list)
    new_proper_nouns: list[str] = field(default_factory=list)
    new_metrics: list[str] = field(default_factory=list)
    new_degrees: list[str] = field(default_factory=list)
    new_certs: list[str] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        """Return True when no violations were found."""
        return len(self.violations) == 0

    def to_dict(self) -> dict:
        return {
            "trust_score": round(self.trust_score, 2),
            "is_clean": self.is_clean,
            "violations": self.violations,
            "new_skills": self.new_skills,
            "new_proper_nouns": self.new_proper_nouns,
            "new_metrics": self.new_metrics,
            "new_degrees": self.new_degrees,
            "new_certs": self.new_certs,
        }


# ---------------------------------------------------------------------------
# Main guard
# ---------------------------------------------------------------------------

class HallucinationGuard:
    """Verify that a rewritten resume does not introduce invented facts.

    Usage::

        guard = HallucinationGuard()
        report = guard.verify(original_text, rewritten_text)
        if not report.is_clean:
            # reject or flag the rewrite
            print(report.violations)
    """

    # How much each category penalises the trust score
    _PENALTY_PER_NEW_SKILL       = 8.0
    _PENALTY_PER_NEW_CERT        = 10.0
    _PENALTY_PER_NEW_DEGREE      = 15.0
    _PENALTY_PER_NEW_METRIC      = 5.0
    _PENALTY_PER_NEW_PROPER_NOUN = 2.0
    _MAX_PROPER_NOUN_PENALTY     = 20.0   # cap noisy penalty

    def verify(
        self,
        original_text: str,
        rewritten_text: str,
        *,
        jd_text: str = "",
    ) -> HallucinationReport:
        """Compare *rewritten_text* against *original_text* (and optionally *jd_text*).

        Entities that appear in the JD are treated as acceptable additions
        (the model is expected to mirror JD language) unless they represent
        fabricated qualifications.
        """
        allowed_extra = _extract_proper_nouns(jd_text) if jd_text else set()

        # --- skills -------------------------------------------------------
        orig_skills  = set(extract_skills(original_text))
        rew_skills   = set(extract_skills(rewritten_text))
        jd_skills    = set(extract_skills(jd_text)) if jd_text else set()
        new_skills   = rew_skills - orig_skills - jd_skills

        # --- certifications -----------------------------------------------
        orig_certs = _extract_certs(original_text)
        rew_certs  = _extract_certs(rewritten_text)
        new_certs  = rew_certs - orig_certs

        # --- degrees ------------------------------------------------------
        orig_degrees = _extract_degrees(original_text)
        rew_degrees  = _extract_degrees(rewritten_text)
        new_degrees  = rew_degrees - orig_degrees

        # --- numeric metrics ----------------------------------------------
        orig_metrics = _extract_metrics(original_text)
        rew_metrics  = _extract_metrics(rewritten_text)
        new_metrics  = rew_metrics - orig_metrics

        # --- proper nouns -------------------------------------------------
        orig_nouns = _extract_proper_nouns(original_text) | allowed_extra
        rew_nouns  = _extract_proper_nouns(rewritten_text)
        new_nouns  = rew_nouns - orig_nouns

        # --- build violations list ----------------------------------------
        violations: list[str] = []

        for skill in sorted(new_skills):
            violations.append(f"Invented skill: '{skill}'")

        for cert in sorted(new_certs):
            violations.append(f"Invented certification: '{cert}'")

        for degree in sorted(new_degrees):
            violations.append(f"Invented degree/qualification: '{degree}'")

        for metric in sorted(new_metrics):
            violations.append(f"Invented numeric claim: '{metric}'")

        # Only report proper nouns if there are many unexpected ones
        flagged_nouns = sorted(new_nouns)[:5]  # top 5 to avoid noise
        if len(new_nouns) >= 4:
            for noun in flagged_nouns:
                violations.append(f"Potentially invented entity: '{noun}'")

        # --- compute trust score ------------------------------------------
        penalty = 0.0
        penalty += len(new_skills)   * self._PENALTY_PER_NEW_SKILL
        penalty += len(new_certs)    * self._PENALTY_PER_NEW_CERT
        penalty += len(new_degrees)  * self._PENALTY_PER_NEW_DEGREE
        penalty += len(new_metrics)  * self._PENALTY_PER_NEW_METRIC
        penalty += min(
            len(new_nouns) * self._PENALTY_PER_NEW_PROPER_NOUN,
            self._MAX_PROPER_NOUN_PENALTY,
        )

        trust_score = max(0.0, 100.0 - penalty)

        return HallucinationReport(
            trust_score=trust_score,
            violations=violations,
            new_skills=sorted(new_skills),
            new_proper_nouns=sorted(new_nouns),
            new_metrics=sorted(new_metrics),
            new_degrees=sorted(new_degrees),
            new_certs=sorted(new_certs),
        )


# ---------------------------------------------------------------------------
# Convenience function (mirrors old API surface)
# ---------------------------------------------------------------------------

def compute_hallucination_trust_score(
    original_text: str,
    rewritten_text: str,
    jd_text: str = "",
) -> float:
    """Return a 0–100 trust score (drop-in replacement for the old risk score)."""
    guard = HallucinationGuard()
    return guard.verify(original_text, rewritten_text, jd_text=jd_text).trust_score
