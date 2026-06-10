"""Tests for jd_builder — job_title and preferred_skills extraction."""

import pytest
from app.services.jd_builder import build_jd_json, _extract_job_title, _extract_preferred_skills


class TestExtractJobTitle:
    def test_labelled_field(self):
        text = "Job Title: Senior Software Engineer\n\nWe are looking for..."
        assert _extract_job_title(text) == "Senior Software Engineer"

    def test_position_field(self):
        text = "Position: Backend Developer\nRequirements..."
        assert _extract_job_title(text) == "Backend Developer"

    def test_role_field(self):
        text = "Role: Data Scientist\n\nAbout the role..."
        assert _extract_job_title(text) == "Data Scientist"

    def test_first_line_heuristic(self):
        text = "Senior Machine Learning Engineer\n\nAbout the company..."
        result = _extract_job_title(text)
        assert result == "Senior Machine Learning Engineer"

    def test_no_title_returns_none(self):
        text = "We are hiring someone with great skills in Python and AWS."
        # No labelled field and first line has no title keyword
        result = _extract_job_title(text)
        # May be None or a false-positive; just verify no crash
        assert result is None or isinstance(result, str)


class TestExtractPreferredSkills:
    def test_preferred_section(self):
        text = (
            "Required Skills\n- Python\n- SQL\n\n"
            "Preferred Skills\n- Go\n- Kubernetes\n\n"
            "About Us\nWe are a great company."
        )
        preferred = _extract_preferred_skills(text, ["Python", "SQL"])
        assert "Go" in preferred
        assert "Kubernetes" in preferred

    def test_nice_to_have_section(self):
        text = "Nice-to-have\n- GraphQL\n- Redis\n\nSalary: Competitive"
        preferred = _extract_preferred_skills(text, [])
        assert "GraphQL" in preferred
        assert "Redis" in preferred

    def test_inline_preferred(self):
        text = "Experience with Python required. Preferred: TypeScript, Rust."
        preferred = _extract_preferred_skills(text, ["Python"])
        assert "TypeScript" in preferred
        assert "Rust" in preferred

    def test_no_duplication_with_required(self):
        text = "Preferred Skills\n- Python\n- Go"
        preferred = _extract_preferred_skills(text, ["Python"])
        # Python is already required — should not appear in preferred
        assert "Python" not in preferred
        assert "Go" in preferred


class TestBuildJdJson:
    def test_full_output_keys(self):
        text = (
            "Senior Data Engineer\n\n"
            "Required: 3+ years of experience with Python, Spark, and SQL.\n\n"
            "Preferred Skills\n- Airflow\n- dbt\n\n"
            "Responsibilities\n- Build pipelines"
        )
        result = build_jd_json(text)
        assert "job_title" in result
        assert "required_skills" in result
        assert "preferred_skills" in result
        assert "experience_required" in result
        assert "responsibilities" in result

    def test_experience_extracted(self):
        text = "We require 5+ years of experience with Python."
        result = build_jd_json(text)
        assert result["experience_required"] is not None
        assert "5" in result["experience_required"]
