#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Build a print-ready bilingual QUIDA progress speech PDF."""

from __future__ import annotations

import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "reports" / "QUIDA_Progress_Speech_Script_EN_CN_2026-11-05.md"
OUTPUT = ROOT / "output" / "pdf" / "QUIDA_Progress_Speech_Script_EN_CN_2026-11-05.pdf"
PREVIEW = ROOT / "_work" / "speech_pdf" / "preview"

PAGE_W, PAGE_H = A4
BG = colors.HexColor("#F7FBFF")
WHITE = colors.white
NAVY = colors.HexColor("#0B1F33")
BLUE = colors.HexColor("#2563EB")
SKY = colors.HexColor("#0EA5E9")
CYAN = colors.HexColor("#0891B2")
TEXT = colors.HexColor("#122A40")
MUTED = colors.HexColor("#587089")
FAINT = colors.HexColor("#8298AD")
PALE = colors.HexColor("#EEF7FF")
PALE_2 = colors.HexColor("#E4F2FF")
BORDER = colors.HexColor("#CBDFF0")
AMBER = colors.HexColor("#D97706")


def register_fonts() -> None:
    fonts = {
        "SegoeUI": r"C:\Windows\Fonts\segoeui.ttf",
        "SegoeUIBold": r"C:\Windows\Fonts\segoeuib.ttf",
        "CJK": r"C:\Windows\Fonts\Deng.ttf",
        "CJKBold": r"C:\Windows\Fonts\Dengb.ttf",
    }
    for name, path in fonts.items():
        pdfmetrics.registerFont(TTFont(name, path))
    pdfmetrics.registerFontFamily(
        "SegoeUI", normal="SegoeUI", bold="SegoeUIBold", italic="SegoeUI", boldItalic="SegoeUIBold"
    )
    pdfmetrics.registerFontFamily(
        "CJK", normal="CJK", bold="CJKBold", italic="CJK", boldItalic="CJKBold"
    )


def clean_paragraph(text: str) -> str:
    text = " ".join(line.strip() for line in text.strip().splitlines() if line.strip())
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = text.replace("`", "")
    return text


def extract_between(text: str, start: str, end: str) -> str:
    if start not in text or end not in text:
        raise ValueError(f"Missing section: {start!r} or {end!r}")
    return text.split(start, 1)[1].split(end, 1)[0]


def parse_english(section: str) -> list[dict]:
    pattern = re.compile(
        r"### Slide (\d+) — (.+?) \| about (\d+) seconds\s*\n(.*?)(?=\n### Slide|\Z)", re.S
    )
    items = []
    for number, title, seconds, body in pattern.findall(section):
        items.append(
            {"number": int(number), "title": title.strip(), "seconds": int(seconds), "body": clean_paragraph(body)}
        )
    if len(items) != 13:
        raise ValueError(f"Expected 13 English slides, found {len(items)}")
    return items


def parse_chinese(section: str) -> list[dict]:
    pattern = re.compile(r"### 第 (\d+) 页：(.+?)\s*\n(.*?)(?=\n### 第|\Z)", re.S)
    items = []
    for number, title, body in pattern.findall(section):
        items.append({"number": int(number), "title": title.strip(), "body": clean_paragraph(body)})
    if len(items) != 13:
        raise ValueError(f"Expected 13 Chinese slides, found {len(items)}")
    return items


def parse_qa(section: str) -> list[dict]:
    pattern = re.compile(r"### (\d+)\. (.+?)\s*\n(.*?)(?=\n### \d+\.|\Z)", re.S)
    return [
        {"number": int(number), "question": title.strip(), "answer": clean_paragraph(body)}
        for number, title, body in pattern.findall(section)
    ]


def parse_tips(section: str) -> list[str]:
    tips = []
    for line in section.splitlines():
        if line.startswith("- "):
            tips.append(clean_paragraph(line[2:]))
    return tips


