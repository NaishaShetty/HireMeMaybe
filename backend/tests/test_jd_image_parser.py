"""Tests for jd_image_parser — validation logic (no live API calls)."""

import pytest
from app.parsers.jd_image_parser import JDImageParserError, extract_jd_from_image


class TestImageParserValidation:
    def test_unsupported_mime_type_raises(self):
        with pytest.raises(JDImageParserError, match="Unsupported image type"):
            extract_jd_from_image(b"fake", mime_type="application/pdf")

    def test_no_keys_raises_parser_error(self, monkeypatch):
        # Patch env so no API keys are present
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        with pytest.raises(JDImageParserError, match="All vision providers failed"):
            extract_jd_from_image(b"\x89PNG\r\n", mime_type="image/png")
