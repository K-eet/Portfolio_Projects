"""
make_pdf.py
Render the one-page target account list from outputs/ranked.csv.

Run score.py first. Plain by design: black on white, one table, readable when
printed, and it must stay on a single A4 page. The script fails if it does not.

Usage:  python make_pdf.py
"""

import csv
import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

HERE = os.path.dirname(os.path.abspath(__file__))
RANKED_CSV = os.path.join(HERE, "outputs", "ranked.csv")
PDF_PATH = os.path.join(HERE, "outputs", "acquirepad_uk_targets.pdf")

# The cut must not split a tie. make_pdf checks this before drawing anything.
TOP_N = 15
METHOD_MAX_LINES = 2

TITLE = "Acquirepad UK: first target accounts"
METHOD = (
    "Acquirepad is the AI-native operating system and data layer for the real estate industry. "
    "27 buyers of UK commercial property scored on six dimensions, led by recent UK triggers."
)
PLAYS_HEAD = "Where I'd start"
PLAYS = [
    "<b>UK firms with new capital.</b> Martley, NewRiver, Chancerygate and Focus Industrial have a new "
    "fund, partner, owner or platform this year, so their systems are being chosen now.",
    "<b>UK managers buying often.</b> Clearbell, Custodian and Greenridge do frequent small deals, each "
    "with its own IM and rent roll.",
    "<b>Continental buyers of small UK lots.</b> Edmond de Rothschild, Iroko, Corum and Remake. "
    "Many agent IMs per deal, small UK teams. Advenis, a French customer, is the reference.",
    "<b>First 30 days:</b> follow up every UK lead from London, contact the top 15 "
    "with a tailored note, and report weekly on any conversions.",
]
# Shown below the table: not targets, but the fastest UK wins may come from accounts already won.
CUSTOMERS_NOTE = (
    "<b>Not on the list: existing customers.</b> Hines bought three UK retail parks in September 2026. "
    "Advenis launched its Eden SCPI with the UK as a target market. Both are expansion accounts."
)
REPO_URL = ("https://github.com/K-eet/Portfolio_Projects/tree/main/"
            "Ideal%20Customer%20Profile%20project/case_studies/acquirepad_uk")
# Shown in full so a printed copy still leads to the case study, not the repo root.
REPO_TEXT = ("github.com/K-eet/Portfolio_Projects/tree/main/"
             "Ideal%20Customer%20Profile%20project/case_studies/acquirepad_uk")
FOOTER = (f"Keet Lee  |  MSc Applied AI for Business, Henley Business School  |  Research date 19 October 2026<br/>"
          f"Full scoring and sources: <link href='{REPO_URL}' color='#1a4fa0'>{REPO_TEXT}</link>")

MARGIN = 14 * mm
GREY = colors.HexColor("#555555")
RULE = colors.HexColor("#bbbbbb")


def styles():
    def style(name, size, leading, bold=False, colour=colors.black, indent=0):
        font = "Helvetica-Bold" if bold else "Helvetica"
        return ParagraphStyle(name, fontName=font, fontSize=size, leading=leading,
                              textColor=colour, alignment=TA_LEFT,
                              leftIndent=indent, bulletIndent=0)

    return {
        "title": style("title", 17, 21, bold=True),
        "method": style("method", 8.5, 11, colour=GREY),
        "section": style("section", 9.5, 12, bold=True),
        "play": style("play", 8.5, 10.4, indent=9),
        "head": style("head", 8, 10, bold=True),
        "cell": style("cell", 8, 9.6),
        "firm": style("firm", 8, 9.6, bold=True),
        "footer": style("footer", 8, 10, colour=GREY),
    }


def short_trigger(text):
    """The CSV records 'None found ... (unverified)' in full. On the page, say it briefly."""
    return "None found (unverified)" if text.startswith("None") else text


def check_cut(rows, top_n):
    """Refuse a cut that separates two firms with the same total."""
    if len(rows) > top_n and rows[top_n - 1]["total_score"] == rows[top_n]["total_score"]:
        raise SystemExit(f"TOP_N = {top_n} splits a tie at {rows[top_n]['total_score']}. Move the cut.")


def build_table(rows, st):
    header = ["#", "Firm", "Why it fits", "Trigger", "First move"]
    data = [[Paragraph(h, st["head"]) for h in header]]
    for row in rows:
        data.append([
            Paragraph(row["rank"], st["cell"]),
            Paragraph(row["firm"], st["firm"]),
            Paragraph(row["why_fit"], st["cell"]),
            Paragraph(short_trigger(row["trigger"]), st["cell"]),
            Paragraph(row["first_move"], st["cell"]),
        ])

    width = A4[0] - 2 * MARGIN
    col_widths = [6 * mm, 29 * mm]
    rest = width - sum(col_widths)
    col_widths += [rest * 0.34, rest * 0.32, rest * 0.34]

    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, colors.black),
        ("LINEBELOW", (0, 1), (-1, -1), 0.3, RULE),
        ("TOPPADDING", (0, 0), (-1, -1), 2.2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2),
        ("LEFTPADDING", (0, 0), (-1, -1), 2.5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    return table


def main():
    if not os.path.exists(RANKED_CSV):
        raise SystemExit(f"{RANKED_CSV} not found. Run `python score.py` first.")
    with open(RANKED_CSV, newline="", encoding="utf-8") as fh:
        ranked = list(csv.DictReader(fh))
    check_cut(ranked, TOP_N)
    rows = ranked[:TOP_N]

    st = styles()
    pages = []

    def footer(canvas, doc):
        pages.append(doc.page)
        canvas.saveState()
        p = Paragraph(FOOTER, st["footer"])
        _, h = p.wrap(A4[0] - 2 * MARGIN, MARGIN)
        p.drawOn(canvas, MARGIN, MARGIN - h - 1 * mm)
        canvas.restoreState()

    doc = SimpleDocTemplate(
        PDF_PATH, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN, bottomMargin=MARGIN + 8 * mm,
        title=TITLE, author="Keet Lee",
    )
    method = Paragraph(METHOD, st["method"])
    # Measure at the width the frame actually prints: SimpleDocTemplate pads it 6pt each side.
    _, height = method.wrap(A4[0] - 2 * MARGIN - 12, A4[1])
    lines = round(height / st["method"].leading)
    if lines > METHOD_MAX_LINES:
        raise SystemExit(f"Method note runs to {lines} lines. Keep it to {METHOD_MAX_LINES}.")

    story = [
        Paragraph(TITLE, st["title"]),
        Spacer(1, 2 * mm),
        method,
        Spacer(1, 3 * mm),
        Paragraph(PLAYS_HEAD, st["section"]),
        Spacer(1, 1 * mm),
    ]
    story += [Paragraph(p, st["play"], bulletText="•") for p in PLAYS]
    story += [Spacer(1, 3 * mm), build_table(rows, st),
              Spacer(1, 3 * mm), Paragraph(CUSTOMERS_NOTE, st["play"], bulletText="\u2022")]
    doc.build(story, onFirstPage=footer, onLaterPages=footer)

    if len(pages) != 1:
        raise SystemExit(f"PDF ran to {len(pages)} pages. It must fit on one A4 page.")
    print(f"Wrote {PDF_PATH} (1 page, top {len(rows)} firms)")


if __name__ == "__main__":
    main()
