"""Resume rewrite engine with pluggable provider support.

Providers:
- ``OPENAI``      — OpenAI chat completions API (default; requires OPENAI_API_KEY)
- ``GEMINI``      — Google Gemini API (requires GEMINI_API_KEY)
- ``ANTHROPIC``   — Anthropic Claude API (requires ANTHROPIC_API_KEY)
- ``LOCAL_MODEL`` — Local Hugging Face causal LM (requires GPU / large RAM)

Fallback chain (when OPENAI is primary): OpenAI → Gemini → Anthropic
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from typing import Any

from app.rewrite.config import RewriteSettings, get_rewrite_settings


logger = logging.getLogger(__name__)


def _is_quota_error(exc: Exception) -> bool:
    """Return True if the exception looks like an OpenAI quota / rate-limit error."""
    msg = str(exc).lower()
    return any(kw in msg for kw in ("429", "quota", "rate_limit", "insufficient_quota", "rate limit"))


def _gemini_retry_delay(exc: Exception) -> float | None:
    """Extract the suggested retry delay (seconds) from a Gemini rate-limit error, if present."""
    import re
    msg = str(exc)
    m = re.search(r"retry[_ ](?:in|delay)[^\d]*(\d+(?:\.\d+)?)", msg, re.IGNORECASE)
    if m:
        return float(m.group(1)) + 1.0   # add 1s buffer
    if "429" in msg or "quota" in msg.lower():
        return 20.0   # safe default if no delay specified
    return None


_SYSTEM_PROMPT = (
    "You are a professional ATS resume optimizer. "
    "Follow the user's instructions exactly. "
    "Never invent experience, companies, projects, certifications, or skills. "
    "Return ONLY the rewritten resume text — no commentary, no markdown fences."
)


class RewriteProvider(str, Enum):
    """Supported rewrite providers."""

    LOCAL_MODEL = "LOCAL_MODEL"
    OPENAI = "OPENAI"
    GEMINI = "GEMINI"
    ANTHROPIC = "ANTHROPIC"


class RewriteEngineError(RuntimeError):
    """Raised when a rewrite cannot be produced."""


@dataclass(frozen=True)
class LocalModelBundle:
    """Container for a loaded local model and its tokenizer."""

    model_name: str
    tokenizer: Any
    model: Any
    device: str


class RewriteEngine:
    """Rewrite resumes using a selected provider.

    Defaults to OpenAI when REWRITE_PROVIDER=OPENAI (recommended).
    Falls back to a local Hugging Face model when REWRITE_PROVIDER=LOCAL_MODEL.
    """

    def __init__(self, settings: RewriteSettings | None = None) -> None:
        self.settings = settings or get_rewrite_settings()
        try:
            self.provider = RewriteProvider(self.settings.provider)
        except ValueError as exc:
            raise RewriteEngineError(
                f"Unsupported rewrite provider '{self.settings.provider}'. "
                f"Valid values: {[p.value for p in RewriteProvider]}"
            ) from exc

        self._openai_client: Any = None
        self._gemini_client: Any = None
        self._anthropic_client: Any = None
        self._backend: LocalModelBundle | None = None

        if self.provider is RewriteProvider.OPENAI:
            self._init_openai()
            self._init_gemini(silent=True)      # pre-load fallback; ignore if no key
            self._init_anthropic(silent=True)   # pre-load last-resort fallback
        elif self.provider is RewriteProvider.GEMINI:
            self._init_gemini()
            self._init_anthropic(silent=True)
        elif self.provider is RewriteProvider.ANTHROPIC:
            self._init_anthropic()
        elif self.provider is RewriteProvider.LOCAL_MODEL:
            self._backend = self._get_local_backend(
                self.settings.local_model_name,
                self.settings.fallback_model_name,
                self.settings.cache_dir,
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def rewrite(self, prompt: str) -> str:
        """Generate an optimised resume from *prompt*.

        Fallback chain when OPENAI is primary:
          OpenAI → Gemini (quota errors) → Anthropic (quota errors)
        """

        if self.provider is RewriteProvider.OPENAI:
            try:
                return self._generate_openai(prompt)
            except RewriteEngineError as exc:
                if not _is_quota_error(exc):
                    raise
                # Gemini fallback
                if self._gemini_client is not None:
                    logger.warning("OpenAI quota exceeded — falling back to Gemini: %s", exc)
                    try:
                        return self._generate_gemini(prompt)
                    except RewriteEngineError as gemini_exc:
                        if not _is_quota_error(gemini_exc):
                            raise
                        # Anthropic last-resort fallback
                        if self._anthropic_client is not None:
                            logger.warning("Gemini quota exceeded — falling back to Anthropic: %s", gemini_exc)
                            return self._generate_anthropic(prompt)
                        raise gemini_exc
                # No Gemini, try Anthropic directly
                if self._anthropic_client is not None:
                    logger.warning("OpenAI quota exceeded — falling back to Anthropic: %s", exc)
                    return self._generate_anthropic(prompt)
                raise

        if self.provider is RewriteProvider.GEMINI:
            try:
                return self._generate_gemini(prompt)
            except RewriteEngineError as exc:
                if _is_quota_error(exc) and self._anthropic_client is not None:
                    logger.warning("Gemini quota exceeded — falling back to Anthropic: %s", exc)
                    return self._generate_anthropic(prompt)
                raise

        if self.provider is RewriteProvider.ANTHROPIC:
            return self._generate_anthropic(prompt)

        if self.provider is RewriteProvider.LOCAL_MODEL:
            if self._backend is None:
                raise RewriteEngineError("Local rewrite backend is not initialised.")
            try:
                raw_text = self._generate_local(prompt)
                return self._clean_output(raw_text)
            except Exception as exc:
                raise RewriteEngineError(f"Local rewrite failed: {exc}") from exc

        raise RewriteEngineError(f"Provider '{self.provider.value}' is not available.")

    # ------------------------------------------------------------------
    # OpenAI provider
    # ------------------------------------------------------------------

    def _init_openai(self) -> None:
        """Lazily import and configure the OpenAI client."""
        try:
            from openai import OpenAI  # type: ignore[import]
        except ImportError as exc:
            raise RewriteEngineError(
                "openai package is not installed. Run: pip install openai"
            ) from exc

        api_key = self.settings.openai_api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RewriteEngineError(
                "OPENAI_API_KEY is not set. Add it to your .env file."
            )

        self._openai_client = OpenAI(api_key=api_key)
        logger.info("OpenAI rewrite provider initialised (model: %s)", self.settings.openai_model)

    def _generate_openai(self, prompt: str) -> str:
        """Call the OpenAI chat completions API."""
        if self._openai_client is None:
            raise RewriteEngineError("OpenAI client is not initialised.")

        try:
            response = self._openai_client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.settings.openai_max_tokens,
                temperature=self.settings.temperature,
            )
            raw_text = response.choices[0].message.content or ""
            return self._clean_output(raw_text)
        except Exception as exc:
            raise RewriteEngineError(f"OpenAI rewrite failed: {exc}") from exc

    # ------------------------------------------------------------------
    # Gemini provider
    # ------------------------------------------------------------------

    def _init_gemini(self, *, silent: bool = False) -> None:
        """Lazily import and configure the Gemini client (google-genai SDK)."""
        api_key = self.settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            if silent:
                return
            raise RewriteEngineError(
                "GEMINI_API_KEY is not set. Add it to your .env file."
            )
        try:
            from google import genai  # type: ignore[import]
            self._gemini_client = genai.Client(api_key=api_key)
            self._gemini_model = self.settings.gemini_model
            logger.info("Gemini rewrite provider initialised (model: %s)", self._gemini_model)
        except ImportError as exc:
            if silent:
                logger.warning("google-genai not installed; Gemini fallback unavailable.")
                return
            raise RewriteEngineError(
                "google-genai package is not installed. Run: pip install google-genai"
            ) from exc

    def _generate_gemini(self, prompt: str) -> str:
        """Call the Gemini API with retry on rate-limit errors."""
        import time
        if self._gemini_client is None:
            raise RewriteEngineError("Gemini client is not initialised.")
        from google import genai  # type: ignore[import]
        model = getattr(self, "_gemini_model", self.settings.gemini_model)
        full_prompt = f"{_SYSTEM_PROMPT}\n\n{prompt}"
        last_exc: Exception | None = None
        for attempt in range(3):
            try:
                response = self._gemini_client.models.generate_content(
                    model=model,
                    contents=full_prompt,
                )
                return self._clean_output(response.text)
            except Exception as exc:
                last_exc = exc
                wait = _gemini_retry_delay(exc)
                if wait and attempt < 2:
                    logger.warning("Gemini rate limited — retrying in %.1fs (attempt %d/3)", wait, attempt + 1)
                    time.sleep(wait)
                else:
                    break
        raise RewriteEngineError(f"Gemini rewrite failed: {last_exc}") from last_exc

    # ------------------------------------------------------------------
    # Anthropic provider
    # ------------------------------------------------------------------

    def _init_anthropic(self, *, silent: bool = False) -> None:
        """Lazily import and configure the Anthropic client."""
        api_key = self.settings.anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            if silent:
                return
            raise RewriteEngineError(
                "ANTHROPIC_API_KEY is not set. Add it to your .env file."
            )
        try:
            import anthropic  # type: ignore[import]
            self._anthropic_client = anthropic.Anthropic(api_key=api_key)
            self._anthropic_model = self.settings.anthropic_model
            logger.info("Anthropic rewrite provider initialised (model: %s)", self._anthropic_model)
        except ImportError as exc:
            if silent:
                logger.warning("anthropic package not installed; Anthropic fallback unavailable.")
                return
            raise RewriteEngineError(
                "anthropic package is not installed. Run: pip install anthropic"
            ) from exc

    def _generate_anthropic(self, prompt: str) -> str:
        """Call the Anthropic Messages API."""
        if self._anthropic_client is None:
            raise RewriteEngineError("Anthropic client is not initialised.")
        model = getattr(self, "_anthropic_model", self.settings.anthropic_model)
        try:
            response = self._anthropic_client.messages.create(
                model=model,
                max_tokens=self.settings.anthropic_max_tokens,
                system=_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            raw_text = response.content[0].text if response.content else ""
            return self._clean_output(raw_text)
        except Exception as exc:
            raise RewriteEngineError(f"Anthropic rewrite failed: {exc}") from exc

    # ------------------------------------------------------------------
    # Local model provider
    # ------------------------------------------------------------------

    def _generate_local(self, prompt: str) -> str:
        """Run one local generation pass."""

        import torch  # type: ignore[import]
        from transformers import AutoModelForCausalLM, AutoTokenizer  # type: ignore[import]

        backend = self._backend
        if backend is None:
            raise RewriteEngineError("Local rewrite backend is not initialised.")
        tokenizer = backend.tokenizer
        model = backend.model
        input_device = self._model_input_device(model)

        messages = [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": self._fit_prompt(prompt, tokenizer)},
        ]

        attention_mask = None

        if hasattr(tokenizer, "apply_chat_template"):
            inputs = tokenizer.apply_chat_template(
                messages,
                add_generation_prompt=True,
                return_tensors="pt",
                tokenize=True,
                return_dict=True,
            )
            if isinstance(inputs, dict) or hasattr(inputs, "get"):
                input_ids = inputs["input_ids"].to(input_device)
                attention_mask = inputs.get("attention_mask")
                if attention_mask is not None:
                    attention_mask = attention_mask.to(input_device)
            elif isinstance(inputs, torch.Tensor):
                input_ids = inputs.to(input_device)
            else:
                input_ids = torch.as_tensor(inputs, device=input_device)
        else:
            encoded = tokenizer(
                f"{_SYSTEM_PROMPT}\n\n{self._fit_prompt(prompt, tokenizer)}",
                return_tensors="pt",
                truncation=True,
                max_length=self._max_input_tokens(tokenizer),
            )
            input_ids = encoded.input_ids.to(input_device)
            attention_mask = (
                encoded.attention_mask.to(input_device)
                if hasattr(encoded, "attention_mask") and encoded.attention_mask is not None
                else None
            )

        with torch.inference_mode():
            generation_kwargs: dict[str, Any] = {
                "input_ids": input_ids,
                "max_new_tokens": self.settings.max_new_tokens,
                "do_sample": self.settings.temperature > 0,
                "temperature": self.settings.temperature,
                "top_p": self.settings.top_p,
                "repetition_penalty": self.settings.repetition_penalty,
                "eos_token_id": getattr(tokenizer, "eos_token_id", None),
                "pad_token_id": (
                    getattr(tokenizer, "pad_token_id", None)
                    or getattr(tokenizer, "eos_token_id", None)
                ),
            }
            if attention_mask is not None:
                generation_kwargs["attention_mask"] = attention_mask

            generated_ids = model.generate(**generation_kwargs)

        new_tokens = generated_ids[0][input_ids.shape[-1]:]
        return tokenizer.decode(new_tokens, skip_special_tokens=True)

    def _fit_prompt(self, prompt: str, tokenizer: Any) -> str:
        """Trim prompt to fit the configured context budget."""

        max_input_tokens = self._max_input_tokens(tokenizer)
        tokens = tokenizer.encode(prompt, add_special_tokens=False)
        if len(tokens) <= max_input_tokens:
            return prompt

        head_tokens = int(max_input_tokens * 0.35)
        tail_tokens = max_input_tokens - head_tokens
        clipped = tokens[:head_tokens] + tokens[-tail_tokens:]
        return tokenizer.decode(clipped, skip_special_tokens=True)

    def _max_input_tokens(self, tokenizer: Any) -> int:
        tokenizer_limit = getattr(tokenizer, "model_max_length", None)
        if tokenizer_limit is None:
            return self.settings.max_input_tokens

        try:
            tokenizer_limit_int = int(tokenizer_limit)
        except (TypeError, ValueError):
            tokenizer_limit_int = self.settings.max_input_tokens

        if tokenizer_limit_int <= 0 or tokenizer_limit_int > 100_000:
            tokenizer_limit_int = self.settings.max_input_tokens

        return min(self.settings.max_input_tokens, tokenizer_limit_int)

    # ------------------------------------------------------------------
    # Shared utilities
    # ------------------------------------------------------------------

    def _clean_output(self, text: str) -> str:
        """Strip markdown fences and common model preamble phrases."""

        cleaned = text.strip()
        cleaned = re.sub(r"^```(?:text|markdown|plaintext)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)

        prefixes = (
            "Here is the rewritten resume:",
            "Here is the optimized resume:",
            "Optimized Resume:",
            "Rewritten Resume:",
            "Sure, here's the rewritten resume:",
            "Here's the optimized version:",
        )
        for prefix in prefixes:
            if cleaned.lower().startswith(prefix.lower()):
                cleaned = cleaned[len(prefix):].strip()
                break

        return cleaned.strip()

    # ------------------------------------------------------------------
    # Local model loading helpers (static / cached)
    # ------------------------------------------------------------------

    @staticmethod
    @lru_cache(maxsize=1)
    def _get_local_backend(
        model_name: str,
        fallback_model_name: str,
        cache_dir: str | None,
    ) -> LocalModelBundle:
        """Load and cache the local model bundle once per process."""

        last_error: Exception | None = None
        for candidate in (model_name, fallback_model_name):
            try:
                return RewriteEngine._load_candidate(candidate, cache_dir)
            except Exception as exc:
                last_error = exc
                logger.warning("Failed to load rewrite model '%s': %s", candidate, exc)

        raise RewriteEngineError(
            f"Unable to load any local rewrite model. Last error: {last_error}"
        ) from last_error

    @staticmethod
    def _load_candidate(model_name: str, cache_dir: str | None) -> LocalModelBundle:
        """Load one Hugging Face model candidate."""

        import torch  # type: ignore[import]
        from transformers import AutoModelForCausalLM, AutoTokenizer  # type: ignore[import]

        use_cuda = torch.cuda.is_available()
        dtype = (
            torch.bfloat16
            if use_cuda and torch.cuda.is_bf16_supported()
            else (torch.float16 if use_cuda else torch.float32)
        )

        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            cache_dir=cache_dir,
            trust_remote_code=True,
            use_fast=True,
        )

        if tokenizer.pad_token is None and tokenizer.eos_token is not None:
            tokenizer.pad_token = tokenizer.eos_token

        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            cache_dir=cache_dir,
            dtype=dtype,
            low_cpu_mem_usage=True,
            trust_remote_code=True,
            device_map="auto" if use_cuda else None,
        )

        if not use_cuda:
            model = model.to("cpu")

        model.eval()
        device = "cuda" if use_cuda else "cpu"

        logger.info("Loaded local rewrite model '%s' on %s", model_name, device)
        return LocalModelBundle(
            model_name=model_name,
            tokenizer=tokenizer,
            model=model,
            device=device,
        )

    @staticmethod
    def _model_input_device(model: Any) -> Any:
        """Resolve the device that should receive input tensors."""

        import torch  # type: ignore[import]

        if hasattr(model, "device"):
            try:
                return torch.device(model.device)
            except (TypeError, RuntimeError, ValueError):
                pass

        try:
            return next(model.parameters()).device
        except (StopIteration, AttributeError):
            return torch.device("cuda" if torch.cuda.is_available() else "cpu")
