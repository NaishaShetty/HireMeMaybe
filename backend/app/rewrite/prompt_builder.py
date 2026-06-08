# app/rewrite/prompt_builder.py

from typing import List


class PromptBuilder:

    @staticmethod
    def build(
        resume_text: str,
        jd_text: str,
        recommendations: List[str]
    ) -> str:

        recommendation_text = "\n".join(
            [f"- {r}" for r in recommendations]
        )

        prompt = f"""
You are an expert ATS Resume Optimizer.

Rewrite the resume to better match the job description.

STRICT RULES:

1. NEVER invent experience.
2. NEVER invent companies.
3. NEVER invent projects.
4. NEVER invent certifications.
5. NEVER invent skills.
6. NEVER fabricate accomplishments.

ALLOWED:

1. Reword bullets.
2. Improve action verbs.
3. Reorder sections.
4. Improve ATS keyword placement.
5. Highlight existing relevant experience.

Recommendations:

{recommendation_text}

======================
RESUME
======================

{resume_text}

======================
JOB DESCRIPTION
======================

{jd_text}

Return ONLY the optimized resume.
"""

        return prompt