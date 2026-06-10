"""Tests for jd_url_parser — URL validation and text cleaning."""

import pytest
from app.parsers.jd_url_parser import _validate_url, _clean_text, JDURLParserError


class TestValidateUrl:
    def test_valid_https(self):
        _validate_url("https://boards.greenhouse.io/company/jobs/123")  # no error

    def test_valid_http(self):
        _validate_url("http://example.com/jobs/456")

    def test_rejects_ftp(self):
        with pytest.raises(JDURLParserError, match="Invalid URL scheme"):
            _validate_url("ftp://files.example.com/job.txt")

    def test_rejects_no_scheme(self):
        with pytest.raises(JDURLParserError):
            _validate_url("example.com/jobs/123")

    def test_rejects_empty(self):
        with pytest.raises(JDURLParserError):
            _validate_url("")


class TestCleanText:
    def test_collapses_blank_lines(self):
        text = "Job Title\n\n\n\n\nResponsibilities"
        result = _clean_text(text)
        assert "\n\n\n" not in result
        assert "Job Title" in result
        assert "Responsibilities" in result

    def test_strips_whitespace(self):
        assert _clean_text("  hello  ").strip() == "hello"

    def test_empty_string(self):
        assert _clean_text("") == ""
