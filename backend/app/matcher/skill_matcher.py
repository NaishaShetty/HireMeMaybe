def get_matched_skills(
    resume_skills,
    jd_skills
):

    resume_set = {
        skill.lower()
        for skill in resume_skills
    }

    matched = []

    for skill in jd_skills:

        if skill.lower() in resume_set:

            matched.append(skill)

    return matched