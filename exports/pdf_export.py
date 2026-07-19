import re
from datetime import datetime

from config import EXPORT_CONFIG
from utils.logging_config import get_logger

try:
    from fpdf import FPDF
except ModuleNotFoundError:
    FPDF = None


class PDFExportError(Exception):
    """Friendly PDF export error for the Streamlit UI."""


logger = get_logger(__name__)


class StudyBuddyPDF(FPDF if FPDF else object):
    def __init__(self, generated_at):
        super().__init__()
        self.generated_at = generated_at
        self.set_auto_page_break(
            auto=True,
            margin=EXPORT_CONFIG.pdf_margin
        )
        self.set_margins(
            EXPORT_CONFIG.pdf_margin,
            EXPORT_CONFIG.pdf_margin,
            EXPORT_CONFIG.pdf_margin
        )

    def footer(self):
        self.set_y(-16)
        self.set_font(
            "Helvetica",
            "I",
            8
        )
        self.set_text_color(110, 120, 135)
        footer_text = (
            f"Generated using AI Study Buddy | "
            f"{self.generated_at.strftime('%d %b %Y, %I:%M %p')} | "
            f"Page {self.page_no()}"
        )
        self.cell(
            0,
            10,
            footer_text,
            align="C"
        )


def create_pdf_export(feature_name, user_prompt, ai_response, student_name=None):
    if FPDF is None:
        logger.error("PDF export requested but fpdf2 is not installed.")
        raise PDFExportError(
            "fpdf2 is not installed. Run: pip install fpdf2"
        )

    if not ai_response or not ai_response.strip():
        raise PDFExportError(
            "Cannot create a PDF because the AI response is empty."
        )

    generated_at = datetime.now()

    try:
        pdf = StudyBuddyPDF(
            generated_at=generated_at
        )
        pdf.add_page()
        _render_header(
            pdf,
            feature_name,
            student_name,
            generated_at
        )
        _render_prompt(
            pdf,
            user_prompt
        )
        _render_response(
            pdf,
            ai_response
        )

        filename = build_export_filename(
            feature_name,
            user_prompt
        )

        return filename, _pdf_to_bytes(pdf)

    except PDFExportError:
        raise

    except Exception as exc:
        logger.exception("PDF generation failed.")
        raise PDFExportError(
            "Could not generate the PDF. Please try again."
        ) from exc


def build_export_filename(feature_name, user_prompt):
    feature_part = _clean_filename_text(
        feature_name
    )
    prompt_part = _clean_filename_text(
        user_prompt
    )

    if prompt_part:
        filename = f"{feature_part}_{prompt_part}.pdf"
    else:
        filename = f"{feature_part}.pdf"

    return filename[:EXPORT_CONFIG.max_filename_length]


def _render_header(pdf, feature_name, student_name, generated_at):
    pdf.set_fill_color(15, 23, 42)
    pdf.rect(
        0,
        0,
        210,
        42,
        style="F"
    )

    pdf.set_xy(
        18,
        12
    )
    pdf.set_text_color(255, 255, 255)
    pdf.set_font(
        "Helvetica",
        "B",
        22
    )
    pdf.cell(
        0,
        8,
        "AI Study Buddy"
    )

    pdf.ln(11)
    pdf.set_x(18)
    pdf.set_font(
        "Helvetica",
        "",
        11
    )
    pdf.cell(
        0,
        7,
        _safe_text(feature_name)
    )

    pdf.ln(8)
    pdf.set_x(18)
    pdf.set_font(
        "Helvetica",
        "",
        9
    )
    date_text = f"Date: {generated_at.strftime('%d %B %Y')}"

    if student_name:
        date_text += f" | Student: {_safe_text(student_name)}"

    pdf.cell(
        0,
        6,
        date_text
    )

    pdf.ln(18)
    pdf.set_text_color(30, 41, 59)


def _render_prompt(pdf, user_prompt):
    prompt = _safe_text(user_prompt).strip()

    if not prompt:
        return

    _section_heading(
        pdf,
        "Original Prompt"
    )
    pdf.set_x(pdf.l_margin)
    pdf.set_font(
        "Helvetica",
        "",
        10
    )
    pdf.set_text_color(71, 85, 105)
    pdf.multi_cell(
        0,
        6,
        prompt[:900]
    )
    pdf.ln(3)


def _render_response(pdf, ai_response):
    _section_heading(
        pdf,
        "Study Material"
    )
    pdf.set_x(pdf.l_margin)
    lines = ai_response.splitlines()
    index = 0

    while index < len(lines):
        line = lines[index].rstrip()

        if not line.strip():
            pdf.ln(2)
            index += 1
            continue

        if _is_table_start(lines, index):
            table_lines = []

            while index < len(lines) and "|" in lines[index]:
                table_lines.append(lines[index])
                index += 1

            _write_table(
                pdf,
                table_lines
            )
            continue

        _write_formatted_line(
            pdf,
            line
        )
        index += 1


