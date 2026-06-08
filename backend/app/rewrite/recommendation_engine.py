# app/rewrite/recommendation_engine.py

from typing import Dict


class RecommendationEngine:

    @staticmethod
    def generate(analysis: Dict):

        recommendations = []

        issues = analysis["issues"]

        for issue in issues:

            if issue == "Low ATS score":

                recommendations.extend([
                    "Move skills section closer to top",
                    "Increase keyword density naturally",
                    "Improve bullet point clarity"
                ])

            elif issue == "Low semantic similarity":

                recommendations.extend([
                    "Emphasize relevant experience",
                    "Highlight technologies matching the job description",
                    "Reorder achievements by relevance"
                ])

            elif issue.startswith("Missing skill:"):

                skill = issue.replace("Missing skill:", "").strip()

                recommendations.append(
                    f"Mention {skill} only if genuinely used"
                )

        deduplicated = []
        seen = set()

        for recommendation in recommendations:
            if recommendation not in seen:
                deduplicated.append(recommendation)
                seen.add(recommendation)

        return {
            "recommendations": deduplicated
        }
