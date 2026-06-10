import re
from difflib import SequenceMatcher


SECTION_HEADERS = {
    "education": [
        "education",
        "academic background",
        "educational background",
        "academic history",
        "qualifications",
    ],

    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "work history",
        "career history",
        "relevant experience",
    ],

    "projects": [
        "projects",
        "personal projects",
        "academic projects",
        "side projects",
        "portfolio",
        "selected projects",
    ],

    "skills": [
        "skills",
        "technical skills",
        "core skills",
        "key skills",
        "competencies",
        "technologies",
        "tools",
        "expertise",
    ],

    "certifications": [
        "certifications",
        "certificates",
        "licenses",
        "accreditations",
        "credentials",
        "professional certifications",
    ],
}

# Flatten for fuzzy lookup: (canonical_header, section_name)
_ALL_HEADERS: list[tuple[str, str]] = [
    (h, section)
    for section, headers in SECTION_HEADERS.items()
    for h in headers
]

FUZZY_THRESHOLD = 0.80
# Only consider lines short enough to plausibly be a section header
MAX_HEADER_WORDS = 5


def _best_section_match(line: str) -> str | None:
    """Return the section name if *line* fuzzy-matches a known header."""
    if not line or len(line.split()) > MAX_HEADER_WORDS:
        return None

    best_score = 0.0
    best_section = None

    for header, section in _ALL_HEADERS:
        score = SequenceMatcher(None, line, header).ratio()
        if score > best_score:
            best_score = score
            best_section = section

    if best_score >= FUZZY_THRESHOLD:
        return best_section
    return None


def extract_sections(text: str) -> dict[str, str]:

    sections: dict[str, str] = {
        "education": "",
        "experience": "",
        "projects": "",
        "skills": "",
        "certifications": "",
    }

    lines = text.split("\n")
    current_section: str | None = None

    for line in lines:
        clean_line = line.strip().lower()

        # Strip trailing punctuation/colons common in PDF headers
        clean_line = re.sub(r"[:\-–—]+$", "", clean_line).strip()

        found_section = _best_section_match(clean_line)

        if found_section:
            current_section = found_section
            continue

        if current_section:
            sections[current_section] += line + "\n"

    return sections