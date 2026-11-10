
from io import BytesIO
from pathlib import Path
from datetime import datetime
from html import escape
from urllib.parse import urlsplit

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle


# ==========================================================
# CYBERSENTINEL AI - PREMIUM SINGLE PAGE PDF REPORT
# Model: v6.7
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent
FONT_DIR = BASE_DIR / "fonts"

PAGE_W, PAGE_H = A4

# Theme
BG = colors.HexColor("#080F20")
PANEL = colors.HexColor("#121E35")
PANEL_ALT = colors.HexColor("#1A2A43")
CYAN = colors.HexColor("#00D9FF")
WHITE = colors.HexColor("#F1F7FF")
MUTED = colors.HexColor("#A7B8CE")
BORDER = colors.HexColor("#2B415D")
GREEN = colors.HexColor("#00E6A0")
AMBER = colors.HexColor("#FFBF47")
RED = colors.HexColor("#FF6478")

MARGIN = 48
CONTENT_W = PAGE_W - 2 * MARGIN


# ==========================================================
# FONT REGISTRATION
# ==========================================================

def register_font(name, filename, fallback):
    path = FONT_DIR / filename

    if path.is_file():
        try:
            pdfmetrics.registerFont(TTFont(name, str(path)))
            return name
        except Exception as exc:
            print(f"Font warning ({filename}): {exc}")

    print(f"Using fallback for {filename}")
    return fallback


TITLE_FONT = register_font(
    "OrbitronBold",
    "Orbitron-Bold.ttf",
    "Helvetica-Bold"
)

HEADING_FONT = register_font(
    "OrbitronSemiBold",
    "Orbitron-SemiBold.ttf",
    "Helvetica-Bold"
)

BODY_FONT = register_font(
    "PoppinsRegular",
    "Poppins-Regular.ttf",
    "Helvetica"
)

BODY_BOLD_FONT = register_font(
    "PoppinsSemiBold",
    "Poppins-SemiBold.ttf",
    "Helvetica-Bold"
)


# ==========================================================
# DRAWING HELPERS
# ==========================================================

def text(c, x, y, value, font=BODY_FONT,
         size=9, color=WHITE):
    c.setFillColor(color)
    c.setFont(font, size)
    c.drawString(x, y, str(value))


def right_text(c, x, y, value, font=BODY_FONT,
               size=9, color=WHITE):
    c.setFillColor(color)
    c.setFont(font, size)
    c.drawRightString(x, y, str(value))


def center_text(c, x, y, value, font=BODY_FONT,
                size=9, color=WHITE):
    c.setFillColor(color)
    c.setFont(font, size)
    c.drawCentredString(x, y, str(value))


def panel(c, x, y, w, h, fill=PANEL, radius=9):
    c.setFillColor(fill)
    c.roundRect(
        x, y, w, h, radius,
        stroke=0,
        fill=1
    )


def line(c, x1, y1, x2, y2, color=BORDER, width=0.7):
    c.setStrokeColor(color)
    c.setLineWidth(width)
    c.line(x1, y1, x2, y2)


def section_title(c, y, title):
    text(
        c, MARGIN, y, title,
        HEADING_FONT, 10.5, CYAN
    )


def paragraph(c, value, x, top_y, width,
              size=8, color=MUTED,
              font=BODY_FONT, leading=12,
              max_height=100):
    style = ParagraphStyle(
        "pdf_text",
        fontName=font,
        fontSize=size,
        leading=leading,
        textColor=color,
        spaceAfter=0,
        wordWrap="CJK",
    )

    p = Paragraph(
        escape(str(value)),
        style
    )

    _, height = p.wrap(width, max_height)
    p.drawOn(c, x, top_y - height)

    return height


def fit_text(c, value, x, y, max_width,
             font=BODY_FONT, size=8,
             min_size=6.5, color=WHITE):
    value = str(value)
    current = size

    while (
        current > min_size
        and pdfmetrics.stringWidth(
            value, font, current
        ) > max_width
    ):
        current -= 0.25

    if pdfmetrics.stringWidth(
        value, font, current
    ) > max_width:
        while value and pdfmetrics.stringWidth(
            value + "...", font, current
        ) > max_width:
            value = value[:-1]
        value += "..."

    text(c, x, y, value, font, current, color)


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default



def score_percent(value):
    # Scanner v6.7 already returns percentages (0-100).
    return max(0.0, min(100.0, safe_float(value)))


def score_color(score):
    if score < 30:
        return GREEN
    if score < 70:
        return AMBER
    return RED


# ==========================================================
# BACKGROUND
# ==========================================================

def draw_background(c):
    c.setFillColor(BG)
    c.rect(
        0, 0, PAGE_W, PAGE_H,
        fill=1, stroke=0
    )

    c.setFillColor(CYAN)
    c.rect(
        0, PAGE_H - 9,
        PAGE_W, 9,
        fill=1, stroke=0
    )

    # Futuristic decorative diagonal lines
    c.setStrokeColor(BORDER)
    c.setLineWidth(1)

    for i in range(5):
        x = PAGE_W - 115 + i * 17
        c.line(
            x, PAGE_H - 26,
            x + 28, PAGE_H - 54
        )


