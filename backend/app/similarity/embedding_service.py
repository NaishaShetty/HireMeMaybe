"""Embedding service with optional Redis cache.

Cache key: SHA-256 of the input text.
Falls back to direct encoding if Redis is unavailable (no config required).
"""

from __future__ import annotations

import hashlib
import os
import logging

import numpy as np

from app.similarity.model_loader import get_model

logger = logging.getLogger(__name__)

# ── Redis client (optional) ───────────────────────────────────────────────────

_redis_client = None


def _get_redis():
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    redis_url = os.getenv("REDIS_URL", "")
    if not redis_url:
        return None
    try:
        import redis  # type: ignore
        _redis_client = redis.from_url(redis_url, socket_connect_timeout=1)
        _redis_client.ping()
        logger.info("Redis embedding cache connected: %s", redis_url)
    except Exception as exc:
        logger.warning("Redis unavailable, skipping cache: %s", exc)
        _redis_client = None
    return _redis_client


# ── Cache helpers ─────────────────────────────────────────────────────────────

CACHE_PREFIX = "hmm:emb:"
CACHE_TTL = 60 * 60 * 24  # 24 hours


def _cache_key(text: str) -> str:
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return CACHE_PREFIX + digest


def _load_from_cache(key: str) -> np.ndarray | None:
    r = _get_redis()
    if r is None:
        return None
    try:
        data = r.get(key)
        if data is not None:
            return np.frombuffer(data, dtype=np.float32)
    except Exception as exc:
        logger.debug("Redis cache read error: %s", exc)
    return None


def _save_to_cache(key: str, embedding: np.ndarray) -> None:
    r = _get_redis()
    if r is None:
        return
    try:
        r.setex(key, CACHE_TTL, embedding.astype(np.float32).tobytes())
    except Exception as exc:
        logger.debug("Redis cache write error: %s", exc)


# ── Public API ────────────────────────────────────────────────────────────────

def generate_embedding(text: str) -> np.ndarray:
    key = _cache_key(text)

    cached = _load_from_cache(key)
    if cached is not None:
        return cached

    model = get_model()
    embedding = model.encode(text, convert_to_numpy=True)

    _save_to_cache(key, embedding)
    return embedding