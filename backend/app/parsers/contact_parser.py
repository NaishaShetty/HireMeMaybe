"""Contact information extractors for resume text."""

import re


def extract_email(text: str):
    match = re.search(
        r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}",
        text,
    )
    return match.group() if match else None


# Phone: requires exactly 10 digits in NXX-NXX-XXXX style formats
# (NXX) NXX-XXXX | NXX-NXX-XXXX | NXX NXX XXXX | NNNNNNNNNN
# Optional country code prefix: +1, +44, etc.
_PHONE_RE = re.compile(
    r"(?<!\d)"
    r"(?:\+\d{1,3}[\s\-.]?)?"
    r"(?:"
        r"\(\d{3}\)[\s\-.]?"
        r"|\d{3}[\s\-.]"
    r")"
    r"\d{3}"
    r"[\s\-.]?"
    r"\d{4}"
    r"(?!\d)"
)


def extract_phone(text: str):
    """Extract the first phone number from text.

    Strict enough to avoid matching date ranges like 2019-2023.
    """
    match = _PHONE_RE.search(text)
    return match.group().strip() if match else None