# ==========================================================
# HEADER
# ==========================================================

def draw_header(c, generated_at, result):
    center_text(
        c, PAGE_W / 2, 757,
        "CYBERSENTINEL AI",
        TITLE_FONT, 21, CYAN
    )

    center_text(
        c, PAGE_W / 2, 734,
        "ADVANCED URL THREAT ANALYSIS REPORT",
        HEADING_FONT, 9, MUTED
    )

    line(
        c, MARGIN, 716,
        PAGE_W - MARGIN, 716,
        CYAN, 1
    )

    text(
        c, MARGIN, 699,
        f"Generated: {generated_at}",
        BODY_FONT, 7.2, MUTED
    )

    right_text(
        c, PAGE_W - MARGIN, 699,
        f"MODEL {result.get('model_version', 'unknown')}",
        BODY_BOLD_FONT, 7.5, CYAN
    )


# ==========================================================
# THREAT OVERVIEW
# ==========================================================

def draw_overview(c, result):
    section_title(
        c, 669,
        "THREAT ANALYSIS OVERVIEW"
    )

    x = MARGIN
    y = 578
    w = CONTENT_W
    h = 72

    panel(c, x, y, w, h)

    col_w = w / 3

    line(c, x + col_w, y + 10,
         x + col_w, y + h - 10)

    line(c, x + 2 * col_w, y + 10,
         x + 2 * col_w, y + h - 10)

    prediction = str(
        result.get("prediction", "Unknown")
    ).upper()

    score = score_percent(
        result.get("threat_score", 0)
    )

    risk = str(
        result.get("risk_level", "Unknown")
    ).upper()

    labels = [
        "AI PREDICTION",
        "MODEL THREAT SCORE",
        "RISK LEVEL"
    ]

    values = [
        prediction,
        f"{score:.2f}%",
        risk
    ]

    for i in range(3):
        cx = x + col_w * (i + 0.5)

        center_text(
            c, cx, 626,
            labels[i],
            BODY_BOLD_FONT, 7.4, MUTED
        )

        font = TITLE_FONT if i == 1 else HEADING_FONT
        font_size = 12 if i == 1 else 9

        value = values[i]

        while (
            font_size > 6
            and pdfmetrics.stringWidth(
                value, font, font_size
            ) > col_w - 14
        ):
            font_size -= 0.3

        center_text(
            c, cx, 602,
            value,
            font, font_size,
            score_color(score) if i == 1 else WHITE
        )

    # Risk indicator
    panel(
        c, MARGIN, 538,
        CONTENT_W, 30,
        PANEL_ALT, 5
    )

    c.setFillColor(score_color(score))
    c.roundRect(
        MARGIN, 538,
        4, 30, 2,
        stroke=0, fill=1
    )

    text(
        c, MARGIN + 13, 549,
        f"RISK INDICATOR: {risk}",
        BODY_BOLD_FONT, 8, WHITE
    )


# ==========================================================
# URL INFORMATION
# ==========================================================

def draw_url_information(c, result):
    section_title(
        c, 516,
        "URL INFORMATION"
    )

    x = MARGIN
    top = 498
    row_h = 29
    header_h = 29

    rows = [
        ("URL", result.get("url", "N/A")),
        ("Hostname", result.get("hostname", "N/A")),
        ("Path", result.get("path", "/")),
        ("Validation", "Input format checks passed"),
        ("Model Version", str(result.get("model_version", "unknown"))),
    ]

    total_h = header_h + len(rows) * row_h
    bottom = top - total_h

    panel(
        c, x, bottom,
        CONTENT_W, total_h,
        PANEL, 5
    )

    c.setFillColor(PANEL_ALT)
    c.rect(
        x, top - header_h,
        CONTENT_W, header_h,
        fill=1, stroke=0
    )

    text(
        c, x + 12, top - 19,
        "FIELD",
        HEADING_FONT, 8.5, CYAN
    )

    text(
        c, x + 150, top - 19,
        "VALUE",
        HEADING_FONT, 8.5, CYAN
    )

    line(
        c, x, top - header_h,
        x + CONTENT_W, top - header_h,
        CYAN, 0.8
    )

    for i, (label, value) in enumerate(rows):
        row_top = top - header_h - i * row_h
        row_bottom = row_top - row_h

        if i % 2 == 1:
            c.setFillColor(PANEL_ALT)
            c.rect(
                x, row_bottom,
                CONTENT_W, row_h,
                fill=1, stroke=0
            )

        text(
            c, x + 12, row_bottom + 10,
            label,
            BODY_FONT, 8, MUTED
        )

        fit_text(
            c, value,
            x + 150, row_bottom + 10,
            CONTENT_W - 165,
            BODY_FONT, 8, 6.5, WHITE
        )

        if i < len(rows) - 1:
            line(
                c, x, row_bottom,
                x + CONTENT_W, row_bottom
            )


# ==========================================================
# CLASSIFICATION SCORES
# ==========================================================

