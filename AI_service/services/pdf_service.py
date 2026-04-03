"""
PDF Generation Service
Converts a Markdown document string into a professional PDF using reportlab.
Saves to static/pdfs/{video_id}.pdf and returns the relative URL.
"""

import os
import re
import logging
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

logger = logging.getLogger(__name__)

PDF_OUTPUT_DIR = os.getenv("PDF_OUTPUT_DIR", "static/pdfs")

# ── Colour Palette ──────────────────────────────────────────
PRIMARY   = colors.HexColor("#2563EB")   # blue-600
SECONDARY = colors.HexColor("#1E3A5F")   # dark navy
ACCENT    = colors.HexColor("#10B981")   # emerald-500
MUTED     = colors.HexColor("#6B7280")   # gray-500
TEXT      = colors.HexColor("#111827")   # almost black
WHITE     = colors.white


def _build_styles():
    base = getSampleStyleSheet()
    styles = {}

    styles["title"] = ParagraphStyle(
        "DocTitle",
        fontSize=24, fontName="Helvetica-Bold",
        textColor=SECONDARY, spaceAfter=6,
        alignment=TA_CENTER,
    )
    styles["meta"] = ParagraphStyle(
        "Meta",
        fontSize=9, fontName="Helvetica",
        textColor=MUTED, spaceAfter=12,
        alignment=TA_CENTER,
    )
    styles["h2"] = ParagraphStyle(
        "H2",
        fontSize=14, fontName="Helvetica-Bold",
        textColor=PRIMARY, spaceBefore=16, spaceAfter=6,
    )
    styles["h3"] = ParagraphStyle(
        "H3",
        fontSize=12, fontName="Helvetica-Bold",
        textColor=SECONDARY, spaceBefore=10, spaceAfter=4,
    )
    styles["body"] = ParagraphStyle(
        "Body",
        fontSize=10, fontName="Helvetica",
        textColor=TEXT, leading=15,
        spaceAfter=6, alignment=TA_JUSTIFY,
    )
    styles["bullet"] = ParagraphStyle(
        "Bullet",
        fontSize=10, fontName="Helvetica",
        textColor=TEXT, leading=14,
        leftIndent=16, spaceAfter=3,
    )
    styles["toc_item"] = ParagraphStyle(
        "TocItem",
        fontSize=10, fontName="Helvetica",
        textColor=PRIMARY, spaceAfter=3, leftIndent=8,
    )
    styles["footer"] = ParagraphStyle(
        "Footer",
        fontSize=8, fontName="Helvetica-Oblique",
        textColor=MUTED, alignment=TA_CENTER,
    )
    return styles


def _parse_markdown_to_story(markdown: str, styles: dict) -> list:
    """
    Parse Markdown text into a list of reportlab Flowable objects.
    Handles: # headings, ## headings, bullet points, horizontal rules, plain text.
    """
    story = []
    lines = markdown.splitlines()
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # Skip empty lines (add small spacer)
        if not line:
            story.append(Spacer(1, 4))
            i += 1
            continue

        # H1 — Title
        if line.startswith("# ") and not line.startswith("## "):
            text = line[2:].strip()
            story.append(Spacer(1, 6))
            story.append(Paragraph(text, styles["title"]))
            story.append(Spacer(1, 4))
            i += 1
            continue

        # H2 — Section heading
        if line.startswith("## ") and not line.startswith("### "):
            text = line[3:].strip()
            # Remove emoji prefix (reportlab can't render them)
            text = re.sub(r"^[^\w\s]+\s*", "", text).strip()
            story.append(Spacer(1, 8))
            story.append(Paragraph(text, styles["h2"]))
            i += 1
            continue

        # H3
        if line.startswith("### "):
            text = line[4:].strip()
            text = re.sub(r"^[^\w\s]+\s*", "", text).strip()
            story.append(Paragraph(text, styles["h3"]))
            i += 1
            continue

        # Horizontal rule
        if line.startswith("---"):
            story.append(Spacer(1, 4))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#D1D5DB")))
            story.append(Spacer(1, 4))
            i += 1
            continue

        # Blockquote (>)
        if line.startswith("> "):
            text = line[2:].strip()
            text = re.sub(r"^[^\w\s]+\s*", "", text).strip()
            story.append(Paragraph(f"<i>{text}</i>", styles["meta"]))
            i += 1
            continue

        # Bullet point (-, *, •)
        if re.match(r"^[-*•]\s+", line):
            text = re.sub(r"^[-*•]\s+", "", line)
            text = _clean_inline(text)
            story.append(Paragraph(f"• {text}", styles["bullet"]))
            i += 1
            continue

        # Numbered list
        if re.match(r"^\d+\.\s+", line):
            text = re.sub(r"^\d+\.\s+", "", line)
            text = _clean_inline(text)
            story.append(Paragraph(f"• {text}", styles["toc_item"]))
            i += 1
            continue

        # Plain paragraph
        text = _clean_inline(line)
        if text:
            story.append(Paragraph(text, styles["body"]))
        i += 1

    return story


def _clean_inline(text: str) -> str:
    """Strip Markdown inline formatting that reportlab can't render."""
    # Bold/italic → keep text
    text = re.sub(r"\*\*\*(.*?)\*\*\*", r"\1", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", text)
    text = re.sub(r"`(.*?)`", r"<i>\1</i>", text)
    # Strip markdown links [text](url) → text
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    # Remove emojis (basic range)
    text = re.sub(r"[^\x00-\x7F]+", "", text).strip()
    return text


def generate_pdf(markdown: str, video_id: str) -> str:
    """
    Convert Markdown document to PDF.

    Args:
        markdown: The full Markdown document string.
        video_id: YouTube video ID (used for filename).

    Returns:
        Relative URL path to the PDF file (e.g. /static/pdfs/abc123.pdf)
    """
    # Ensure output directory exists
    output_dir = Path(PDF_OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    pdf_filename = f"{video_id}.pdf"
    pdf_path = output_dir / pdf_filename

    styles = _build_styles()
    story = _parse_markdown_to_story(markdown, styles)

    # Add footer spacer
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#D1D5DB")))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Generated by YouTube → Document AI Pipeline", styles["footer"]))

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="AI Generated Document",
    )

    doc.build(story)
    logger.info(f"PDF saved to: {pdf_path}")

    return f"/static/pdfs/{pdf_filename}"
