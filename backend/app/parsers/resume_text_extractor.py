import pymupdf

def extract_pdf_text(pdf_path):
    doc = pymupdf.open(pdf_path)

    text = ""

    for page in doc:
        text += page.get_text()

    return text