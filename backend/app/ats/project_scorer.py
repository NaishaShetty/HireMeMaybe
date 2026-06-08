def calculate_project_score(
    resume,
    jd
):

    projects = resume.get(
        "projects",
        []
    )

    jd_skills = {
        skill.lower()
        for skill in jd.get(
            "required_skills",
            []
        )
    }

    if not projects:
        return 0

    matches = 0

    for project in projects:

        text = " ".join(
            project.get(
                "description",
                []
            )
        ).lower()

        for skill in jd_skills:

            if skill in text:
                matches += 1

    score = min(
        100,
        matches * 15
    )

    return score