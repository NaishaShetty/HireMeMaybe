from app.parsers.jd_skill_parser import (
    extract_jd_skills
)

from app.parsers.jd_requirements_parser import (
    extract_experience_requirement
)

from app.parsers.jd_section_parser import (
    extract_responsibilities
)


def build_jd_json(text):

    skills = extract_jd_skills(text)

    experience = (
        extract_experience_requirement(text)
    )

    responsibilities = (
        extract_responsibilities(text)
    )

    return {

        "job_title": None,

        "required_skills": skills,

        "preferred_skills": [],

        "experience_required": experience,

        "responsibilities": responsibilities
    }