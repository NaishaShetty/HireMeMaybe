"""Job Description builder — parses raw JD text into structured JSON."""

from __future__ import annotations

import re

from app.parsers.jd_skill_parser import extract_jd_skills
from app.parsers.jd_requirements_parser import extract_experience_requirement
from app.parsers.jd_section_parser import extract_responsibilities

# ---------------------------------------------------------------------------
# Job title extraction
# ---------------------------------------------------------------------------

_TITLE_HEADER_RE = re.compile(
    r"^(?:job\s+title|position|role|title)\s*[:\-]\s*(.+)$",
    re.IGNORECASE | re.MULTILINE,
)

_TITLE_KEYWORDS = re.compile(
    r"\b(engineer|developer|analyst|manager|scientist|architect|designer|"
    r"consultant|specialist|lead|director|coordinator|intern|associate|"
    r"senior|junior|staff|principal|head\s+of|vp|vice\s+president)\b",
    re.IGNORECASE,
)

_MARKDOWN_NOISE_RE = re.compile(r"^[#*_`>|\s]+|[#*_`>|\s]+$")


def _strip_markdown(line: str) -> str:
    """Remove leading/trailing markdown symbols (**, ##, __, etc.) from a line."""
    return _MARKDOWN_NOISE_RE.sub("", line).strip()


def _extract_job_title(text):
    m = _TITLE_HEADER_RE.search(text)
    if m:
        return m.group(1).strip()
    # Scan the first 15 non-empty lines for a short title-like line.
    # The old code had a `break` after the first non-matching line, so it
    # only ever checked one line — that's why job_title was always null on
    # JDs whose first line is a company name, location header, or preamble.
    checked = 0
    for line in text.splitlines():
        clean = _strip_markdown(line)
        if not clean:
            continue
        if len(clean.split()) <= 8 and _TITLE_KEYWORDS.search(clean):
            return clean
        checked += 1
        if checked >= 15:
            break
    return None


# ---------------------------------------------------------------------------
# Preferred skills extraction
# ---------------------------------------------------------------------------

_PREFERRED_SECTION_RE = re.compile(
    r"^(?:preferred|nice[\s\-]to[\s\-]have|bonus|desired|plus|advantageous)"
    r"(?:\s+(?:skills?|qualifications?|requirements?|experience))?",
    re.IGNORECASE,
)

_SECTION_BREAK_RE = re.compile(
    r"^(?:required|must[\s\-]have|responsibilities|duties|about\s+us|benefits|"
    r"compensation|salary|equal\s+opportunity)",
    re.IGNORECASE,
)

_BULLET_RE = re.compile(r"^[\-\*•·▸▹►◆◇➤➢✓✗]\s+")


def _extract_preferred_skills(text, required_skills):
    preferred = []
    required_lower = {s.lower() for s in required_skills}
    lines = text.splitlines()
    in_preferred_section = False

    for line in lines:
        clean = line.strip()
        if not clean:
            continue
        # Strip markdown formatting (**bold**, ## headers, etc.) before testing
        # section headers so "**Preferred Skills**" still matches.
        header_candidate = _strip_markdown(clean)
        if _PREFERRED_SECTION_RE.match(header_candidate):
            in_preferred_section = True
            continue
        if in_preferred_section and _SECTION_BREAK_RE.match(header_candidate):
            in_preferred_section = False
            continue
        if in_preferred_section:
            item = _BULLET_RE.sub("", clean).strip()
            item = _strip_markdown(item)
            if item and item.lower() not in required_lower:
                preferred.append(item)

    inline_matches = re.findall(
        r"preferred(?:\s+skills?)?\s*[:\-]\s*([^.\n]+)",
        text,
        re.IGNORECASE,
    )
    for match in inline_matches:
        for part in re.split(r"[,;]", match):
            skill = part.strip().strip(".")
            if skill and skill.lower() not in required_lower and skill not in preferred:
                preferred.append(skill)

    return preferred


# ---------------------------------------------------------------------------
# Public builder
# ---------------------------------------------------------------------------


def build_jd_json(text):
    required_skills = extract_jd_skills(text)
    experience = extract_experience_requirement(text)
    responsibilities = extract_responsibilities(text)
    job_title = _extract_job_title(text)
    preferred_skills = _extract_preferred_skills(text, required_skills)

    return {
        "job_title": job_title,
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "experience_required": experience,
        "responsibilities": responsibilities,
    }
