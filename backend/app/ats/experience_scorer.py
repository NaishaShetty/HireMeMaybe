def calculate_experience_score(
    resume,
    jd
):

    experiences = resume.get(
        "experience",
        []
    )

    jd_skills = {
        skill.lower()
        for skill in jd.get(
            "required_skills",
            []
        )
    }

    if not experiences:
        return 0

    matches = 0

    for exp in experiences:

        text = " ".join(
            exp.get(
                "description",
                []
            )
        ).lower()

        for skill in jd_skills:

            if skill in text:
                matches += 1

    score = min(
        100,
        matches * 20
    )

    return score