def make_styles() -> dict[str, ParagraphStyle]:
    return {
        "cover_kicker": ParagraphStyle(
            "cover_kicker", fontName="SegoeUIBold", fontSize=8, leading=10, textColor=BLUE,
            spaceAfter=8,
        ),
        "cover_title": ParagraphStyle(
            "cover_title", fontName="SegoeUIBold", fontSize=32, leading=36, textColor=NAVY,
            spaceAfter=10,
        ),
        "cover_sub": ParagraphStyle(
            "cover_sub", fontName="SegoeUI", fontSize=15, leading=22, textColor=MUTED,
            spaceAfter=8,
        ),
        "cover_desc": ParagraphStyle(
            "cover_desc", fontName="SegoeUI", fontSize=10.5, leading=16, textColor=TEXT,
        ),
        "badge": ParagraphStyle(
            "badge", fontName="SegoeUIBold", fontSize=7.5, leading=9, textColor=BLUE,
            alignment=TA_LEFT,
        ),
        "box_label": ParagraphStyle(
            "box_label", fontName="SegoeUIBold", fontSize=7.5, leading=9, textColor=BLUE,
            spaceAfter=4,
        ),
        "box_text": ParagraphStyle(
            "box_text", fontName="SegoeUI", fontSize=10, leading=15, textColor=TEXT,
        ),
        "section_title": ParagraphStyle(
            "section_title", fontName="SegoeUIBold", fontSize=18, leading=22, textColor=NAVY,
        ),
        "section_sub": ParagraphStyle(
            "section_sub", fontName="SegoeUI", fontSize=9, leading=12, textColor=MUTED,
        ),
        "cn_section_title": ParagraphStyle(
            "cn_section_title", fontName="CJKBold", fontSize=18, leading=22, textColor=NAVY,
            wordWrap="CJK",
        ),
        "cn_section_sub": ParagraphStyle(
            "cn_section_sub", fontName="CJK", fontSize=9, leading=12, textColor=MUTED,
            wordWrap="CJK",
        ),
        "slide_label": ParagraphStyle(
            "slide_label", fontName="SegoeUIBold", fontSize=7.2, leading=9, textColor=BLUE,
            spaceAfter=2,
        ),
        "slide_title": ParagraphStyle(
            "slide_title", fontName="SegoeUIBold", fontSize=11.2, leading=14, textColor=NAVY,
            spaceAfter=3,
        ),
        "eng_body": ParagraphStyle(
            "eng_body", fontName="SegoeUI", fontSize=9.55, leading=14.2, textColor=TEXT,
            alignment=TA_LEFT,
        ),
        "cn_label": ParagraphStyle(
            "cn_label", fontName="CJKBold", fontSize=7.8, leading=10, textColor=BLUE,
            spaceAfter=2, wordWrap="CJK",
        ),
        "cn_title": ParagraphStyle(
            "cn_title", fontName="CJKBold", fontSize=11.8, leading=15, textColor=NAVY,
            spaceAfter=3, wordWrap="CJK",
        ),
        "cn_body": ParagraphStyle(
            "cn_body", fontName="CJK", fontSize=10.0, leading=17.0, textColor=TEXT,
            alignment=TA_LEFT, wordWrap="CJK",
        ),
        "qa_question": ParagraphStyle(
            "qa_question", fontName="SegoeUIBold", fontSize=10, leading=13, textColor=NAVY,
            spaceAfter=3,
        ),
        "qa_answer": ParagraphStyle(
            "qa_answer", fontName="SegoeUI", fontSize=9.2, leading=13.2, textColor=TEXT,
        ),
        "tip": ParagraphStyle(
            "tip", fontName="SegoeUI", fontSize=9.2, leading=13.4, textColor=TEXT,
            leftIndent=14, firstLineIndent=-9, spaceAfter=3,
        ),
        "footer": ParagraphStyle(
            "footer", fontName="SegoeUI", fontSize=7, leading=9, textColor=FAINT,
        ),
        "footer_right": ParagraphStyle(
            "footer_right", fontName="SegoeUI", fontSize=7, leading=9, textColor=FAINT,
            alignment=TA_RIGHT,
        ),
    }


def draw_cover(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFillColor(BG)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canvas.setFillColor(PALE)
    canvas.circle(PAGE_W - 18 * mm, PAGE_H - 30 * mm, 72 * mm, fill=1, stroke=0)
    canvas.setFillColor(PALE_2)
    canvas.circle(PAGE_W - 16 * mm, PAGE_H - 34 * mm, 50 * mm, fill=1, stroke=0)
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.5)
    for radius in (30 * mm, 43 * mm, 58 * mm):
        canvas.circle(PAGE_W - 25 * mm, PAGE_H - 45 * mm, radius, fill=0, stroke=1)
    canvas.setFillColor(BLUE)
    canvas.rect(18 * mm, PAGE_H - 22 * mm, 24 * mm, 2.2 * mm, fill=1, stroke=0)
    canvas.restoreState()


