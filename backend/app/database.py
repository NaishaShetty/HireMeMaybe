"""SQLite persistence layer for HireMeMaybe.

Tables
------
audit_log         — per-request audit trail (latency, IP, status)
users             — user accounts (email, hashed password, plan tier)
sessions          — auth session tokens
analysis_runs     — every resume × JD analysis with all scores
resume_versions   — versioned resume text + metadata per user
job_applications  — user job application tracker

The database file lives at backend/hirememaybe.db by default,
configurable via the DB_PATH environment variable.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import secrets
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator

logger = logging.getLogger(__name__)

_DB_PATH = Path(os.getenv("DB_PATH", Path(__file__).resolve().parent.parent / "hirememaybe.db"))

_SCHEMA = """
-- ── Audit ────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS audit_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ts          REAL    NOT NULL,
    endpoint    TEXT    NOT NULL,
    method      TEXT    NOT NULL DEFAULT 'POST',
    client_ip   TEXT,
    status_code INTEGER,
    latency_ms  REAL,
    error       TEXT
);
CREATE INDEX IF NOT EXISTS idx_audit_ts       ON audit_log (ts);
CREATE INDEX IF NOT EXISTS idx_audit_endpoint ON audit_log (endpoint);

-- ── Users ────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    email         TEXT    NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT    NOT NULL,
    plan          TEXT    NOT NULL DEFAULT 'free',   -- 'free' | 'pro' | 'team'
    display_name  TEXT,
    created_at    REAL    NOT NULL,
    last_login    REAL,
    is_active     INTEGER NOT NULL DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);

-- ── Sessions ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sessions (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token      TEXT    NOT NULL UNIQUE,
    created_at REAL    NOT NULL,
    expires_at REAL    NOT NULL,
    client_ip  TEXT
);
CREATE INDEX IF NOT EXISTS idx_sessions_token   ON sessions (token);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions (user_id);

