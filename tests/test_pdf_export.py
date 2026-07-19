import pytest

from exports.pdf_export import PDFExportError, build_export_filename, create_pdf_export


def test_build_export_filename_sanitizes_text():
    filename = build_export_filename(
        "Topic Explanation",
        "Machine Learning: Intro?",
    )

    assert filename == "Topic_Explanation_Machine_Learning_Intro.pdf"


def test_create_pdf_export_rejects_empty_response():
    with pytest.raises(PDFExportError):
        create_pdf_export(
            "Topic Explanation",
            "Python",
            "",
        )


def test_create_pdf_export_returns_pdf_bytes():
    filename, pdf_bytes = create_pdf_export(
        "Topic Explanation",
        "Python",
        "# Overview\nPython is a programming language.",
    )

    assert filename.endswith(".pdf")
    assert pdf_bytes.startswith(b"%PDF")


def test_create_pdf_export_with_table_and_list():
    ai_response = (
        "# Python Overview\n"
        "Here is some information about Python:\n\n"
        "| Feature | Description |\n"
        "|---------|-------------|\n"
        "| Syntax  | Very clean  |\n"
        "| Speed   | Moderate    |\n\n"
        "1. First item after the table.\n"
        "2. Second item after the table.\n"
    )
    filename, pdf_bytes = create_pdf_export(
        "Topic Explanation",
        "Python details",
        ai_response,
        student_name="Jaswanth"
    )
    assert filename.endswith(".pdf")
    assert pdf_bytes.startswith(b"%PDF")
