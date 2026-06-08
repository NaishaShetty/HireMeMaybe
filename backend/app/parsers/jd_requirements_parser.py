import re


def extract_experience_requirement(text):

    patterns = [

        r"\d+\+?\s+years",

        r"\d+\s*-\s*\d+\s+years",

        r"\d+\+?\s+years of experience"

    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            return match.group()

    return None