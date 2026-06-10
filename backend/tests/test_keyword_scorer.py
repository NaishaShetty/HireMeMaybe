"""Tests for the ATS keyword scorer including stuffing detection."""

import pytest
from app.ats.keyword_scorer import calculate_keyword_score


class TestKeywordScore:
    def test_passthrough_no_stuffing(self):
        # When resume skills ≈ JD skills, score passes through unchanged
        score = calculate_keyword_score(80.0, resume_skill_count=10, jd_skill_count=8)
        assert score == 80.0

    def test_no_penalty_below_threshold(self):
        # 3× ratio is the threshold — exactly at boundary, no penalty
        score = calculate_keyword_score(70.0, resume_skill_count=30, jd_skill_count=10)
        assert score == 70.0

    def test_stuffing_penalty_applied(self):
        # 60 skills vs 10 required = 6× ratio → well above threshold → penalised
        score = calculate_keyword_score(90.0, resume_skill_count=60, jd_skill_count=10)
        assert score < 90.0

    def test_stuffing_does_not_go_negative(self):
        score = calculate_keyword_score(5.0, resume_skill_count=1000, jd_skill_count=5)
        assert score >= 0.0

    def test_zero_jd_skills_no_crash(self):
        # Edge case: no JD skills — no penalty, score returned as-is
        score = calculate_keyword_score(50.0, resume_skill_count=20, jd_skill_count=0)
        assert score == 50.0

    def test_score_clamped_at_100(self):
        score = calculate_keyword_score(110.0, resume_skill_count=5, jd_skill_count=10)
        assert score == 100.0