def draw_content(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFillColor(WHITE)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canvas.setFillColor(BLUE)
    canvas.rect(15 * mm, PAGE_H - 13.2 * mm, 3.2 * mm, 1.6 * mm, fill=1, stroke=0)
    canvas.setFont("SegoeUIBold", 6.8)
    canvas.setFillColor(MUTED)
    canvas.drawString(21 * mm, PAGE_H - 12.4 * mm, "QUIDA / DATA CLEANING & PRELIMINARY BASELINES")
    canvas.drawRightString(PAGE_W - 15 * mm, PAGE_H - 12.4 * mm, "SIMPLE SPEECH SCRIPT")
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.4)
    canvas.line(15 * mm, PAGE_H - 15.5 * mm, PAGE_W - 15 * mm, PAGE_H - 15.5 * mm)
    canvas.line(15 * mm, 14.2 * mm, PAGE_W - 15 * mm, 14.2 * mm)
    canvas.setFont("SegoeUI", 6.8)
    canvas.setFillColor(FAINT)
    canvas.drawString(15 * mm, 9.6 * mm, "QUIDA progress report  ·  5-6 minutes  ·  preliminary results only")
    canvas.drawRightString(PAGE_W - 15 * mm, 9.6 * mm, f"{doc.page:02d}")
    canvas.restoreState()


def section_banner(title: str, subtitle: str, styles: dict[str, ParagraphStyle], chinese: bool = False):
    body = Paragraph(title, styles["cn_section_title" if chinese else "section_title"])
    sub = Paragraph(subtitle, styles["cn_section_sub" if chinese else "section_sub"])
    table = Table([[body], [sub]], colWidths=[170 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PALE),
                ("LINEBEFORE", (0, 0), (0, -1), 3.2, BLUE),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (0, 0), 11),
                ("BOTTOMPADDING", (0, 0), (0, 0), 2),
                ("TOPPADDING", (0, 1), (0, 1), 1),
                ("BOTTOMPADDING", (0, 1), (0, 1), 10),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    return KeepTogether([table, Spacer(1, 7 * mm)])


def slide_block(item: dict, styles: dict[str, ParagraphStyle], chinese: bool = False):
    if chinese:
        label = Paragraph(f"第 {item['number']:02d} 页  /  中文汇报版", styles["cn_label"])
        title = Paragraph(item["title"], styles["cn_title"])
        body = Paragraph(item["body"], styles["cn_body"])
    else:
        label = Paragraph(
            f"SLIDE {item['number']:02d}  /  {item['seconds']} SEC", styles["slide_label"]
        )
        title = Paragraph(item["title"], styles["slide_title"])
        body = Paragraph(item["body"], styles["eng_body"])
    rule = HRFlowable(width="100%", thickness=0.45, color=BORDER, spaceBefore=4, spaceAfter=6)
    return KeepTogether([label, title, body, rule])


def info_box(label: str, text: str, styles: dict[str, ParagraphStyle], accent=BLUE, background=PALE):
    left = Paragraph(label, styles["box_label"])
    body = Paragraph(text, styles["box_text"])
    table = Table([[left], [body]], colWidths=[170 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), background),
                ("LINEBEFORE", (0, 0), (0, -1), 3.2, accent),
                ("LEFTPADDING", (0, 0), (-1, -1), 11),
                ("RIGHTPADDING", (0, 0), (-1, -1), 11),
                ("TOPPADDING", (0, 0), (0, 0), 9),
                ("BOTTOMPADDING", (0, 0), (0, 0), 2),
                ("TOPPADDING", (0, 1), (0, 1), 1),
                ("BOTTOMPADDING", (0, 1), (0, 1), 9),
            ]
        )
    )
    return table