-- ── Resume versions ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS resume_versions (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER REFERENCES users(id) ON DELETE SET NULL,
    session_id   TEXT,               -- anonymous session fingerprint
    filename     TEXT,
    resume_text  TEXT    NOT NULL,
    parsed_json  TEXT,               -- JSON blob from build_resume_json
    ats_score    REAL,
    label        TEXT,               -- e.g. 'original', 'optimized_v1'
    created_at   REAL    NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_resume_user    ON resume_versions (user_id);
CREATE INDEX IF NOT EXISTS idx_resume_session ON resume_versions (session_id);

-- ── Analysis runs ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS analysis_runs (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER REFERENCES users(id) ON DELETE SET NULL,
    session_id          TEXT,
    resume_version_id   INTEGER REFERENCES resume_versions(id) ON DELETE SET NULL,
    jd_text             TEXT,
    jd_title            TEXT,
    jd_company          TEXT,
    ats_score           REAL,
    semantic_score      REAL,
    skill_match_score   REAL,
    interview_prob      REAL,
    missing_skills      TEXT,        -- JSON array
    matched_skills      TEXT,        -- JSON array
    full_result         TEXT,        -- full JSON response blob
    hallucination_trust REAL,        -- from rewrite if applicable
    created_at          REAL    NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_analysis_user    ON analysis_runs (user_id);
CREATE INDEX IF NOT EXISTS idx_analysis_session ON analysis_runs (session_id);
CREATE INDEX IF NOT EXISTS idx_analysis_ts      ON analysis_runs (created_at);

-- ── Job applications ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS job_applications (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id           INTEGER REFERENCES users(id) ON DELETE SET NULL,
    session_id        TEXT,
    analysis_run_id   INTEGER REFERENCES analysis_runs(id) ON DELETE SET NULL,
    company           TEXT,
    job_title         TEXT,
    job_url           TEXT,
    status            TEXT NOT NULL DEFAULT 'saved',  -- saved|applied|viewed|interview|offer|rejected
    ats_score         REAL,
    match_score       REAL,
    notes             TEXT,
    applied_at        REAL,
    created_at        REAL NOT NULL,
    updated_at        REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_jobs_user   ON job_applications (user_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON job_applications (status);
"""


# ── Connection helper ─────────────────────────────────────────────────────────

@contextmanager
def _get_conn() -> Generator[sqlite3.Connection, None, None]:
    """Yield a WAL-mode SQLite connection."""
    conn = sqlite3.connect(str(_DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ── Schema init ───────────────────────────────────────────────────────────────

def init_db() -> None:
    """Create all tables. Safe to call multiple times (idempotent)."""
    try:
        with _get_conn() as conn:
            conn.executescript(_SCHEMA)
        logger.info("Database initialised at %s", _DB_PATH)
    except Exception as exc:
        logger.error("Database init failed: %s", exc)


# ── Audit log ─────────────────────────────────────────────────────────────────

def log_request(
    *,
    endpoint: str,
    method: str = "POST",
    client_ip: str | None = None,
    status_code: int | None = None,
    latency_ms: float | None = None,
    error: str | None = None,
) -> None:
    """Insert one audit record. Failures are logged but never raised."""
    try:
        with _get_conn() as conn:
            conn.execute(
                "INSERT INTO audit_log (ts, endpoint, method, client_ip, status_code, latency_ms, error)"
                " VALUES (?, ?, ?, ?, ?, ?, ?)",
                (time.time(), endpoint, method, client_ip, status_code, latency_ms, error),
            )
    except Exception as exc:
        logger.warning("audit log insert failed: %s", exc)


# ── User management ───────────────────────────────────────────────────────────

def _hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{digest}"


def _verify_password(password: str, stored: str) -> bool:
    try:
        salt, digest = stored.split(":", 1)
        return hashlib.sha256((salt + password).encode()).hexdigest() == digest
    except Exception:
        return False


def create_user(email: str, password: str, display_name: str | None = None) -> int | None:
    """Insert a new user. Returns the new user id, or None if email already exists."""
    try:
        with _get_conn() as conn:
            cur = conn.execute(
                "INSERT INTO users (email, password_hash, display_name, created_at) VALUES (?,?,?,?)",
                (email.lower().strip(), _hash_password(password), display_name, time.time()),
            )
            return cur.lastrowid
    except sqlite3.IntegrityError:
        return None
    except Exception as exc:
        logger.warning("create_user failed: %s", exc)
        return None


def authenticate_user(email: str, password: str) -> dict | None:
    """Return user row dict on success, None on failure."""
    try:
        with _get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE email=? AND is_active=1",
                (email.lower().strip(),),
            ).fetchone()
        if row and _verify_password(password, row["password_hash"]):
            conn2_dict = dict(row)
            # Update last_login without yielding again
            _update_last_login(row["id"])
            conn2_dict.pop("password_hash", None)
            return conn2_dict
        return None
    except Exception as exc:
        logger.warning("authenticate_user failed: %s", exc)
        return None


def _update_last_login(user_id: int) -> None:
    try:
        with _get_conn() as conn:
            conn.execute("UPDATE users SET last_login=? WHERE id=?", (time.time(), user_id))
    except Exception:
        pass


def get_user_by_id(user_id: int) -> dict | None:
    try:
        with _get_conn() as conn:
            row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
        if row:
            d = dict(row)
            d.pop("password_hash", None)
            return d
        return None
    except Exception:
        return None


# ── Session management ────────────────────────────────────────────────────────

SESSION_TTL_SECONDS = 30 * 24 * 3600  # 30 days


def create_session(user_id: int, client_ip: str | None = None) -> str:
    """Create a session token for *user_id* and return it."""
    token = secrets.token_urlsafe(32)
    now = time.time()
    try:
        with _get_conn() as conn:
            conn.execute(
                "INSERT INTO sessions (user_id, token, created_at, expires_at, client_ip) VALUES (?,?,?,?,?)",
                (user_id, token, now, now + SESSION_TTL_SECONDS, client_ip),
            )
    except Exception as exc:
        logger.warning("create_session failed: %s", exc)
    return token


def validate_session(token: str) -> dict | None:
    """Return user dict if *token* is valid and unexpired, else None."""
    try:
        with _get_conn() as conn:
            row = conn.execute(
                "SELECT s.user_id, s.expires_at FROM sessions s WHERE s.token=?",
                (token,),
            ).fetchone()
        if row and row["expires_at"] > time.time():
            return get_user_by_id(row["user_id"])
        return None
    except Exception:
        return None


def revoke_session(token: str) -> None:
    try:
        with _get_conn() as conn:
            conn.execute("DELETE FROM sessions WHERE token=?", (token,))
    except Exception:
        pass


# ── Resume versions ───────────────────────────────────────────────────────────

def save_resume_version(
    *,
    resume_text: str,
    parsed_json: dict | None = None,
    ats_score: float | None = None,
    filename: str | None = None,
    label: str = "original",
    user_id: int | None = None,
    session_id: str | None = None,
) -> int | None:
    """Persist a resume version. Returns the new row id."""
    try:
        with _get_conn() as conn:
            cur = conn.execute(
                """INSERT INTO resume_versions
                   (user_id, session_id, filename, resume_text, parsed_json, ats_score, label, created_at)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (
                    user_id, session_id, filename, resume_text,
                    json.dumps(parsed_json) if parsed_json else None,
                    ats_score, label, time.time(),
                ),
            )
            return cur.lastrowid
    except Exception as exc:
        logger.warning("save_resume_version failed: %s", exc)
        return None


def get_resume_versions(
    user_id: int | None = None,
    session_id: str | None = None,
    limit: int = 20,
) -> list[dict]:
    """Return the most recent *limit* resume versions for a user or session."""
    try:
        with _get_conn() as conn:
            if user_id:
                rows = conn.execute(
                    "SELECT * FROM resume_versions WHERE user_id=? ORDER BY created_at DESC LIMIT ?",
                    (user_id, limit),
                ).fetchall()
            elif session_id:
                rows = conn.execute(
                    "SELECT * FROM resume_versions WHERE session_id=? ORDER BY created_at DESC LIMIT ?",
                    (session_id, limit),
                ).fetchall()
            else:
                return []
        return [dict(r) for r in rows]
    except Exception:
        return []


# ── Analysis runs ─────────────────────────────────────────────────────────────

def save_analysis_run(
    *,
    jd_text: str = "",
    jd_title: str | None = None,
    jd_company: str | None = None,
    ats_score: float | None = None,
    semantic_score: float | None = None,
    skill_match_score: float | None = None,
    interview_prob: float | None = None,
    missing_skills: list | None = None,
    matched_skills: list | None = None,
    full_result: dict | None = None,
    hallucination_trust: float | None = None,
    resume_version_id: int | None = None,
    user_id: int | None = None,
    session_id: str | None = None,
) -> int | None:
    """Persist a full analysis run. Returns the new row id."""
    try:
        with _get_conn() as conn:
            cur = conn.execute(
                """INSERT INTO analysis_runs
                   (user_id, session_id, resume_version_id, jd_text, jd_title, jd_company,
                    ats_score, semantic_score, skill_match_score, interview_prob,
                    missing_skills, matched_skills, full_result, hallucination_trust, created_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    user_id, session_id, resume_version_id,
                    jd_text[:4000] if jd_text else None,
                    jd_title, jd_company,
                    ats_score, semantic_score, skill_match_score, interview_prob,
                    json.dumps(missing_skills or []),
                    json.dumps(matched_skills or []),
                    json.dumps(full_result) if full_result else None,
                    hallucination_trust,
                    time.time(),
                ),
            )
            return cur.lastrowid
    except Exception as exc:
        logger.warning("save_analysis_run failed: %s", exc)
        return None


def get_analysis_history(
    user_id: int | None = None,
    session_id: str | None = None,
    limit: int = 50,
) -> list[dict]:
    """Return analysis run history, newest first."""
    try:
        with _get_conn() as conn:
            if user_id:
                rows = conn.execute(
                    "SELECT id, jd_title, jd_company, ats_score, semantic_score, "
                    "skill_match_score, interview_prob, created_at "
                    "FROM analysis_runs WHERE user_id=? ORDER BY created_at DESC LIMIT ?",
                    (user_id, limit),
                ).fetchall()
            elif session_id:
                rows = conn.execute(
                    "SELECT id, jd_title, jd_company, ats_score, semantic_score, "
                    "skill_match_score, interview_prob, created_at "
                    "FROM analysis_runs WHERE session_id=? ORDER BY created_at DESC LIMIT ?",
                    (session_id, limit),
                ).fetchall()
            else:
                return []
        return [dict(r) for r in rows]
    except Exception:
        return []


# ── Job applications ──────────────────────────────────────────────────────────

def save_job_application(
    *,
    company: str | None = None,
    job_title: str | None = None,
    job_url: str | None = None,
    status: str = "saved",
    ats_score: float | None = None,
    match_score: float | None = None,
    notes: str | None = None,
    analysis_run_id: int | None = None,
    user_id: int | None = None,
    session_id: str | None = None,
) -> int | None:
    now = time.time()
    try:
        with _get_conn() as conn:
            cur = conn.execute(
                """INSERT INTO job_applications
                   (user_id, session_id, analysis_run_id, company, job_title, job_url,
                    status, ats_score, match_score, notes, created_at, updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (user_id, session_id, analysis_run_id, company, job_title, job_url,
                 status, ats_score, match_score, notes, now, now),
            )
            return cur.lastrowid
    except Exception as exc:
        logger.warning("save_job_application failed: %s", exc)
        return None


def update_job_application_status(app_id: int, status: str) -> bool:
    try:
        with _get_conn() as conn:
            conn.execute(
                "UPDATE job_applications SET status=?, updated_at=? WHERE id=?",
                (status, time.time(), app_id),
            )
        return True
    except Exception:
        return False


def get_job_applications(
    user_id: int | None = None,
    session_id: str | None = None,
) -> list[dict]:
    try:
        with _get_conn() as conn:
            if user_id:
                rows = conn.execute(
                    "SELECT * FROM job_applications WHERE user_id=? ORDER BY updated_at DESC",
                    (user_id,),
                ).fetchall()
            elif session_id:
                rows = conn.execute(
                    "SELECT * FROM job_applications WHERE session_id=? ORDER BY updated_at DESC",
                    (session_id,),
                ).fetchall()
            else:
                return []
        return [dict(r) for r in rows]
    except Exception:
        return []


# ── Analytics helpers ─────────────────────────────────────────────────────────

def get_user_stats(user_id: int) -> dict[str, Any]:
    """Return aggregate stats for a user's dashboard."""
    try:
        with _get_conn() as conn:
            analysis_count = conn.execute(
                "SELECT COUNT(*) FROM analysis_runs WHERE user_id=?", (user_id,)
            ).fetchone()[0]
            resume_count = conn.execute(
                "SELECT COUNT(*) FROM resume_versions WHERE user_id=?", (user_id,)
            ).fetchone()[0]
            best_ats = conn.execute(
                "SELECT MAX(ats_score) FROM analysis_runs WHERE user_id=?", (user_id,)
            ).fetchone()[0]
            app_counts = conn.execute(
                "SELECT status, COUNT(*) as cnt FROM job_applications WHERE user_id=? GROUP BY status",
                (user_id,),
            ).fetchall()
        return {
            "analysis_count": analysis_count,
            "resume_count": resume_count,
            "best_ats_score": best_ats,
            "applications": {row["status"]: row["cnt"] for row in app_counts},
        }
    except Exception:
        return {}
