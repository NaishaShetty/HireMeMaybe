"""JD URL Parser — extracts job description text from a job posting URL.

Strategy:
1. Direct fetch with httpx + BeautifulSoup (fast, no rate limits, works for
   Greenhouse, Lever, Ashby, Indeed, and most public boards).
2. Jina AI Reader fallback (https://r.jina.ai/{url}) — renders JS-heavy pages
   server-side; works for LinkedIn, Workday, SuccessFactors, etc.
   Free to use, no API key required.

Usage:
    text = extract_jd_from_url("https://boards.greenhouse.io/company/jobs/12345")
"""

from __future__ import annotations

import logging
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

_REQUEST_TIMEOUT = 15  # seconds
_JINA_BASE = "https://r.jina.ai/"

# Tags that typically contain the main JD body on common job boards
_CONTENT_SELECTORS = [
    # Generic semantic HTML
    "article", "main",
    # Common job board classes / IDs (BeautifulSoup CSS selectors)
    "[class*='job-description']", "[class*='jobDescription']",
    "[class*='job_description']", "[class*='description']",
    "[id*='job-description']", "[id*='jobDescription']",
    # Greenhouse
    ".job-post-description",
    # Lever
    ".posting-description",
    # Ashby
    "[class*='ashby']",
    # Indeed
    "#jobDescriptionText",
    # Workday
    "[data-automation-id='jobPostingDescription']",
]

_MIN_TEXT_LENGTH = 200  # below this, the extraction is considered a failure


class JDURLParserError(RuntimeError):
    pass


def extract_jd_from_url(url: str) -> str:
    """Return the raw JD text from *url*.

    Raises JDURLParserError if both strategies fail.
    """
    _validate_url(url)

    # Strategy 1: direct fetch
    try:
        text = _fetch_direct(url)
        if text and len(text.strip()) >= _MIN_TEXT_LENGTH:
            logger.info("JD URL parser: direct fetch succeeded for %s", url)
            return text.strip()
        logger.info("JD URL parser: direct fetch returned thin content (%d chars), trying Jina", len(text or ""))
    except Exception as exc:
        logger.info("JD URL parser: direct fetch failed (%s), trying Jina", exc)

    # Strategy 2: Jina AI Reader
    try:
        text = _fetch_jina(url)
        if text and len(text.strip()) >= _MIN_TEXT_LENGTH:
            logger.info("JD URL parser: Jina fetch succeeded for %s", url)
            return text.strip()
        raise JDURLParserError("Jina returned thin content — page may require login")
    except JDURLParserError:
        raise
    except Exception as exc:
        raise JDURLParserError(
            f"Could not extract job description from {url}. "
            f"The page may require login or block automated access. "
            f"Try uploading a screenshot instead. (Error: {exc})"
        ) from exc


# ---------------------------------------------------------------------------
# Strategy 1: direct HTTP fetch + BeautifulSoup
# ---------------------------------------------------------------------------

def _fetch_direct(url: str) -> str:
    try:
        import httpx
    except ImportError as exc:
        raise ImportError("httpx not installed. Run: pip install httpx") from exc

    try:
        from bs4 import BeautifulSoup
    except ImportError as exc:
        raise ImportError("beautifulsoup4 not installed. Run: pip install beautifulsoup4") from exc

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    resp = httpx.get(url, headers=headers, timeout=_REQUEST_TIMEOUT, follow_redirects=True)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove noise elements
    for tag in soup(["script", "style", "nav", "header", "footer", "aside",
                     "form", "iframe", "noscript"]):
        tag.decompose()

    # Try targeted selectors first
    for selector in _CONTENT_SELECTORS:
        try:
            el = soup.select_one(selector)
            if el:
                text = el.get_text(separator="\n", strip=True)
                if len(text) >= _MIN_TEXT_LENGTH:
                    return _clean_text(text)
        except Exception:
            continue

    # Fallback: body text
    body = soup.find("body")
    if body:
        return _clean_text(body.get_text(separator="\n", strip=True))

    return _clean_text(soup.get_text(separator="\n", strip=True))


# ---------------------------------------------------------------------------
# Strategy 2: Jina AI Reader
# ---------------------------------------------------------------------------

def _fetch_jina(url: str) -> str:
    try:
        import httpx
    except ImportError as exc:
        raise ImportError("httpx not installed. Run: pip install httpx") from exc

    jina_url = f"{_JINA_BASE}{url}"
    headers = {
        "Accept": "text/plain",
        "User-Agent": "HireMeMaybe/1.0",
    }

    resp = httpx.get(jina_url, headers=headers, timeout=_REQUEST_TIMEOUT + 15, follow_redirects=True)
    resp.raise_for_status()
    return _clean_text(resp.text)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _validate_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise JDURLParserError(f"Invalid URL scheme '{parsed.scheme}'. Only http/https are supported.")
    if not parsed.netloc:
        raise JDURLParserError("Invalid URL — no hostname found.")


def _clean_text(text: str) -> str:
    """Collapse excessive blank lines and strip leading/trailing whitespace."""
    # Collapse 3+ consecutive newlines to 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Collapse long runs of spaces/tabs within a line
    text = re.sub(r"[ \t]{3,}", "  ", text)
    return text.strip()
