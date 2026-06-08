from app.parsers.experience_parser import (
    parse_experience_section
)

from app.parsers.project_parser import (
    parse_projects_section
)

from app.parsers.certification_parser import (
    parse_certifications_section
)


def build_resume_json(
    email,
    phone,
    skills,
    sections
):

    resume = {
        "email": email,
        "phone": phone,
        "skills": skills,
        "education": [],
        "experience": [],
        "projects": [],
        "certifications": []
    }

    education_lines = [
        line.strip()
        for line in sections["education"].split("\n")
        if line.strip()
    ]

    for line in education_lines:

        resume["education"].append({
            "institution": line
        })

    resume["experience"] = (
        parse_experience_section(
            sections["experience"]
        )
    )

    resume["projects"] = (
        parse_projects_section(
            sections["projects"]
        )
    )

    resume["certifications"] = (
        parse_certifications_section(
            sections["certifications"]
        )
    )

    return resume