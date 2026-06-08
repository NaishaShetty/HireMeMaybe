# app/rewrite/rewrite_analyzer.py

from typing import Dict


class RewriteAnalyzer:

    @staticmethod
    def analyze(
        ats_score: float,
        semantic_score: float,
        missing_skills: list
    ) -> Dict:

        issues = []

        if ats_score < 80:
            issues.append("Low ATS score")

        if semantic_score < 0.80:
            issues.append("Low semantic similarity")

        if len(missing_skills) > 0:
            issues.append("Missing required skills")

            for skill in missing_skills:
                issues.append(f"Missing skill: {skill}")

        return {
            "issues": issues
        }