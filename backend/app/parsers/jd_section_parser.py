def extract_responsibilities(text):

    responsibilities = []

    lines = text.split("\n")

    collecting = False

    for line in lines:

        clean = line.strip()

        lower = clean.lower()

        if "responsibilities" in lower:

            collecting = True
            continue

        if any(
            keyword in lower
            for keyword in [
                "requirements",
                "qualifications",
                "preferred",
                "skills"
            ]
        ):
            collecting = False

        if collecting:

            if clean.startswith("-"):

                responsibilities.append(
                    clean
                )

            elif clean.startswith("•"):

                responsibilities.append(
                    clean
                )

    return responsibilities