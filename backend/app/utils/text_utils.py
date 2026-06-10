"""Text utility helpers."""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Prompt injection mitigation
# ---------------------------------------------------------------------------

# Patterns that indicate an attempt to override LLM system instructions.
_INJECTION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior|above|earlier)\s+(instructions?|prompts?|context)", re.IGNORECASE),
    re.compile(r"forget\s+(everything|all|previous|prior)", re.IGNORECASE),
    re.compile(r"(new|your\s+new|updated)\s+instructions?\s*:", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+a", re.IGNORECASE),
    re.compile(r"act\s+as\s+(if\s+you\s+are|a\s+)", re.IGNORECASE),
    re.compile(r"system\s*:\s+", re.IGNORECASE),
    re.compile(r"<\|?(system|im_start|im_end|endoftext)\|?>", re.IGNORECASE),
    re.compile(r"\[INST\]|\[/INST\]|<<SYS>>|<</SYS>>"),
    re.compile(r"###\s*(system|instruction|prompt)", re.IGNORECASE),
    re.compile(r"disregard\s+(your\s+)?(previous|prior|all)\s+(instructions?|training)", re.IGNORECASE),
    re.compile(r"jailbreak", re.IGNORECASE),
    re.compile(r"do\s+anything\s+now", re.IGNORECASE),  # DAN
]

_MAX_TEXT_LENGTH = 50_000  # hard cap on characters sent to any LLM prompt


def sanitize_for_prompt(text: str) -> str:
    """Strip prompt-injection attempts from user-supplied text.

    - Removes lines that contain known injection patterns.
    - Truncates to *_MAX_TEXT_LENGTH* characters.
    - Strips null bytes and control characters that could confuse parsers.

    Returns the sanitized string.  Logs a warning when injections are detected.
    """
    import logging
    logger = logging.getLogger(__name__)

    # Remove null bytes and most control chars (keep newline, tab, carriage return)
    cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

    lines = cleaned.splitlines()
    safe_lines: list[str] = []
    injection_count = 0

    for line in lines:
        if any(pat.search(line) for pat in _INJECTION_PATTERNS):
            injection_count += 1
            # Replace with a neutral placeholder rather than dropping entirely
            # so the resume structure isn't corrupted.
            safe_lines.append("[content removed]")
        else:
            safe_lines.append(line)

    if injection_count:
        logger.warning(
            "sanitize_for_prompt: removed %d line(s) containing injection patterns",
            injection_count,
        )

    result = "\n".join(safe_lines)

    # Enforce hard length cap
    if len(result) > _MAX_TEXT_LENGTH:
        logger.warning(
            "sanitize_for_prompt: text truncated from %d to %d characters",
            len(result),
            _MAX_TEXT_LENGTH,
        )
        result = result[:_MAX_TEXT_LENGTH]

    return result