def draw_classification(c, result):
    section_title(
        c, 299,
        "AI CLASSIFICATION SCORES"
    )

    scores = result.get("class_scores") or {}

    categories = [
        "benign",
        "defacement",
        "malware",
        "phishing"
    ]

    x = MARGIN
    top = 282
    header_h = 28
    row_h = 27

    total_h = header_h + 4 * row_h
    bottom = top - total_h

    panel(
        c, x, bottom,
        CONTENT_W, total_h,
        PANEL, 5
    )

    c.setFillColor(PANEL_ALT)
    c.rect(
        x, top - header_h,
        CONTENT_W, header_h,
        fill=1, stroke=0
    )

    text(
        c, x + 12, top - 18,
        "THREAT CATEGORY",
        HEADING_FONT, 8.5, CYAN
    )

    right_text(
        c, x + CONTENT_W - 15, top - 18,
        "MODEL SCORE",
        HEADING_FONT, 8.5, CYAN
    )

    line(
        c, x, top - header_h,
        x + CONTENT_W, top - header_h,
        CYAN, 0.8
    )

    normalized = {
        str(k).lower(): v
        for k, v in scores.items()
    }

    for i, category in enumerate(categories):
        row_top = top - header_h - i * row_h
        row_bottom = row_top - row_h

        if i % 2 == 1:
            c.setFillColor(PANEL_ALT)
            c.rect(
                x, row_bottom,
                CONTENT_W, row_h,
                fill=1, stroke=0
            )

        value = normalized.get(category, 0)
        percentage = score_percent(value)

        text(
            c, x + 12, row_bottom + 9,
            category.title(),
            BODY_FONT, 8, WHITE
        )

        right_text(
            c, x + CONTENT_W - 15,
            row_bottom + 9,
            f"{percentage:.2f}%",
            BODY_BOLD_FONT, 8, WHITE
        )

        if i < 3:
            line(
                c, x, row_bottom,
                x + CONTENT_W, row_bottom
            )


# ==========================================================
# SECURITY DISCLAIMER
# ==========================================================

def draw_disclaimer(c):
    section_title(
        c, 126,
        "SECURITY DISCLAIMER"
    )

    disclaimer = (
        "This report contains uncalibrated machine-learning "
        "model estimates, not verified website safety "
        "probabilities. CyberSentinel AI does not visit "
        "the URL or inspect live website content. "
        "A lower threat score does not guarantee safety, "
        "and a higher score does not confirm malicious "
        "activity. Independent verification is recommended."
    )

    paragraph(
        c, disclaimer,
        MARGIN, 114,
        CONTENT_W,
        size=7.1,
        leading=10.5,
        max_height=65
    )


# ==========================================================
# FOOTER
# ==========================================================

def draw_footer(c):
    line(
        c, MARGIN, 44,
        PAGE_W - MARGIN, 44,
        BORDER, 0.7
    )

    text(
        c, MARGIN, 29,
        "CYBERSENTINEL AI | URL THREAT INTELLIGENCE",
        BODY_FONT, 6.5, MUTED
    )

    right_text(
        c, PAGE_W - MARGIN, 29,
        "PAGE 1 OF 1",
        BODY_BOLD_FONT, 6.5, MUTED
    )


# ==========================================================
# MAIN PDF GENERATOR
# ==========================================================

def generate_pdf_report(result):
    """
    Accepts a scanner result dictionary.
    Returns PDF bytes for Streamlit download.
    """

    buffer = BytesIO()

    c = canvas.Canvas(
        buffer,
        pagesize=A4,
        pageCompression=1
    )

    c.setTitle(
        "CyberSentinel AI - URL Threat Analysis"
    )

    c.setAuthor("CyberSentinel AI")
    c.setSubject("AI URL Threat Analysis Report")

    generated_at = datetime.now().astimezone().strftime(
        "%Y-%m-%d %H:%M:%S %z"
    )

    draw_background(c)
    draw_header(c, generated_at, result)
    draw_overview(c, result)
    draw_url_information(c, result)
    draw_classification(c, result)
    draw_disclaimer(c)
    draw_footer(c)

    c.showPage()
    c.save()

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes


# ==========================================================
# STANDALONE TEST
# ==========================================================

if __name__ == "__main__":

    sample_result = {
        "url": "https://example.com",
        "hostname": "example.com",
        "path": "/",
        "prediction": "benign",
        "threat_score": 0.0610,
        "risk_level": "Lower Model Score",
        "class_scores": {
            "benign": 0.9390,
            "defacement": 0.0016,
            "malware": 0.0098,
            "phishing": 0.0495
        }
    }

    pdf_data = generate_pdf_report(sample_result)

    output_path = (
        BASE_DIR / "CyberSentinel_Futuristic_Report.pdf"
    )

    output_path.write_bytes(pdf_data)

    print("Premium PDF generated successfully!")
    print(f"Saved to: {output_path}")
    print(f"PDF size: {len(pdf_data)} bytes")
    print(f"Title Font: {TITLE_FONT}")
    print(f"Heading Font: {HEADING_FONT}")
    print(f"Body Font: {BODY_FONT}")
    print(f"Body Bold Font: {BODY_BOLD_FONT}")
