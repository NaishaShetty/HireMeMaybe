from app.ats.keyword_scorer import calculate_keyword_score
from app.ats.section_scorer import calculate_section_score
from app.ats.formatting_scorer import calculate_formatting_score
from app.ats.experience_scorer import calculate_experience_score
from app.ats.project_scorer import calculate_project_score
from app.ats.certification_scorer import calculate_certification_score


def calculate_ats_score(resume, jd, match_result):
    keyword_score = calculate_keyword_score(match_result["skill_match_score"])
    experience_score = calculate_experience_score(resume, jd)
    project_score = calculate_project_score(resume, jd)
    certification_score = calculate_certification_score(resume)
    section_score = calculate_section_score(resume)
    formatting_score = calculate_formatting_score(resume)

    ats_score = (
        keyword_score * 0.25
        + experience_score * 0.20
        + project_score * 0.15
        + certification_score * 0.10
        + section_score * 0.20
        + formatting_score * 0.10
    )

    return round(ats_score, 2)
