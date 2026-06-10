"""Tests for all ATS sub-scorers and the composite calculate_ats_score."""

import pytest

from app.ats.ats_scorer import calculate_ats_score
from app.ats.certification_scorer import calculate_certification_score
from app.ats.experience_scorer import calculate_experience_score
from app.ats.formatting_scorer import calculate_formatting_score
from app.ats.project_scorer import calculate_project_score
from app.ats.section_scorer import calculate_section_score


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _resume(**overrides):
    base = {
        "email": "jane@example.com",
        "phone": "415-555-1234",
        "skills": ["Python", "SQL", "Docker"],
        "education": [{"institution": "MIT", "degree": "BSc Computer Science"}],
        "experience": [
            {
                "title": "Software Engineer",
                "company": "Acme",
                "description": ["Built Python APIs", "Managed SQL databases"],
            }
        ],
        "projects": [
            {"name": "Data Pipeline", "description": ["Python ETL using Docker"]}
        ],
        "certifications": ["AWS Certified Developer"],
    }
    base.update(overrides)
    return base


def _jd(**overrides):
    base = {"required_skills": ["Python", "SQL", "Docker"]}
    base.update(overrides)
    return base


def _match(skill_match=80.0, matched=None, missing=None):
    return {
        "skill_match_score": skill_match,
        "matched_skills": matched or ["Python", "SQL"],
        "missing_skills": missing or [],
    }


# ---------------------------------------------------------------------------
# section_scorer
# ---------------------------------------------------------------------------

class TestSectionScorer:
    def test_all_sections_present(self):
        r = _resume()
        assert calculate_section_score(r) == 100

    def test_missing_certifications(self):
        r = _resume(certifications=[])
        assert calculate_section_score(r) == 80

    def test_no_sections(self):
        assert calculate_section_score({}) == 0

    def test_partial_sections(self):
        r = {"skills": ["Python"], "experience": [{"title": "Dev"}]}
        score = calculate_section_score(r)
        assert score == 40  # 2 of 5 sections


# ---------------------------------------------------------------------------
# formatting_scorer
# ---------------------------------------------------------------------------

class TestFormattingScorer:
    def test_complete_resume_full_score(self):
        r = _resume()
        assert calculate_formatting_score(r) == 100.0

    def test_missing_email_penalised(self):
        r = _resume(email=None)
        assert calculate_formatting_score(r) < 100.0

    def test_missing_phone_penalised(self):
        r = _resume(phone=None)
        assert calculate_formatting_score(r) < 100.0

    def test_missing_skills_penalised(self):
        r = _resume(skills=[])
        assert calculate_formatting_score(r) < 100.0

    def test_missing_experience_penalised(self):
        r = _resume(experience=[])
        assert calculate_formatting_score(r) < 100.0

    def test_experience_without_bullets_penalised(self):
        r = _resume(experience=[{"title": "Dev", "company": "Co"}])
        assert calculate_formatting_score(r) < 100.0

    def test_empty_resume_returns_zero_or_positive(self):
        score = calculate_formatting_score({})
        assert score >= 0.0

    def test_none_resume_returns_default(self):
        assert calculate_formatting_score(None) == 50.0


# ---------------------------------------------------------------------------
# experience_scorer
# ---------------------------------------------------------------------------

class TestExperienceScorer:
    def test_skills_in_experience_score_positive(self):
        r = _resume()
        score = calculate_experience_score(r, _jd())
        assert score > 0

    def test_no_experience_returns_zero(self):
        r = _resume(experience=[])
        assert calculate_experience_score(r, _jd()) == 0

    def test_score_capped_at_100(self):
        exp = [{"description": ["python sql docker " * 20]} for _ in range(10)]
        r = _resume(experience=exp)
        jd = _jd(required_skills=["python"])
        assert calculate_experience_score(r, jd) <= 100

    def test_no_jd_skills_returns_zero(self):
        r = _resume()
        assert calculate_experience_score(r, {"required_skills": []}) == 0


# ---------------------------------------------------------------------------
# project_scorer
# ---------------------------------------------------------------------------

class TestProjectScorer:
    def test_skills_in_projects_score_positive(self):
        r = _resume()
        score = calculate_project_score(r, _jd())
        assert score > 0

    def test_no_projects_returns_zero(self):
        r = _resume(projects=[])
        assert calculate_project_score(r, _jd()) == 0

    def test_score_capped_at_100(self):
        projects = [{"description": ["python sql docker " * 20]} for _ in range(10)]
        r = _resume(projects=projects)
        assert calculate_project_score(r, _jd()) <= 100

    def test_no_jd_skills_returns_zero(self):
        r = _resume()
        assert calculate_project_score(r, {"required_skills": []}) == 0


# ---------------------------------------------------------------------------
# certification_scorer
# ---------------------------------------------------------------------------

class TestCertificationScorer:
    def test_no_certs_returns_zero(self):
        assert calculate_certification_score({"certifications": []}) == 0

    def test_one_cert_returns_60(self):
        assert calculate_certification_score({"certifications": ["AWS"]}) == 60

    def test_three_certs_returns_80(self):
        r = {"certifications": ["A", "B", "C"]}
        assert calculate_certification_score(r) == 80

    def test_five_or_more_returns_100(self):
        r = {"certifications": ["A", "B", "C", "D", "E"]}
        assert calculate_certification_score(r) == 100

    def test_missing_key_returns_zero(self):
        assert calculate_certification_score({}) == 0


# ---------------------------------------------------------------------------
# composite calculate_ats_score
# ---------------------------------------------------------------------------

class TestCalculateAtsScore:
    def test_returns_float_in_range(self):
        score = calculate_ats_score(_resume(), _jd(), _match())
        assert 0.0 <= score <= 100.0

    def test_strong_resume_scores_higher(self):
        strong = calculate_ats_score(_resume(), _jd(), _match(skill_match=90.0))
        weak = calculate_ats_score(
            _resume(skills=[], experience=[], projects=[], certifications=[]),
            _jd(),
            _match(skill_match=10.0),
        )
        assert strong > weak

    def test_empty_resume_does_not_crash(self):
        score = calculate_ats_score({}, {}, _match(skill_match=0.0))
        assert 0.0 <= score <= 100.0

    def test_score_capped_at_100(self):
        score = calculate_ats_score(_resume(), _jd(), _match(skill_match=100.0))
        assert score <= 100.0