def build() -> None:
    register_fonts()
    styles = make_styles()
    text = SOURCE.read_text(encoding="utf-8")
    english = parse_english(extract_between(text, "## A. English Delivery Script", "## B. 中文汇报版"))
    chinese = parse_chinese(extract_between(text, "## B. 中文汇报版", "## C. Short Answers for Likely Questions"))
    qa = parse_qa(extract_between(text, "## C. Short Answers for Likely Questions", "## D. Delivery Tips"))
    tips = parse_tips(text.split("## D. Delivery Tips", 1)[1])

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    PREVIEW.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=18 * mm,
        title="QUIDA Progress Report - Simple Speech Script",
        author="QUIDA project",
        subject="Data cleaning and preliminary fall-detection baselines",
    )
    cover_frame = Frame(18 * mm, 18 * mm, PAGE_W - 36 * mm, PAGE_H - 36 * mm, id="cover-frame")
    content_frame = Frame(20 * mm, 18 * mm, PAGE_W - 40 * mm, PAGE_H - 37 * mm, id="content-frame")
    doc.addPageTemplates(
        [
            PageTemplate(id="cover", frames=[cover_frame], onPage=draw_cover),
            PageTemplate(id="content", frames=[content_frame], onPage=draw_content),
        ]
    )

    story = [
        Spacer(1, 14 * mm),
        Paragraph("QUIDA / PFP 2026", styles["cover_kicker"]),
        Paragraph("Simple Speech Script", styles["cover_title"]),
        Paragraph("Data cleaning and preliminary fall-detection baselines", styles["cover_sub"]),
        Spacer(1, 4 * mm),
        HRFlowable(width=38 * mm, thickness=2.4, color=BLUE, hAlign="LEFT", spaceAfter=8),
        Paragraph(
            "A concise progress report for the professor: what we completed, what we found, and where the remaining risks are.",
            styles["cover_desc"],
        ),
        Spacer(1, 9 * mm),
    ]
    badges = Table(
        [[
            Paragraph("5-6 MIN", styles["badge"]),
            Paragraph("13 SLIDES", styles["badge"]),
            Paragraph("EN + CN", styles["badge"]),
        ]],
        colWidths=[38 * mm, 38 * mm, 40 * mm],
        rowHeights=[10 * mm],
    )
    badges.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PALE),
                ("BOX", (0, 0), (-1, -1), 0.6, BORDER),
                ("INNERGRID", (0, 0), (-1, -1), 0.6, BORDER),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
            ]
        )
    )
    story += [badges, Spacer(1, 10 * mm)]
    story += [
        info_box(
            "CORE MESSAGE",
            "The data foundation is ready. The model scores validate the pipeline, but they are not yet a final generalisation claim.",
            styles,
        ),
        Spacer(1, 7 * mm),
        info_box(
            "DELIVERY RULE",
            "Keep it simple. Focus on progress and problems, not on every number. Say clearly that the results are preliminary.",
            styles,
            accent=CYAN,
            background=colors.HexColor("#F2FBFC"),
        ),
        Spacer(1, 8 * mm),
        HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceAfter=5),
        Paragraph(
            "INSIDE  /  English script  ·  Chinese script  ·  Likely questions  ·  Delivery tips",
            styles["section_sub"],
        ),
        Spacer(1, 9 * mm),
        Paragraph("Prepared 5 November 2026  ·  Companion deck: QUIDA_Data_Cleaning_EN_WhiteBlue.pptx", styles["cover_desc"]),
        NextPageTemplate("content"),
        PageBreak(),
        section_banner("A / ENGLISH DELIVERY SCRIPT", "Approx. 5-6 minutes  ·  Speak slowly and pause after the key numbers", styles),
        info_box(
            "HOW TO USE THIS SCRIPT",
            "Do not read every number. Emphasise the cleaned dataset, the independent QA, and the preliminary nature of the model results.",
            styles,
        ),
        Spacer(1, 5 * mm),
    ]
    for index, item in enumerate(english, start=1):
        story.append(slide_block(item, styles))
        if index == 7:
            story.append(PageBreak())
    story += [
        PageBreak(),
        section_banner("B / 中文汇报版", "建议 5-6 分钟  ·  与英文讲稿逐页对应", styles, chinese=True),
    ]
    for index, item in enumerate(chinese, start=1):
        story.append(slide_block(item, styles, chinese=True))
        if index == 7:
            story.append(PageBreak())
    story += [
        PageBreak(),
        section_banner("C / LIKELY QUESTIONS", "Short answers to keep the discussion focused", styles),
    ]
    for item in qa:
        block = KeepTogether(
            [
                Paragraph(f"{item['number']:02d}  /  {item['question']}", styles["qa_question"]),
                Paragraph(item["answer"], styles["qa_answer"]),
                Spacer(1, 5 * mm),
            ]
        )
        story.append(block)
    story += [
        Spacer(1, 4 * mm),
        section_banner("D / DELIVERY TIPS", "Small cues that make the report sound clear and confident", styles),
    ]
    for index, tip in enumerate(tips, start=1):
        story.append(Paragraph(f"{index}.  {tip}", styles["tip"]))

    doc.build(story)
    print(OUTPUT)


if __name__ == "__main__":
    build()
