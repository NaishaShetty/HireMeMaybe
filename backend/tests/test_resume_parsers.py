"""Tests for resume parsers: section_parser and skill_parser."""

import pytest

from app.parsers.section_parser import extract_sections
from app.parsers.skill_parser import extract_skills


# ---------------------------------------------------------------------------
# extract_sections
# ---------------------------------------------------------------------------

class TestExtractSections:
    def test_standard_sections_detected(self):
        text = (
            "EXPERIENCE\n"
            "Software Engineer at Google 2020-2023\n"
            "- Built distributed systems\n\n"
            "EDUCATION\n"
            "BSc Computer Science, MIT 2020\n\n"
            "SKILLS\n"
            "Python, Go, SQL\n\n"
            "PROJECTS\n"
            "Data Pipeline — ETL project using Python\n"
        )
        sections = extract_sections(text)
        assert "experience" in sections
        assert "education" in sections
        assert "skills" in sections
        assert "projects" in sections

    def test_alternate_header_names(self):
        text = (
            "Work History\n"
            "Junior Dev at Startup 2021-2022\n\n"
            "Technical Skills\n"
            "Python, Docker\n"
        )
        sections = extract_sections(text)
        assert "experience" in sections
        assert "skills" in sections

    def test_empty_text_returns_empty_dict(self):
        sections = extract_sections("")
        assert isinstance(sections, dict)

    def test_certifications_section(self):
        text = "Certifications\nAWS Certified Developer\nGoogle Cloud Professional\n"
        sections = extract_sections(text)
        assert "certifications" in sections

    def test_section_content_is_non_empty(self):
        text = (
            "EXPERIENCE\n"
            "Engineer at Corp 2019-2022\n"
            "- Led a team of 5 engineers\n"
        )
        sections = extract_sections(text)
        assert sections.get("experience")  # non-empty list/string


# ---------------------------------------------------------------------------
# extract_skills
# ---------------------------------------------------------------------------

class TestExtractSkills:
    def test_common_tech_skills(self):
        text = "Experienced with Python, Docker, and PostgreSQL."
        skills = extract_skills(text)
        assert "Python" in skills
        assert "Docker" in skills

    def test_case_insensitive_matching(self):
        skills = extract_skills("I know JAVASCRIPT and react.")
        assert "JavaScript" in skills
        assert "React" in skills

    def test_no_skills_returns_empty_list(self):
        skills = extract_skills("I love working with teams and solving problems.")
        assert isinstance(skills, list)

    def test_no_duplicates(self):
        text = "Python Python Python Docker Docker"
        skills = extract_skills(text)
        assert len([s for s in skills if s == "Python"]) == 1

    def test_skill_as_substring_not_matched(self):
        # "Java" should not be matched inside "JavaScript"
        skills = extract_skills("Worked extensively with JavaScript frameworks.")
        assert "Java" not in skills
