"""Cover Letter Engine — generates a tailored cover letter from resume + JD.

Uses the same multi-provider LLM infrastructure as InterviewEngine and
RewriteEngine (OpenAI → Gemini → Anthropic fallback chain).

Anti-hallucination: the prompt explicitly forbids inventing experience,
companies, projects, or skills not present in the source resume.
"""

from __future__ import annotations

import logging
import os
import re
import textwrap
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = (
    "You are a professional career coach who writes compelling, personalized cover letters. "
    "You only use facts explicitly stated in the candidate's resume — you never invent "
    "experience, companies, skills, or achievements. "
    "Return only the cover letter text — no markdown, no commentary, no preamble."
)

_COVER_LETTER_PROMPT = """\
Write a professional cover letter for the following candidate applying to the specified role.

=== CANDIDATE RESUME ===
{resume_text}

=== JOB DESCRIPTION ===
{jd_text}

=== ROLE / COMPANY ===
Role: {role}
Company: {company}

Instructions:
- Address the hiring manager professionally (use "Dear Hiring Manager," if no name is known)
- Opening paragraph: express genuine enthusiasm for the role and company; mention 1–2 specific things from the JD that excite the candidate
- Middle paragraph(s): connect the candidate's most relevant experience and skills directly to the key requirements in the JD; use concrete achievements from the resume (with numbers when available)
- Closing paragraph: reiterate interest, invite next steps, thank the reader
- Keep length to 3–4 paragraphs (≈250–350 words)
- Use a professional but warm, human tone — avoid hollow buzzwords
- Do NOT invent any experience, company names, certifications, or skills not in the resume
- End with: Sincerely,\\n[Candidate Name]

Return ONLY the cover letter text, starting with "Dear Hiring Manager," (or a proper salutation).
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
# Result
# ---------------------------------------------------------------------------

@dataclass
class CoverLetterResult:
    cover_letter: str = ""
    role: str = ""
    company: str = ""
    word_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "cover_letter": self.cover_letter,
            "role": self.role,
            "company": self.company,
            "word_count": self.word_count,
        }


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class CoverLetterEngine:
    """Generate a tailored cover letter from a resume and job description."""

    def __init__(self) -> None:
        self._providers: list[_Provider] = []
        self._init_providers()

    # ------------------------------------------------------------------
    # Provider init — identical pattern to InterviewEngine
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
                "CoverLetterEngine: no LLM provider available. "
                "Set OPENAI_API_KEY, GEMINI_API_KEY, or ANTHROPIC_API_KEY."
            )
        else:
            logger.info("CoverLetterEngine providers: %s", [p.name for p in self._providers])

    def _try_init_openai(self) -> "_Provider | None":
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            return None
        try:
            from openai import OpenAI  # type: ignore[import]
            return _Provider("openai", OpenAI(api_key=api_key), os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
        except ImportError:
            return None

    def _try_init_gemini(self) -> "_Provider | None":
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            return None
        try:
            from google import genai  # type: ignore[import]
            return _Provider("gemini", genai.Client(api_key=api_key), os.getenv("GEMINI_MODEL", "gemini-2.0-flash"))
        except ImportError:
            return None

    def _try_init_anthropic(self) -> "_Provider | None":
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        if not api_key:
            return None
        try:
            import anthropic  # type: ignore[import]
            return _Provider("anthropic", anthropic.Anthropic(api_key=api_key), os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022"))
        except ImportError:
            return None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(
        self,
        *,
        resume_text: str,
        jd_text: str,
        role: str = "the role",
        company: str = "your company",
    ) -> CoverLetterResult:
        prompt = _COVER_LETTER_PROMPT.format(
            resume_text=resume_text[:4000],
            jd_text=jd_text[:2000],
            role=role,
            company=company,
        )

        letter = ""
        for provider in self._providers:
            try:
                letter = self._call_provider(provider, prompt).strip()
                if letter:
                    logger.info("CoverLetterEngine used provider: %s", provider.name)
                    break
            except Exception as exc:
                logger.warning("CoverLetterEngine provider %s failed: %s", provider.name, exc)

        if not letter:
            letter = self._fallback_letter(resume_text, role, company)

        word_count = len(letter.split())
        return CoverLetterResult(
            cover_letter=letter,
            role=role,
            company=company,
            word_count=word_count,
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
                max_tokens=700,
                temperature=0.6,
            )
            return response.choices[0].message.content or ""

        if provider.name == "gemini":
            full_prompt = f"{_SYSTEM_PROMPT}\n\n{prompt}"
            response = provider.client.models.generate_content(
                model=provider.model,
                contents=full_prompt,
            )
            return response.text or ""

        if provider.name == "anthropic":
            response = provider.client.messages.create(
                model=provider.model,
                max_tokens=700,
                system=_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text if response.content else ""

        raise ValueError(f"Unknown provider: {provider.name}")

    # ------------------------------------------------------------------
    # Rule-based fallback (no LLM available)
    # ------------------------------------------------------------------

    def _fallback_letter(self, resume_text: str, role: str, company: str) -> str:
        name = resume_text.splitlines()[0].strip() if resume_text.strip() else "Candidate"
        return textwrap.dedent(f"""\
            Dear Hiring Manager,

            I am writing to express my strong interest in the {role} position at {company}. \
            Based on my background and experience, I believe I am a strong fit for this opportunity.

            Throughout my career, I have developed a broad set of skills directly relevant to this role. \
            I am excited by the challenges and growth opportunities this position offers, and I am confident \
            I can make a meaningful contribution to your team from day one.

            I would welcome the opportunity to discuss how my experience aligns with your needs. \
            Thank you for your time and consideration.

            Sincerely,
            {name}
        """)
