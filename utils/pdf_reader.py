from pypdf import PdfReader

def extract_pdf_text(pdf_file):

    reader = PdfReader(pdf_file)

    text = ""

    for page in reader.pages:

        text += page.extract_text()

    return text