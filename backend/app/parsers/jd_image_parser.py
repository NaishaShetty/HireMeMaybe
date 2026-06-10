"""JD Image Parser — extracts job description text from a screenshot using vision LLMs.

Supports the same provider chain as the rewrite engine:
  OpenAI (GPT-4o vision) → Gemini (gemini-2.0-flash) → Anthropic (claude-3-5-haiku)

Usage:
    text = extract_jd_from_image(image_bytes, mime_type="image/png")
"""

from __future__ import annotations

import base64
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

logger = logging.getLogger(__name__)

_VISION_PROMPT = (
    "Extract the complete job description text from this image of a job posting. "
    "Include the job title, all requirements, responsibilities, qualifications, "
    "and any other relevant details exactly as written. "
    "Return only the extracted text — no commentary, no markdown fences, no paraphrasing."
)

_SUPPORTED_MIME_TYPES = {"image/png", "image/jpeg", "image/webp", "image/gif"}


class JDImageParserError(RuntimeError):
    pass


def extract_jd_from_image(image_bytes: bytes, mime_type: str = "image/png") -> str:
    """Return raw JD text extracted from *image_bytes* via a vision LLM.

    Tries providers in order: OpenAI → Gemini → Anthropic.
    Raises JDImageParserError if all providers fail or are unconfigured.
    """
    if mime_type not in _SUPPORTED_MIME_TYPES:
        raise JDImageParserError(
            f"Unsupported image type '{mime_type}'. "
            f"Supported: {sorted(_SUPPORTED_MIME_TYPES)}"
        )

    errors: list[str] = []

    # --- OpenAI GPT-4o vision ---
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        try:
            return _extract_openai(image_bytes, mime_type, openai_key)
        except Exception as exc:
            logger.warning("OpenAI vision failed: %s", exc)
            errors.append(f"OpenAI: {exc}")

    # --- Google Gemini vision ---
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        try:
            return _extract_gemini(image_bytes, mime_type, gemini_key)
        except Exception as exc:
            logger.warning("Gemini vision failed: %s", exc)
            errors.append(f"Gemini: {exc}")

    # --- Anthropic Claude vision ---
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        try:
            return _extract_anthropic(image_bytes, mime_type, anthropic_key)
        except Exception as exc:
            logger.warning("Anthropic vision failed: %s", exc)
            errors.append(f"Anthropic: {exc}")

    raise JDImageParserError(
        "All vision providers failed or no API keys configured. "
        + " | ".join(errors)
    )


# ---------------------------------------------------------------------------
# Provider implementations
# ---------------------------------------------------------------------------

def _extract_openai(image_bytes: bytes, mime_type: str, api_key: str) -> str:
    from openai import OpenAI  # type: ignore[import]

    b64 = base64.b64encode(image_bytes).decode("utf-8")
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{b64}"},
                    },
                    {"type": "text", "text": _VISION_PROMPT},
                ],
            }
        ],
        max_tokens=4096,
    )
    text = response.choices[0].message.content or ""
    if not text.strip():
        raise JDImageParserError("OpenAI returned empty response")
    return text.strip()


def _extract_gemini(image_bytes: bytes, mime_type: str, api_key: str) -> str:
    from google import genai  # type: ignore[import]
    from google.genai import types  # type: ignore[import]

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            _VISION_PROMPT,
        ],
    )
    text = response.text or ""
    if not text.strip():
        raise JDImageParserError("Gemini returned empty response")
    return text.strip()


def _extract_anthropic(image_bytes: bytes, mime_type: str, api_key: str) -> str:
    import anthropic  # type: ignore[import]

    b64 = base64.b64encode(image_bytes).decode("utf-8")
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": mime_type,
                            "data": b64,
                        },
                    },
                    {"type": "text", "text": _VISION_PROMPT},
                ],
            }
        ],
    )
    text = response.content[0].text if response.content else ""
    if not text.strip():
        raise JDImageParserError("Anthropic returned empty response")
    return text.strip()
