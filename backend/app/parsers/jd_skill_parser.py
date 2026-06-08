import json
import re
from pathlib import Path

_SKILLS_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "skills.json"


def extract_jd_skills(text):

    with _SKILLS_DB_PATH.open("r", encoding="utf-8") as file:

        skills_db = json.load(file)

    text = text.lower()

    found_skills = []

    for skill, aliases in skills_db.items():

        for alias in aliases:

            pattern = r"\b" + re.escape(alias.lower()) + r"\b"

            if re.search(pattern, text):

                found_skills.append(skill)
                break

    return found_skills