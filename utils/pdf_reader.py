from pypdf import PdfReader

def extract_pdf_text(pdf_file):

    reader = PdfReader(pdf_file)

    text_parts = []

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text_parts.append(
                page_text
            )

    return "\n".join(
        text_parts
    )
