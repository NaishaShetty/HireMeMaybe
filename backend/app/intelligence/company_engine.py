"""Company Intelligence Engine — Stage 10.

Given a company name (and optionally a role title), generates a structured
Company Intelligence Report covering:

  - Company overview (mission, size, industry, founded)
  - Tech stack / engineering tools
  - Interview process (stages, typical format)
  - Common interview questions for the company
  - Leadership / cultural principles
  - Estimated salary ranges for the role
  - Recent news / notable events (from LLM training data)

Full runtime fallback chain: tries OpenAI → Gemini → Anthropic on every
request, so a 429 from one provider automatically rolls over to the next.
"""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = (
    "You are a career intelligence researcher who provides accurate, helpful "
    "information about companies and their hiring processes. "
    "Be concise but informative. Return valid JSON only — no markdown, no preamble."
)

_REPORT_PROMPT = """\
Generate a company intelligence report for a candidate preparing to interview at {company}.
{role_line}

Return this exact JSON structure (fill every field with real information where known,
or an empty string / empty list if genuinely unknown):

{{
  "company_overview": {{
    "name": "{company}",
    "industry": "",
    "founded": "",
    "headquarters": "",
    "size": "",
    "mission": "",
    "business_model": "",
    "notable_products_or_services": []
  }},
  "tech_stack": {{
    "languages": [],
    "frameworks": [],
    "infrastructure": [],
    "data_tools": [],
    "notes": ""
  }},
  "interview_process": {{
    "typical_stages": [],
    "format": "",
    "duration_weeks": "",
    "tips": []
  }},
  "common_interview_questions": [
    {{
      "question": "",
      "type": "technical|behavioural|values"
    }}
  ],
  "culture_and_values": {{
    "key_principles": [],
    "work_style": "",
    "known_for": ""
  }},
  "salary_ranges": {{
    "role": "{role}",
    "junior": "",
    "mid": "",
    "senior": "",
    "currency": "USD",
    "source_note": "Estimated from public data (Glassdoor, Levels.fyi, Blind) — verify independently"
  }},
  "recent_news": [],
  "preparation_tips": []
}}

Rules:
- Provide 6–8 common_interview_questions
- Provide 4–6 preparation_tips specific to this company
- Salary ranges should be annual in the format "$X – $Y"
- recent_news should be 2–4 notable headlines or developments (from your training data)
- Return ONLY valid JSON
"""


# ---------------------------------------------------------------------------
# Provider record
# ---------------------------------------------------------------------------

@dataclass
class _Provider:
    name: str
    client: Any
    model: str


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclass
class CompanyIntelReport:
    company_name: str
    role: str
    company_overview: dict[str, Any] = field(default_factory=dict)
    tech_stack: dict[str, Any] = field(default_factory=dict)
    interview_process: dict[str, Any] = field(default_factory=dict)
    common_interview_questions: list[dict[str, Any]] = field(default_factory=list)
    culture_and_values: dict[str, Any] = field(default_factory=dict)
    salary_ranges: dict[str, Any] = field(default_factory=dict)
    recent_news: list[str] = field(default_factory=list)
    preparation_tips: list[str] = field(default_factory=list)
    disclaimer: str = (
        "This report is generated from the AI's training data. "
        "Salary ranges and recent news should be verified via Glassdoor, Levels.fyi, "
        "and the company's official newsroom."
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "company_name": self.company_name,
            "role": self.role,
            "company_overview": self.company_overview,
            "tech_stack": self.tech_stack,
            "interview_process": self.interview_process,
            "common_interview_questions": self.common_interview_questions,
            "culture_and_values": self.culture_and_values,
            "salary_ranges": self.salary_ranges,
            "recent_news": self.recent_news,
            "preparation_tips": self.preparation_tips,
            "disclaimer": self.disclaimer,
        }


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


