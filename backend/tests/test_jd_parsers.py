"""Tests for JD parsers: jd_requirements_parser, jd_section_parser, jd_skill_parser."""

import pytest

from app.parsers.jd_requirements_parser import extract_experience_requirement
from app.parsers.jd_section_parser import extract_responsibilities
from app.parsers.jd_skill_parser import extract_jd_skills


# ---------------------------------------------------------------------------
# extract_experience_requirement
# ---------------------------------------------------------------------------

class TestExtractExperienceRequirement:
    def test_simple_years(self):
        result = extract_experience_requirement("We need 5 years of experience.")
        assert result is not None
        assert "5" in result

    def test_plus_notation(self):
        result = extract_experience_requirement("3+ years of experience required.")
        assert result is not None
        assert "3" in result

    def test_range_notation(self):
        result = extract_experience_requirement("4-6 years of experience preferred.")
        assert result is not None
        assert "4" in result

    def test_years_of_experience_phrase(self):
        result = extract_experience_requirement("Minimum 7+ years of experience with Python.")
        assert result is not None
        assert "7" in result

    def test_no_experience_mentioned(self):
        assert extract_experience_requirement("Great company, great culture.") is None

    def test_case_insensitive(self):
        result = extract_experience_requirement("2 YEARS of experience in cloud.")
        assert result is not None


# ---------------------------------------------------------------------------
# extract_responsibilities
# ---------------------------------------------------------------------------

class TestExtractResponsibilities:
    def test_basic_responsibilities(self):
        text = (
            "Responsibilities\n"
            "- Design backend systems\n"
            "- Write unit tests\n"
            "Requirements\n"
            "- Python experience\n"
        )
        result = extract_responsibilities(text)
        assert any("Design backend" in r for r in result)
        assert any("Write unit tests" in r for r in result)

    def test_bullet_with_dot(self):
        text = (
            "Responsibilities\n"
            "• Build REST APIs\n"
            "• Mentor junior developers\n"
        )
        result = extract_responsibilities(text)
        assert any("Build REST APIs" in r for r in result)

    def test_stops_at_requirements(self):
        text = (
            "Responsibilities\n"
            "- Develop features\n"
            "Requirements\n"
            "- 3 years experience\n"
        )
        result = extract_responsibilities(text)
        assert not any("3 years" in r for r in result)

    def test_no_responsibilities_section(self):
        text = "We are a great company. Join us today."
        result = extract_responsibilities(text)
        assert result == []


# ---------------------------------------------------------------------------
# extract_jd_skills
# ---------------------------------------------------------------------------

class TestExtractJdSkills:
    def test_common_skills_detected(self):
        text = "We require Python, SQL, and experience with Docker."
        skills = extract_jd_skills(text)
        assert "Python" in skills
        assert "SQL" in skills
        assert "Docker" in skills

    def test_case_insensitive(self):
        skills = extract_jd_skills("Must know PYTHON and javascript.")
        assert "Python" in skills
        assert "JavaScript" in skills

    def test_no_skills(self):
        skills = extract_jd_skills("We are looking for a motivated individual.")
        # May return empty or contain generic skills; must not crash
        assert isinstance(skills, list)

    def test_no_duplicates(self):
        text = "Python Python Python SQL SQL"
        skills = extract_jd_skills(text)
        assert len([s for s in skills if s == "Python"]) == 1
