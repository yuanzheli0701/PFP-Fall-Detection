# -*- coding: utf-8 -*-
import sys, io, runpy
sys.stdout.reconfigure(encoding="utf-8")

W = r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\_work"
g1 = runpy.run_path(W + r"\content.py")
g2 = runpy.run_path(W + r"\content2.py")
BLOCKS = g1["BLOCKS"] + g2["BLOCKS2"]

TITLE = "State of the Art 报告 · 中文全译与公式详解"
SUBTITLE = "原文件：State of the art - shared (revu2).docx ｜ 结课项目：基于度量学习的有限多模态数据跌倒检测"
AUTHORS = "Clémence Vergniaud & Yuanzhe Li（李元哲） ｜ 导师：Wafa Njima ｜ 模块 IP. 3510"

# ---------- Markdown ----------
md = []
md.append(f"# {TITLE}\n")
md.append(f"*{SUBTITLE}*\n")
md.append(f"{AUTHORS}\n")
md.append("---\n")
for kind, payload in BLOCKS:
    if kind == "h1":
        md.append(f"\n# {payload}\n")
    elif kind == "h2":
        md.append(f"\n## {payload}\n")
    elif kind == "h3":
        md.append(f"\n### {payload}\n")
    elif kind == "p":
        md.append(payload + "\n")
    elif kind == "bullet":
        md.append("- " + payload + "\n")
    elif kind == "formula":
        md.append(f"\n**公式：** `{payload}`\n")
    elif kind == "note":
        md.append(f"> {payload}\n")
    elif kind == "caption":
        md.append(f"*{payload}*\n")
    elif kind == "table":
        header, rows = payload
        md.append("| " + " | ".join(header) + " |")
        md.append("|" + "|".join([" --- "] * len(header)) + "|")
        for r in rows:
            md.append("| " + " | ".join(str(c) for c in r) + " |")
        md.append("")

md_path = r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\State of the Art 报告-中文全译与公式详解.md"
with open(md_path, "w", encoding="utf-8") as f:
    f.write("\n".join(md))
print("MD written:", md_path)

# ---------- DOCX ----------
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

doc = Document()

# Normal style fonts
st = doc.styles["Normal"]
st.font.name = "Calibri"; st.font.size = Pt(11)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")

def set_run(run, size=None, bold=None, italic=None, color=None, east="微软雅黑"):
    run.font.name = "Calibri"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), east)
    if size: run.font.size = Pt(size)
    if bold is not None: run.font.bold = bold
    if italic is not None: run.font.italic = italic
    if color: run.font.color.rgb = color

def add_heading(text, level):
    p = doc.add_heading("", level=level)
    r = p.add_run(text)
    sizes = {1: 16, 2: 13.5, 3: 12}
    set_run(r, size=sizes.get(level, 12), bold=True, color=RGBColor(0x1F, 0x3B, 0x5C))
    return p

# title page
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_run(p.add_run(TITLE), size=20, bold=True)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_run(p.add_run(SUBTITLE), size=11, italic=True)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_run(p.add_run(AUTHORS), size=10.5)
doc.add_paragraph()

for kind, payload in BLOCKS:
    if kind == "h1":
        add_heading(payload, 1)
    elif kind == "h2":
        add_heading(payload, 2)
    elif kind == "h3":
        add_heading(payload, 3)
    elif kind == "p":
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        set_run(p.add_run(payload))
    elif kind == "bullet":
        p = doc.add_paragraph(style="List Bullet")
        set_run(p.add_run(payload))
    elif kind == "formula":
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(6); p.paragraph_format.space_after = Pt(6)
        set_run(p.add_run(payload), size=12, bold=True, east="Cambria Math")
    elif kind == "note":
        p = doc.add_paragraph(); p.paragraph_format.left_indent = Cm(0.6)
        set_run(p.add_run(payload), size=10.5, italic=True, color=RGBColor(0x60, 0x60, 0x60))
    elif kind == "caption":
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_run(p.add_run(payload), size=10, bold=True, color=RGBColor(0x40, 0x40, 0x40))
    elif kind == "table":
        header, rows = payload
        t = doc.add_table(rows=1 + len(rows), cols=len(header))
        t.style = "Table Grid"
        for j, h in enumerate(header):
            cell = t.cell(0, j)
            cell.text = ""
            set_run(cell.paragraphs[0].add_run(str(h)), size=10, bold=True)
        for i, r in enumerate(rows, start=1):
            for j, c in enumerate(r):
                cell = t.cell(i, j)
                cell.text = ""
                set_run(cell.paragraphs[0].add_run(str(c)), size=10)
        doc.add_paragraph()

docx_path = r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\State of the Art 报告-中文全译与公式详解.docx"
doc.save(docx_path)
print("DOCX written:", docx_path)
