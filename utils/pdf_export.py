from fpdf import FPDF

def create_pdf(text):

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font(
        "Arial",
        size=12
    )

    pdf.multi_cell(
        0,
        10,
        text
    )

    filename = "output.pdf"

    pdf.output(filename)

    return filename