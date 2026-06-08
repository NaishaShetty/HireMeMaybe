"""Generate human-readable explanations for resume rewrite differences."""

from __future__ import annotations

import difflib
import re
from collections import Counter
from typing import Iterable

from app.parsers.skill_parser import extract_skills


SECTION_PATTERNS: dict[str, tuple[str, ...]] = {
    "summary": ("summary", "professional summary", "profile", "objective"),
    "skills": ("skills", "technical skills", "core skills", "key skills"),
    "experience": ("experience", "work experience", "professional experience", "employment history"),
    "projects": ("projects", "personal projects", "academic projects"),
    "education": ("education", "academic background"),
    "certifications": ("certifications", "certificates", "licenses"),
}

ACTION_VERBS = {
    "achieved",
    "analyzed",
    "built",
    "collaborated",
    "created",
    "delivered",
    "designed",
    "developed",
    "drove",
    "implemented",
    "improved",
    "increased",
    "launched",
    "led",
    "managed",
    "optimized",
    "reduced",
    "refactored",
    "streamlined",
    "strengthened",
    "transformed",
    "validated",
}

STOPWORDS = {
    "and",
    "the",
    "for",
    "with",
    "that",
    "from",
    "into",
    "this",
    "your",
    "their",
    "have",
    "been",
    "were",
    "will",
    "has",
    "had",
    "are",
    "was",
    "but",
    "not",
    "you",
    "our",
    "can",
    "all",
    "any",
    "team",
    "work",
    "skills",
    "experience",
    "resume",
    "job",
}

TOKEN_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9+#./-]*")
HEADER_PATTERN = re.compile(r"^[A-Z][A-Z\s/&-]{2,}$")


class DiffAnalyzer:
    """Compare two resume versions and summarize the observable changes."""

    @staticmethod
    def analyze(before: str, after: str) -> dict[str, list[str]]:
        """Return user-friendly explanations of the textual differences."""

        before_lines = _normalize_lines(before)
        after_lines = _normalize_lines(after)
        added_lines, removed_lines = _line_diff(before_lines, after_lines)
        changes: list[str] = []

        if added_lines:
            changes.extend(_summarize_additions(added_lines))

        if removed_lines:
            changes.extend(_summarize_removals(removed_lines))

        changes.extend(_summarize_section_reordering(before, after))
        changes.extend(_summarize_keyword_changes(before, after))

        if not changes:
            changes.append("No meaningful text changes detected")

        deduplicated: list[str] = []
        seen: set[str] = set()
        for change in changes:
            if change not in seen:
                deduplicated.append(change)
                seen.add(change)

        return {"changes": deduplicated}


def _normalize_lines(text: str) -> tuple[str, ...]:
    return tuple(line.strip() for line in text.splitlines() if line.strip())


def _line_diff(before_lines: tuple[str, ...], after_lines: tuple[str, ...]) -> tuple[list[str], list[str]]:
    matcher = difflib.SequenceMatcher(a=list(before_lines), b=list(after_lines))
    added: list[str] = []
    removed: list[str] = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag in {"insert", "replace"}:
            added.extend(after_lines[j1:j2])
        if tag in {"delete", "replace"}:
            removed.extend(before_lines[i1:i2])

    return added, removed


def _is_section_header(line: str) -> bool:
    normalized = line.strip().lower().rstrip(":")
    if HEADER_PATTERN.match(line.strip()):
        return True

    for headers in SECTION_PATTERNS.values():
        if normalized in headers:
            return True

    return False


def _section_name(line: str) -> str | None:
    normalized = line.strip().lower().rstrip(":")
    for name, headers in SECTION_PATTERNS.items():
        if normalized in headers:
            return name
    return None


def _extract_section_order(text: str) -> list[str]:
    order: list[str] = []
    for line in _normalize_lines(text):
        section = _section_name(line)
        if section and (not order or order[-1] != section):
            order.append(section)
    return order


def _summarize_additions(added_lines: list[str]) -> list[str]:
    changes: list[str] = []
    section_headers = [line for line in added_lines if _is_section_header(line)]
    if section_headers:
        changes.append("Added or expanded resume sections")

    bullet_like = [line for line in added_lines if line.lstrip().startswith(("-", "*"))]
    if bullet_like:
        changes.append("Expanded bullet points with additional detail")

    non_header_additions = [line for line in added_lines if not _is_section_header(line)]
    if non_header_additions and not bullet_like and not section_headers:
        changes.append("Added supporting content")

    return changes


def _summarize_removals(removed_lines: list[str]) -> list[str]:
    if any(_is_section_header(line) for line in removed_lines):
        return ["Removed or condensed at least one section"]
    return ["Removed some existing content"]


def _summarize_section_reordering(before: str, after: str) -> list[str]:
    before_order = _extract_section_order(before)
    after_order = _extract_section_order(after)
    if not before_order or not after_order:
        return []

    changes: list[str] = []
    before_index = {section: index for index, section in enumerate(before_order)}
    after_index = {section: index for index, section in enumerate(after_order)}

    if "skills" in before_index and "skills" in after_index and after_index["skills"] < before_index["skills"]:
        changes.append("Moved skills section higher")

    if before_order != after_order:
        changes.append("Reordered sections for better flow")

    return changes


def _meaningful_tokens(text: str) -> list[str]:
    tokens = []
    for match in TOKEN_PATTERN.finditer(text.lower()):
        token = match.group(0)
        if len(token) <= 2:
            continue
        if token in STOPWORDS:
            continue
        tokens.append(token)
    return tokens


def _token_counts(text: str) -> Counter[str]:
    return Counter(_meaningful_tokens(text))


def _action_verb_count(text: str) -> int:
    tokens = _meaningful_tokens(text)
    return sum(1 for token in tokens if token in ACTION_VERBS)


def _summarize_keyword_changes(before: str, after: str) -> list[str]:
    changes: list[str] = []

    before_skill_hits = set(extract_skills(before))
    after_skill_hits = set(extract_skills(after))
    new_skill_hits = after_skill_hits - before_skill_hits
    if new_skill_hits:
        changes.append("Added additional skill keywords")

    before_action_count = _action_verb_count(before)
    after_action_count = _action_verb_count(after)
    if after_action_count > before_action_count:
        changes.append("Added stronger action verbs")

    before_tokens = _token_counts(before)
    after_tokens = _token_counts(after)
    shared_tokens = set(before_tokens) & set(after_tokens)
    if shared_tokens:
        before_first_hit = _first_keyword_line_index(before, shared_tokens)
        after_first_hit = _first_keyword_line_index(after, shared_tokens)
        if (
            after_first_hit is not None
            and before_first_hit is not None
            and after_first_hit < before_first_hit
        ):
            changes.append("Improved keyword placement")

    return changes


def _first_keyword_line_index(text: str, keywords: Iterable[str]) -> int | None:
    keyword_set = {keyword.lower() for keyword in keywords}
    lines = _normalize_lines(text)
    for index, line in enumerate(lines):
        line_tokens = set(_meaningful_tokens(line))
        if line_tokens & keyword_set:
            return index
    return None
