"""Composite ATS score from all sub-scorers."""
from __future__ import annotations

from app.ats.keyword_scorer import calculate_keyword_score
from app.ats.section_scorer import calculate_section_score
from app.ats.formatting_scorer import calculate_formatting_score
from app.ats.experience_scorer import calculate_experience_score
from app.ats.project_scorer import calculate_project_score
from app.ats.certification_scorer import calculate_certification_score


def calculate_ats_score(resume: dict, jd: dict, match_result: dict) -> float:
    """Return a 0-100 ATS score by combining sub-scorer results.

    Weights:
      keyword      25 %  (skill match, stuffing-penalised)
      section      20 %  (presence of key resume sections)
      experience   20 %  (skill mentions in work history)
      project      15 %  (skill mentions in project descriptions)
      formatting   10 %  (contact info, bullet structure)
      certification 10 % (number of certs on record)
    """
    resume_skill_count = len(resume.get("skills", []))
    jd_skill_count = len(jd.get("required_skills", []))

    keyword_score = calculate_keyword_score(
        match_result["skill_match_score"],
        resume_skill_count=resume_skill_count,
        jd_skill_count=jd_skill_count,
    )
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

    return round(min(100.0, max(0.0, ats_score)), 2)