def _section_heading(pdf, text):
    pdf.set_font(
        "Helvetica",
        "B",
        15
    )
    pdf.set_text_color(15, 23, 42)
    pdf.cell(
        0,
        9,
        _safe_text(text)
    )
    pdf.ln(9)
    pdf.set_draw_color(56, 189, 248)
    pdf.set_line_width(0.6)
    pdf.line(
        pdf.l_margin,
        pdf.get_y(),
        192,
        pdf.get_y()
    )
    pdf.ln(5)


def _write_formatted_line(pdf, line):
    pdf.set_x(pdf.l_margin)
    text = _clean_markdown(
        line
    )
    stripped = text.strip()

    if stripped.startswith("#"):
        heading = stripped.lstrip("#").strip()
        level = min(
            line.count("#"),
            3
        )
        size = 15 if level == 1 else 13 if level == 2 else 11
        pdf.set_font(
            "Helvetica",
            "B",
            size
        )
        pdf.set_text_color(15, 23, 42)
        pdf.multi_cell(
            0,
            7,
            _safe_text(heading)
        )
        pdf.ln(1)
        return

    if _is_bullet(stripped):
        pdf.set_font(
            "Helvetica",
            "",
            10
        )
        pdf.set_text_color(30, 41, 59)
        pdf.set_x(pdf.l_margin + 3)
        pdf.multi_cell(
            0,
            6,
            f"- {_safe_text(stripped[1:].strip())}"
        )
        return

    if _is_numbered_item(stripped):
        pdf.set_font(
            "Helvetica",
            "",
            10
        )
        pdf.set_text_color(30, 41, 59)
        pdf.multi_cell(
            0,
            6,
            _safe_text(stripped)
        )
        return

    if stripped.endswith(":") and len(stripped) < 90:
        pdf.set_font(
            "Helvetica",
            "B",
            11
        )
        pdf.set_text_color(15, 23, 42)
        pdf.multi_cell(
            0,
            7,
            _safe_text(stripped)
        )
        return

    pdf.set_font(
        "Helvetica",
        "",
        10
    )
    pdf.set_text_color(30, 41, 59)
    pdf.multi_cell(
        0,
        6,
        _safe_text(stripped)
    )


def _write_table(pdf, table_lines):
    rows = [
        [
            _safe_text(cell.strip())
            for cell in line.strip().strip("|").split("|")
        ]
        for line in table_lines
        if not _is_markdown_separator(line)
    ]

    if not rows:
        return

    col_count = max(
        len(row)
        for row in rows
    )
    usable_width = pdf.w - pdf.l_margin - pdf.r_margin
    col_width = usable_width / col_count

    pdf.set_font(
        "Helvetica",
        "B",
        9
    )

    for row_index, row in enumerate(rows):
        if pdf.get_y() > 260:
            pdf.add_page()

        pdf.set_fill_color(226, 232, 240) if row_index == 0 else pdf.set_fill_color(248, 250, 252)
        pdf.set_text_color(15, 23, 42)

        y_start = pdf.get_y()
        x_start = pdf.l_margin
        max_height = 8

        for col_index in range(col_count):
            cell_text = row[col_index] if col_index < len(row) else ""
            x = x_start + (col_index * col_width)
            pdf.set_xy(
                x,
                y_start
            )
            pdf.multi_cell(
                col_width,
                6,
                cell_text,
                border=1,
                fill=True
            )
            max_height = max(
                max_height,
                pdf.get_y() - y_start
            )

        pdf.set_y(
            y_start + max_height
        )
        pdf.set_font(
            "Helvetica",
            "",
            9
        )

    pdf.set_x(pdf.l_margin)
    pdf.ln(4)


def _is_table_start(lines, index):
    return (
        "|" in lines[index]
        and index + 1 < len(lines)
        and _is_markdown_separator(lines[index + 1])
    )


def _is_markdown_separator(line):
    stripped = line.strip().strip("|").replace(" ", "")
    return bool(stripped) and all(
        char in "-:|"
        for char in stripped
    )


def _is_bullet(text):
    return text.startswith(("-", "*", "+", "•"))


def _is_numbered_item(text):
    return re.match(r"^\d+[\.\)]\s+", text) is not None


def _clean_markdown(text):
    cleaned = text.replace("**", "")
    cleaned = cleaned.replace("__", "")
    cleaned = cleaned.replace("`", "")
    return cleaned


def _clean_filename_text(value):
    text = _safe_text(value)
    text = _clean_markdown(text)
    text = re.sub(r"[^A-Za-z0-9]+", "_", text)
    text = text.strip("_")
    return text[:45] or "Export"


def _safe_text(value):
    if value is None:
        return ""

    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2022": "-",
        "\u2026": "...",
        "\u00a0": " ",
    }
    text = str(value)

    for source, replacement in replacements.items():
        text = text.replace(
            source,
            replacement
        )

    return text.encode(
        "latin-1",
        "replace"
    ).decode(
        "latin-1"
    )


def _pdf_to_bytes(pdf):
    output = pdf.output(
        dest="S"
    )

    if isinstance(output, bytearray):
        return bytes(output)

    if isinstance(output, bytes):
        return output

    return output.encode(
        "latin-1"
    )
