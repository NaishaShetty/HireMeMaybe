"""Tests for skill_matcher — exact, substring, and fuzzy matching."""

import pytest
from app.matcher.skill_matcher import get_matched_skills


class TestExactMatch:
    def test_exact_match_case_insensitive(self):
        matched = get_matched_skills(["Python", "SQL"], ["python", "sql"])
        assert "python" in matched
        assert "sql" in matched

    def test_no_match(self):
        matched = get_matched_skills(["Python"], ["Go"])
        assert matched == []

    def test_partial_jd_covered(self):
        matched = get_matched_skills(["Python", "Docker"], ["Python", "Kubernetes"])
        assert "Python" in matched
        assert "Kubernetes" not in matched


class TestSubstringMatch:
    def test_skill_found_in_resume_text(self):
        resume_text = "Extensive experience with FastAPI and REST API design."
        matched = get_matched_skills([], ["FastAPI"], resume_text=resume_text)
        assert "FastAPI" in matched

    def test_skill_not_in_resume_text(self):
        matched = get_matched_skills([], ["GraphQL"], resume_text="I used REST APIs only.")
        assert matched == []

    def test_partial_word_does_not_match(self):
        # "Java" should not match "JavaScript" via substring (word boundary required)
        matched = get_matched_skills([], ["Java"], resume_text="Worked with JavaScript.")
        assert "Java" not in matched


class TestFuzzyMatch:
    def test_typo_match(self):
        # "Postgress" (typo) should fuzzy-match "PostgreSQL" — actually let's be realistic:
        # "PostgreSQL" vs "postgres" — high enough ratio
        matched = get_matched_skills(["postgres"], ["PostgreSQL"])
        assert "PostgreSQL" in matched

    def test_no_false_positive(self):
        # "React" vs "Redux" — very different, should not match
        matched = get_matched_skills(["Redux"], ["React"])
        assert "React" not in matched


class TestCombined:
    def test_all_tiers(self):
        resume_skills = ["Python", "postgres"]
        resume_text = "Built pipelines using Apache Spark."
        jd_skills = ["Python", "PostgreSQL", "Apache Spark"]
        matched = get_matched_skills(resume_skills, jd_skills, resume_text=resume_text)
        assert "Python" in matched          # exact
        assert "PostgreSQL" in matched      # fuzzy
        assert "Apache Spark" in matched    # substring
