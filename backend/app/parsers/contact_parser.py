import re


def extract_email(text):

    match = re.search(
        r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}',
        text
    )

    return match.group() if match else None


def extract_phone(text):

    match = re.search(
        r'(\+?\d[\d\s\-]{8,})',
        text
    )

    return match.group() if match else None