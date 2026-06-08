"""Score resume formatting quality based on structural signals."""


def calculate_formatting_score(resume: dict | None = None) -> float:
    """Evaluate formatting quality from the parsed resume structure.

    Checks for contact info, populated sections, and bullet-point content.
    Returns a score between 0 and 100.
    """
    if not resume:
        return 50.0

    score = 100.0

    # Contact information
    if not resume.get("email"):
        score -= 15
    if not resume.get("phone"):
        score -= 10

    # Critical sections should be populated
    required_sections = {
        "skills": 15,
        "experience": 20,
        "education": 10,
    }
    for section, penalty in required_sections.items():
        if not resume.get(section):
            score -= penalty

    # Experience entries should have bullet-point descriptions
    experience = resume.get("experience", [])
    if experience:
        entries_without_bullets = sum(
            1 for exp in experience if not exp.get("description")
        )
        if entries_without_bullets > 0:
            score -= min(15, entries_without_bullets * 5)

    # Projects should have descriptions
    projects = resume.get("projects", [])
    if projects:
        entries_without_desc = sum(
            1 for p in projects if not p.get("description")
        )
        if entries_without_desc > 0:
            score -= min(10, entries_without_desc * 3)

    return max(0.0, round(score, 2))
