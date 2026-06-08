"""Append successful rewrite examples to a JSONL training dataset.

The dataset is stored at ``data/rewrite_dataset.jsonl`` relative to the backend
root so it can be consumed later for supervised fine-tuning or evaluation.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

_WRITE_LOCK = Lock()
_DEFAULT_DATASET_PATH = (
    Path(__file__).resolve().parents[2] / "data" / "rewrite_dataset.jsonl"
)


def _utc_timestamp() -> str:
    """Return an ISO 8601 UTC timestamp with a trailing ``Z``."""

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00",
        "Z",
    )


def get_dataset_path(dataset_path: Path | None = None) -> Path:
    """Resolve the dataset path and ensure the parent directory exists."""

    resolved_path = Path(dataset_path) if dataset_path is not None else _DEFAULT_DATASET_PATH
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    return resolved_path


def append_rewrite_example(
    *,
    resume_before: str,
    resume_after: str,
    jd: str,
    ats_before: float,
    ats_after: float,
    improvement: float,
    timestamp: str | None = None,
    dataset_path: Path | None = None,
) -> Path:
    """Append one rewrite example to the JSONL dataset.

    The write is protected by a process-local lock to prevent interleaved lines
    when multiple requests complete in parallel.
    """

    target_path = get_dataset_path(dataset_path)
    record = {
        "resume_before": resume_before,
        "resume_after": resume_after,
        "jd": jd,
        "ats_before": round(float(ats_before), 2),
        "ats_after": round(float(ats_after), 2),
        "improvement": round(float(improvement), 2),
        "timestamp": timestamp or _utc_timestamp(),
    }

    line = json.dumps(record, ensure_ascii=False)

    with _WRITE_LOCK:
        with target_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(line)
            handle.write("\n")
            handle.flush()

            try:
                os.fsync(handle.fileno())
            except OSError:
                # fsync can fail on some virtualized or networked filesystems;
                # the append has still completed successfully.
                pass

    return target_path
