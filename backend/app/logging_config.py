"""
Centralized logging configuration for HireMeMaybe.

Sets up:
- Structured JSON logging via python-json-logger
- Optional Sentry integration (enabled when SENTRY_DSN is set)
- A single call-site: `setup_logging()` called once at startup

Usage
-----
    from app.logging_config import setup_logging
    setup_logging()

Every module still does the standard:
    import logging
    logger = logging.getLogger(__name__)

Log records will automatically be emitted as JSON when this config is active.
"""
from __future__ import annotations

import logging
import os
import sys
from typing import Any

# ---------------------------------------------------------------------------
# JSON formatter (python-json-logger)
# ---------------------------------------------------------------------------
try:
    from pythonjsonlogger import jsonlogger  # type: ignore

    class _AppJsonFormatter(jsonlogger.JsonFormatter):
        """Extends the default JSON formatter with fixed app-level fields."""

        def add_fields(
            self,
            log_record: dict[str, Any],
            record: logging.LogRecord,
            message_dict: dict[str, Any],
        ) -> None:
            super().add_fields(log_record, record, message_dict)
            log_record.setdefault("app", "hirememaybe")
            log_record.setdefault("env", os.getenv("APP_ENV", "development"))
            # Promote severity to a top-level field so log aggregators can filter
            log_record["severity"] = record.levelname

    _JSON_AVAILABLE = True
except ImportError:  # pragma: no cover
    _JSON_AVAILABLE = False


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def setup_logging(level: str | None = None) -> None:
    """Configure root logger.  Call once, at application startup.

    Parameters
    ----------
    level:
        Override log level string (e.g. ``"DEBUG"``).  Falls back to
        ``LOG_LEVEL`` env var, then ``"INFO"``.
    """
    log_level_str = level or os.getenv("LOG_LEVEL", "INFO")
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)

    root = logging.getLogger()

    # Idempotent — don't add duplicate handlers if called twice
    if root.handlers:
        root.setLevel(log_level)
        return

    handler = logging.StreamHandler(sys.stdout)

    if _JSON_AVAILABLE:
        fmt = _AppJsonFormatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
    else:
        # Fallback plain-text format if python-json-logger isn't installed yet
        fmt = logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(name)s - %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )

    handler.setFormatter(fmt)
    root.setLevel(log_level)
    root.addHandler(handler)

    # Quiet down chatty third-party loggers
    for noisy in ("httpx", "urllib3", "httpcore", "hpack"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    _setup_sentry()

    logging.getLogger(__name__).info(
        "Logging initialised",
        extra={"log_level": log_level_str, "json_enabled": _JSON_AVAILABLE},
    )


def _setup_sentry() -> None:
    """Initialise Sentry SDK if SENTRY_DSN is present in the environment."""
    dsn = os.getenv("SENTRY_DSN", "").strip()
    if not dsn:
        logging.getLogger(__name__).debug("SENTRY_DSN not set — Sentry disabled")
        return

    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration
        from sentry_sdk.integrations.starlette import StarletteIntegration

        sentry_logging = LoggingIntegration(
            level=logging.INFO,        # Breadcrumbs from INFO+
            event_level=logging.ERROR, # Send Sentry events for ERROR+
        )

        sentry_sdk.init(
            dsn=dsn,
            integrations=[
                sentry_logging,
                StarletteIntegration(transaction_style="endpoint"),
                FastApiIntegration(transaction_style="endpoint"),
            ],
            environment=os.getenv("APP_ENV", "development"),
            release=os.getenv("APP_VERSION", "unknown"),
            # Don't send PII (IPs, user agents) by default
            send_default_pii=False,
            # Keep traces_sample_rate low in prod; set via env var
            traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
        )
        logging.getLogger(__name__).info("Sentry initialised", extra={"dsn_prefix": dsn[:20] + "…"})
    except ImportError:
        logging.getLogger(__name__).warning(
            "sentry-sdk not installed — pip install 'sentry-sdk[fastapi]' to enable Sentry"
        )
    except Exception as exc:  # noqa: BLE001
        logging.getLogger(__name__).warning("Sentry init failed: %s", exc)
