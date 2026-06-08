import re


MONTH_PATTERN = (
    r"(Jan|Feb|Mar|Apr|May|Jun|Jul|July|"
    r"Aug|Sep|Sept|Oct|Nov|Dec)"
)

YEAR_RANGE_PATTERN = r"\d{4}\s*[–-]\s*\d{4}"

SINGLE_YEAR_PATTERN = r"\d{4}"

FULL_DATE_PATTERN = MONTH_PATTERN + r".*"


def is_date_line(text):

    return (
        bool(re.search(FULL_DATE_PATTERN, text))
        or bool(re.search(YEAR_RANGE_PATTERN, text))
        or bool(re.fullmatch(SINGLE_YEAR_PATTERN, text))
    )


def parse_projects_section(text):

    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]

    projects = []

    i = 0

    while i < len(lines):

        title = lines[i]

        if i + 2 >= len(lines):
            break

        date_line = lines[i + 1]

        if not is_date_line(date_line):
            i += 1
            continue

        links_line = lines[i + 2]

        project = {
            "title": title,
            "date": date_line,
            "links": [],
            "description": []
        }

        if "github" in links_line.lower():
            project["links"].append("GitHub")

        if "live demo" in links_line.lower():
            project["links"].append("Live Demo")

        i += 3

        while i < len(lines):

            current = lines[i]

            if (
                i + 1 < len(lines)
                and is_date_line(lines[i + 1])
            ):
                break

            if current.startswith("•"):
                project["description"].append(current)

            i += 1

        projects.append(project)

    return projects