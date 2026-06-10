"""Extract experience requirements from job description text."""
import re


def extract_experience_requirement(text):
    # Range pattern must come first: "4-6 years [of experience]".
    # A bare `\d+\+?\s+years` would greedily grab only the second number
    # out of a range string, giving "6 years" instead of "4-6 years".
    patterns = [
        r"\d+\s*-\s*\d+\s+years(?:\s+of\s+experience)?",  # "4-6 years [of exp]"
        r"\d+\+?\s+years of experience",                   # "3+ years of experience"
        r"\d+\+?\s+years",                                 # "5 years" / "5+ years"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group()

    return None
