def calculate_section_score(
    resume
):

    score = 0

    sections = [

        "education",

        "experience",

        "projects",

        "skills",

        "certifications"
    ]

    for section in sections:

        if resume.get(section):

            score += 20

    return score