from app.matcher.skill_matcher import (
    get_matched_skills
)

from app.matcher.missing_skill_detector import (
    get_missing_skills
)


def calculate_skill_match_score(
    matched_skills,
    jd_skills
):

    if len(jd_skills) == 0:

        return 0

    score = (
        len(matched_skills)
        / len(jd_skills)
    ) * 100

    return round(score, 2)


def match_resume_to_jd(
    resume,
    jd
):

    resume_skills = resume.get(
        "skills",
        []
    )

    jd_skills = jd.get(
        "required_skills",
        []
    )

    matched_skills = (
        get_matched_skills(
            resume_skills,
            jd_skills
        )
    )

    missing_skills = (
        get_missing_skills(
            resume_skills,
            jd_skills
        )
    )

    score = (
        calculate_skill_match_score(
            matched_skills,
            jd_skills
        )
    )

    return {

        "skill_match_score": score,

        "matched_skills": matched_skills,

        "missing_skills": missing_skills
    }