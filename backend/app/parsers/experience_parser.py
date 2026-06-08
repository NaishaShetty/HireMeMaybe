import re


MONTH_PATTERN = (
    r"(Jan|Feb|Mar|Apr|May|Jun|Jul|July|"
    r"Aug|Sep|Sept|Oct|Nov|Dec)"
)

YEAR_RANGE_PATTERN = r"\d{4}\s*[–-]\s*(\d{4}|Present)"

FULL_DATE_PATTERN = MONTH_PATTERN + r".*"


def is_date_line(text):

    return (
        bool(re.search(FULL_DATE_PATTERN, text))
        or bool(re.search(YEAR_RANGE_PATTERN, text))
    )


def parse_experience_section(text):

    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]

    experiences = []

    i = 0

    while i < len(lines) - 2:

        role = lines[i]

        date_line = lines[i + 1]

        company = lines[i + 2]

        if is_date_line(date_line):

            experience = {
                "role": role,
                "company": company,
                "dates": date_line,
                "description": []
            }

            i += 3

            while i < len(lines):

                current = lines[i]

                if (
                    i + 1 < len(lines)
                    and is_date_line(lines[i + 1])
                ):
                    break

                if current.startswith("•"):
                    experience["description"].append(current)

                i += 1

            experiences.append(experience)

        else:
            i += 1

    return experiences