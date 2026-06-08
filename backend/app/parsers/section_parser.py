import re


SECTION_HEADERS = {
    "education": [
        "education",
        "academic background"
    ],

    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment history"
    ],

    "projects": [
        "projects",
        "personal projects",
        "academic projects"
    ],

    "skills": [
        "skills",
        "technical skills",
        "core skills"
    ],

    "certifications": [
        "certifications",
        "certificates",
        "licenses"
    ]
}


def extract_sections(text):

    sections = {
        "education": "",
        "experience": "",
        "projects": "",
        "skills": "",
        "certifications": ""
    }

    lines = text.split("\n")

    current_section = None

    for line in lines:

        clean_line = line.strip().lower()

        found_section = None

        for section_name, headers in SECTION_HEADERS.items():

            if clean_line in headers:
                found_section = section_name
                break

        if found_section:
            current_section = found_section
            continue

        if current_section:
            sections[current_section] += line + "\n"

    return sections