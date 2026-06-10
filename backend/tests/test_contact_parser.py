"""Tests for contact_parser — email and phone extraction."""

import pytest
from app.parsers.contact_parser import extract_email, extract_phone


class TestExtractEmail:
    def test_simple_email(self):
        assert extract_email("Contact me at jane@example.com today.") == "jane@example.com"

    def test_email_with_plus(self):
        assert extract_email("user+tag@mail.co.uk") == "user+tag@mail.co.uk"

    def test_no_email(self):
        assert extract_email("No email here, just text.") is None

    def test_email_first_of_multiple(self):
        assert extract_email("primary@a.com and secondary@b.com") == "primary@a.com"


class TestExtractPhone:
    def test_us_dashes(self):
        result = extract_phone("Call me at 415-555-1234.")
        assert result is not None and "415" in result

    def test_us_with_country_code(self):
        assert extract_phone("+1 (415) 555-1234") is not None

    def test_parentheses_format(self):
        assert extract_phone("(800) 123-4567") is not None

    def test_no_match_for_date_range(self):
        # "2019-2023" must NOT be matched as a phone number
        assert extract_phone("Worked 2019-2023 at Acme.") is None

    def test_no_match_for_year_pair(self):
        assert extract_phone("Graduated 2018, started 2019") is None

    def test_no_match_for_short_number(self):
        assert extract_phone("Code: 123456") is None

    def test_plain_10_digits_without_separator(self):
        # Bare 10-digit strings are intentionally not matched —
        # indistinguishable from order numbers, account IDs, SSNs, etc.
        assert extract_phone("My number is 4155551234.") is None

    def test_10_digits_with_space_separator(self):
        result = extract_phone("Call 415 555 1234 for help.")
        assert result is not None
