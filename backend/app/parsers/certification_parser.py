import re


MONTH_PATTERN = (
    r"(Jan|Feb|Mar|Apr|May|Jun|Jul|July|"
    r"Aug|Sep|Sept|Oct|Nov|Dec)"
)


def parse_certifications_section(text):

    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]

    certifications = []

    i = 0

    while i < len(lines):

        cert_name = lines[i]

        cert = {
            "name": cert_name,
            "date": None
        }

        if i + 1 < len(lines):

            next_line = lines[i + 1]

            if re.search(MONTH_PATTERN, next_line):

                cert["date"] = next_line
                i += 1

        certifications.append(cert)

        i += 1

    return certifications