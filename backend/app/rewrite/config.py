"""Configuration for rewrite provider selection and generation settings."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class RewriteSettings:
    """Runtime settings for provider selection and text generation.

    Set REWRITE_PROVIDER=OPENAI (default) to use the OpenAI API.
    Set REWRITE_PROVIDER=LOCAL_MODEL to use a local Hugging Face model.
    """

    provider: str = field(
        default_factory=lambda: os.getenv("REWRITE_PROVIDER", "OPENAI").upper()
    )
    openai_api_key: str | None = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY")
    )
    openai_model: str = field(
        default_factory=lambda: os.getenv("REWRITE_OPENAI_MODEL", "gpt-4o-mini")
    )
    openai_max_tokens: int = field(
        default_factory=lambda: _env_int("REWRITE_OPENAI_MAX_TOKENS", 2000)
    )
    temperature: float = field(
        default_factory=lambda: _env_float("REWRITE_TEMPERATURE", 0.3)
    )
    top_p: float = field(
        default_factory=lambda: _env_float("REWRITE_TOP_P", 0.9)
    )
    local_model_name: str = field(
        default_factory=lambda: os.getenv(
            "REWRITE_LOCAL_MODEL", "Qwen/Qwen2.5-3B-Instruct"
        )
    )
    fallback_model_name: str = field(
        default_factory=lambda: os.getenv(
            "REWRITE_FALLBACK_MODEL", "microsoft/Phi-3-mini-4k-instruct"
        )
    )
    max_input_tokens: int = field(
        default_factory=lambda: _env_int("REWRITE_MAX_INPUT_TOKENS", 6144)
    )
    max_new_tokens: int = field(
        default_factory=lambda: _env_int("REWRITE_MAX_NEW_TOKENS", 512)
    )
    repetition_penalty: float = field(
        default_factory=lambda: _env_float("REWRITE_REPETITION_PENALTY", 1.08)
    )
    cache_dir: str | None = field(
        default_factory=lambda: os.getenv("REWRITE_MODEL_CACHE_DIR")
    )
    gemini_api_key: str | None = field(
        default_factory=lambda: os.getenv("GEMINI_API_KEY")
    )
    gemini_model: str = field(
        default_factory=lambda: os.getenv("REWRITE_GEMINI_MODEL", "gemini-2.0-flash")
    )
    anthropic_api_key: str | None = field(
        default_factory=lambda: os.getenv("ANTHROPIC_API_KEY")
    )
    anthropic_model: str = field(
        default_factory=lambda: os.getenv("REWRITE_ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
    )
    anthropic_max_tokens: int = field(
        default_factory=lambda: _env_int("REWRITE_ANTHROPIC_MAX_TOKENS", 2000)
    )


def get_rewrite_settings() -> RewriteSettings:
    """Return the active rewrite settings (reads env vars at call time)."""
    return RewriteSettings()
