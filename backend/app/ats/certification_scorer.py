def calculate_certification_score(
    resume
):

    certs = resume.get(
        "certifications",
        []
    )

    if len(certs) >= 5:
        return 100

    if len(certs) >= 3:
        return 80

    if len(certs) >= 1:
        return 60

    return 0