class CompanyIntelEngine:
    """Generate a company intelligence report via LLM with runtime fallback."""

    def __init__(self) -> None:
        self._providers: list[_Provider] = []
        self._init_providers()

    # ------------------------------------------------------------------
    # Provider initialisation — build ordered list of all available providers
    # ------------------------------------------------------------------

    def _init_providers(self) -> None:
        preferred = os.getenv("REWRITE_PROVIDER", "OPENAI").upper()
        order = [preferred.lower()] + [p for p in ("openai", "gemini", "anthropic") if p != preferred.lower()]
        for name in order:
            p = getattr(self, f"_try_init_{name}")()
            if p:
                self._providers.append(p)

        if not self._providers:
            logger.warning(
                "CompanyIntelEngine: no LLM provider available. "
                "Set OPENAI_API_KEY, GEMINI_API_KEY, or ANTHROPIC_API_KEY."
            )
        else:
            logger.info("CompanyIntelEngine providers: %s", [p.name for p in self._providers])

    def _try_init_openai(self) -> "_Provider | None":
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            return None
        try:
            from openai import OpenAI  # type: ignore[import]
            client = OpenAI(api_key=api_key)
            return _Provider("openai", client, os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
        except ImportError:
            return None

    def _try_init_gemini(self) -> "_Provider | None":
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            return None
        try:
            from google import genai  # type: ignore[import]
            client = genai.Client(api_key=api_key)
            return _Provider("gemini", client, os.getenv("GEMINI_MODEL", "gemini-2.0-flash"))
        except ImportError:
            return None

    def _try_init_anthropic(self) -> "_Provider | None":
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            return None
        try:
            import anthropic  # type: ignore[import]
            client = anthropic.Anthropic(api_key=api_key)
            return _Provider("anthropic", client, os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022"))
        except ImportError:
            return None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(
        self,
        *,
        company: str,
        role: str = "Software Engineer",
    ) -> CompanyIntelReport:
        """Generate a company intelligence report with runtime provider fallback."""
        role_line = f"The candidate is applying for: {role}" if role else ""
        prompt = _REPORT_PROMPT.format(
            company=company,
            role=role,
            role_line=role_line,
        )

        raw_json: dict[str, Any] = {}
        for provider in self._providers:
            try:
                raw_text = self._call_provider(provider, prompt)
                raw_json = self._parse_json(raw_text)
                if raw_json:
                    logger.info("CompanyIntelEngine used provider: %s", provider.name)
                    break
            except Exception as exc:
                logger.warning("CompanyIntelEngine provider %s failed: %s", provider.name, exc)
                continue

        if not raw_json:
            return self._empty_report(company, role)

        return CompanyIntelReport(
            company_name=company,
            role=role,
            company_overview=raw_json.get("company_overview", {}),
            tech_stack=raw_json.get("tech_stack", {}),
            interview_process=raw_json.get("interview_process", {}),
            common_interview_questions=raw_json.get("common_interview_questions", []),
            culture_and_values=raw_json.get("culture_and_values", {}),
            salary_ranges=raw_json.get("salary_ranges", {}),
            recent_news=raw_json.get("recent_news", []),
            preparation_tips=raw_json.get("preparation_tips", []),
        )

    # ------------------------------------------------------------------
    # LLM dispatch
    # ------------------------------------------------------------------

    def _call_provider(self, provider: _Provider, prompt: str) -> str:
        if provider.name == "openai":
            response = provider.client.chat.completions.create(
                model=provider.model,
                messages=[
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=2500,
                temperature=0.3,
            )
            return response.choices[0].message.content or ""

        if provider.name == "gemini":
            full_prompt = f"{_SYSTEM_PROMPT}\n\n{prompt}"
            response = provider.client.models.generate_content(
                model=provider.model, contents=full_prompt
            )
            return response.text or ""

        if provider.name == "anthropic":
            response = provider.client.messages.create(
                model=provider.model,
                max_tokens=2500,
                system=_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text if response.content else ""

        raise RuntimeError(f"Unknown provider: {provider.name}")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_json(text: str) -> dict[str, Any]:
        cleaned = text.strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if match:
                return json.loads(match.group())
            raise

    @staticmethod
    def _empty_report(company: str, role: str) -> CompanyIntelReport:
        return CompanyIntelReport(
            company_name=company,
            role=role,
            company_overview={"name": company, "industry": "", "notes": "Data unavailable — no LLM provider configured"},
            tech_stack={},
            interview_process={},
            common_interview_questions=[],
            culture_and_values={},
            salary_ranges={"role": role, "note": "Unavailable"},
            recent_news=[],
            preparation_tips=[
                f"Research {company}'s mission and recent news before the interview.",
                "Review the job description carefully and prepare concrete examples.",
                "Practice STAR-format answers for your most relevant experiences.",
            ],
            disclaimer=(
                "LLM provider not configured. Set OPENAI_API_KEY, GEMINI_API_KEY, "
                "or ANTHROPIC_API_KEY to enable full company intelligence reports."
            ),
        )
