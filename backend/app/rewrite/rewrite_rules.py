# app/rewrite/rewrite_rules.py

from typing import List


class RewriteRules:

    ALLOWED_ACTIONS = [
        "reword_bullets",
        "reorder_sections",
        "improve_keywords",
        "improve_action_verbs",
        "highlight_existing_experience"
    ]

    FORBIDDEN_ACTIONS = [
        "invent_company",
        "invent_project",
        "invent_skill",
        "invent_certification",
        "invent_degree"
    ]

    @staticmethod
    def validate_recommendation(text: str) -> bool:

        banned_phrases = [
            "add aws experience",
            "create project",
            "invent",
            "fake",
            "fabricate",
            "new certification",
            "new company"
        ]

        text = text.lower()

        for phrase in banned_phrases:
            if phrase in text:
                return False

        return True

    @staticmethod
    def validate_recommendations(recommendations: List[str]):

        safe = []

        for rec in recommendations:
            if RewriteRules.validate_recommendation(rec):
                safe.append(rec)

        return safe