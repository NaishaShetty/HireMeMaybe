def get_missing_skills(
    resume_skills,
    jd_skills
):

    resume_set = {
        skill.lower()
        for skill in resume_skills
    }

    missing = []

    for skill in jd_skills:

        if skill.lower() not in resume_set:

            missing.append(skill)

    return missing