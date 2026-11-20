#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Build the CNN / LSTM summary document.

The document reuses "State of the art - shared.docx" as its template: page setup,
styles, heading numbering, header, footer and the ISEP logo are inherited, while
the body is rebuilt from the blocks defined in scripts/contenu_synthese.py.
Equations are authored in LaTeX and converted to native Word equations (OMML)
with pandoc.

Usage:  python scripts/build_synthese_cnn_lstm.py [--lang zh|en] [--no-word]
"""

from __future__ import annotations

import argparse
import importlib
import io
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from lxml import etree

sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "State of the art - shared.docx"
PANDOC = r"D:\Anaconda\Library\bin\pandoc.exe"

LANGUAGES = {
    "zh": {
        "module": "contenu_synthese",
        "output": ROOT / "Synthese_CNN_LSTM.docx",
        "figures": ROOT / "figures",
        "toc_title": "\u76ee\u5f55",
        "toc_placeholder": "\u5728 Word \u4e2d\u6309 Ctrl+A\uff0c\u518d\u6309 F9 \u5237\u65b0\u76ee\u5f55",
    },
    "en": {
        "module": "contenu_synthese_en",
        "output": ROOT / "Synthese_CNN_LSTM_EN.docx",
        "figures": ROOT / "figures" / "en",
        "toc_title": "Contents",
        "toc_placeholder": "In Word, press Ctrl+A, then F9 to refresh the table of contents",
    },
}
CONFIG = LANGUAGES["zh"]
CONTENU = None
OUTPUT = CONFIG["output"]
FIG_DIR = CONFIG["figures"]


def configure(lang):
    """Select the language: content module, output file and figure directory."""
    global CONFIG, CONTENU, OUTPUT, FIG_DIR
    CONFIG = LANGUAGES[lang]
    CONTENU = importlib.import_module(CONFIG["module"]).CONTENU
    OUTPUT = CONFIG["output"]
    FIG_DIR = CONFIG["figures"]

TEXT_WIDTH_TWIPS = 9072
BODY_FONT = "Arial"
CJK_FONT = "Microsoft YaHei"
MONO_FONT = "Consolas"
CAPTION_COLOR = RGBColor(0x33, 0x33, 0x33)
GREY_TEXT = RGBColor(0x5A, 0x5A, 0x5A)

INLINE_RE = re.compile(r"(\*\*.+?\*\*|`[^`]+`)")


# --------------------------------------------------------------------------
# low level helpers
# --------------------------------------------------------------------------
def set_run_font(run, name=BODY_FONT, size=None, bold=None, italic=None, color=None, cjk=CJK_FONT):
    run.font.name = name
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.get_or_add_rFonts()
    for attr in ("w:ascii", "w:hAnsi", "w:cs"):
        rFonts.set(qn(attr), name)
    rFonts.set(qn("w:eastAsia"), cjk)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    if italic is not None:
        run.font.italic = italic
    if color is not None:
        run.font.color.rgb = color


def add_runs(paragraph, text, size=None, bold=False, color=None, cjk=CJK_FONT):
    """Add text to a paragraph, honouring **bold** and `code` markers."""
    for part in INLINE_RE.split(text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            run = paragraph.add_run(part[2:-2])
            set_run_font(run, size=size, bold=True, color=color, cjk=cjk)
        elif part.startswith("`") and part.endswith("`") and len(part) > 2:
            run = paragraph.add_run(part[1:-1])
            set_run_font(run, name=MONO_FONT, size=(size - 0.5) if size else None, bold=bold, color=color, cjk=cjk)
        else:
            run = paragraph.add_run(part)
            set_run_font(run, size=size, bold=bold, color=color, cjk=cjk)
    return paragraph


def add_tab_stops(paragraph, stops):
    pPr = paragraph._p.get_or_add_pPr()
    tabs = OxmlElement("w:tabs")
    for value, position in stops:
        tab = OxmlElement("w:tab")
        tab.set(qn("w:val"), value)
        tab.set(qn("w:pos"), str(position))
        tabs.append(tab)
    pPr.insert(0, tabs) if not len(pPr) else _insert_in_order(pPr, tabs)


_PPR_ORDER = [
    "w:pStyle", "w:keepNext", "w:keepLines", "w:pageBreakBefore", "w:framePr",
    "w:widowControl", "w:numPr", "w:suppressLineNumbers", "w:pBdr", "w:shd",
    "w:tabs", "w:suppressAutoHyphens", "w:kinsoku", "w:wordWrap",
    "w:overflowPunct", "w:topLinePunct", "w:autoSpaceDE", "w:autoSpaceDN",
    "w:bidi", "w:adjustRightInd", "w:snapToGrid", "w:spacing", "w:ind",
    "w:contextualSpacing", "w:mirrorIndents", "w:suppressOverlap", "w:jc",
    "w:textDirection", "w:textAlignment", "w:textboxTightWrap",
    "w:outlineLvl", "w:divId", "w:cnfStyle", "w:rPr", "w:sectPr", "w:pPrChange",
]


def _insert_in_order(pPr, element):
    """Insert element into pPr respecting the CT_PPr child order."""
    tag = element.tag.split("}")[1]
    index = _PPR_ORDER.index("w:" + tag)
    for child in pPr:
        child_tag = child.tag.split("}")[1]
        if "w:" + child_tag not in _PPR_ORDER:
            continue
        if _PPR_ORDER.index("w:" + child_tag) > index:
            child.addprevious(element)
            return element
    pPr.append(element)
    return element


def set_paragraph_shading(paragraph, fill):
    pPr = paragraph._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    _insert_in_order(pPr, shd)


def set_cell_shading(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tcPr.append(shd)


def keep_with_next(paragraph):
    pPr = paragraph._p.get_or_add_pPr()
    _insert_in_order(pPr, OxmlElement("w:keepNext"))


# --------------------------------------------------------------------------
# document level helpers
# --------------------------------------------------------------------------
def prepare_document():
    """Copy the template and clear its body, keeping styles and section setup."""
    shutil.copy(TEMPLATE, OUTPUT)
    document = Document(OUTPUT)
    body = document.element.body
    for child in list(body.iterchildren()):
        if child.tag != qn("w:sectPr"):
            body.remove(child)

    for name in ("Normal", "Heading 1", "Heading 2", "Heading 3", "List Paragraph", "TOC Heading"):
        try:
            style = document.styles[name]
        except KeyError:
            continue
        font = style.font
        if font.name is None or name in ("Normal", "List Paragraph"):
            font.name = BODY_FONT
        rPr = style.element.get_or_add_rPr()
        rFonts = rPr.get_or_add_rFonts()
        for attr in ("w:ascii", "w:hAnsi", "w:cs"):
            if rFonts.get(qn(attr)) is None:
                rFonts.set(qn(attr), BODY_FONT)
        rFonts.set(qn("w:eastAsia"), CJK_FONT)
    return document


def add_title_page(document, spec):
    logo = None
    with zipfile.ZipFile(TEMPLATE) as archive:
        for name in archive.namelist():
            if name.startswith("word/media/"):
                logo = archive.read(name)
                break

    for _ in range(3):
        document.add_paragraph()
    if logo:
        paragraph = document.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragraph.add_run().add_picture(io.BytesIO(logo), width=Inches(1.91))
    for _ in range(6):
        document.add_paragraph()

    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run(spec["title"])
    set_run_font(run, size=20, bold=True)

    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_runs(paragraph, spec["subtitle"], size=16)

    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_runs(paragraph, spec["module"], size=12)

    for _ in range(7):
        document.add_paragraph()

    for line in (spec["authors"], spec["supervisor"]):
        paragraph = document.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_runs(paragraph, line, size=12)

    for _ in range(2):
        document.add_paragraph()

    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_runs(paragraph, spec["version"], size=12)


def add_toc(document):
    paragraph = document.add_paragraph(style="TOC Heading")
    add_runs(paragraph, CONFIG["toc_title"], size=16)
    paragraph = document.add_paragraph()
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = r' TOC \o "1-3" \h \z \u '
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    run._r.append(begin)
    run._r.append(instr)
    run._r.append(separate)
    placeholder = paragraph.add_run(CONFIG["toc_placeholder"])
    set_run_font(placeholder, size=12, color=GREY_TEXT)
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    paragraph.add_run()._r.append(end)
    document.add_page_break()


def add_heading(document, text, level):
    paragraph = document.add_paragraph(style=f"Heading {level}")
    add_runs(paragraph, text)
    if paragraph.runs:
        set_run_font(paragraph.runs[0], size={1: 16, 2: 14, 3: 12}[level])
    return paragraph


def add_body(document, text, indent=True, size=12, space_after=None, color=None, italic=False):
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if indent:
        paragraph.paragraph_format.first_line_indent = Inches(0.25)
    if space_after is not None:
        paragraph.paragraph_format.space_after = Pt(space_after)
    add_runs(paragraph, text, size=size, color=color)
    if italic:
        for run in paragraph.runs:
            run.font.italic = True
    return paragraph


def add_list(document, items, marker="•"):
    for item in items:
        paragraph = document.add_paragraph()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        paragraph.paragraph_format.left_indent = Inches(0.3)
        paragraph.paragraph_format.first_line_indent = Inches(-0.3)
        add_tab_stops(paragraph, [("left", 432)])
        run = paragraph.add_run(marker + "\t")
        set_run_font(run, size=12)
        add_runs(paragraph, item, size=12)


def add_code(document, code):
    lines = code.strip("\n").split("\n")
    for index, line in enumerate(lines):
        paragraph = document.add_paragraph()
        paragraph.paragraph_format.space_before = Pt(3 if index == 0 else 0)
        paragraph.paragraph_format.space_after = Pt(3 if index == len(lines) - 1 else 0)
        paragraph.paragraph_format.line_spacing = 1.0
        paragraph.paragraph_format.left_indent = Inches(0.12)
        set_paragraph_shading(paragraph, "F5F7FA")
        run = paragraph.add_run(line if line.strip() else " ")
        set_run_font(run, name=MONO_FONT, size=9.5, cjk=CJK_FONT)


def add_figure(document, filename, caption, width_inches):
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_before = Pt(8)
    paragraph.paragraph_format.space_after = Pt(4)
    keep_with_next(paragraph)
    paragraph.add_run().add_picture(str(FIG_DIR / filename), width=Inches(width_inches))
    caption_paragraph = document.add_paragraph()
    caption_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption_paragraph.paragraph_format.space_after = Pt(12)
    add_runs(caption_paragraph, caption, size=10.5, bold=True, color=CAPTION_COLOR)


def add_table(document, caption, rows, widths=None, font_size=10.5):
    table = document.add_table(rows=len(rows), cols=len(rows[0]))
    table.style = document.styles["Table Grid"]
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    trPr = table.rows[0]._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    trPr.append(tbl_header)
    for row_index, row in enumerate(rows):
        for col_index, value in enumerate(row):
            cell = table.cell(row_index, col_index)
            cell.text = ""
            paragraph = cell.paragraphs[0]
            paragraph.paragraph_format.space_before = Pt(2)
            paragraph.paragraph_format.space_after = Pt(2)
            paragraph.paragraph_format.line_spacing = 1.0
            add_runs(paragraph, str(value), size=font_size, bold=(row_index == 0))
            if row_index == 0:
                set_cell_shading(cell, "EDF2F7")
            if widths:
                cell.width = Inches(widths[col_index])
    caption_paragraph = document.add_paragraph()
    caption_paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    caption_paragraph.paragraph_format.space_before = Pt(4)
    caption_paragraph.paragraph_format.space_after = Pt(12)
    add_runs(caption_paragraph, caption, size=10.5, bold=True, color=CAPTION_COLOR)


def add_equation(document, omml_xml, number):
    paragraph = document.add_paragraph()
    pPr = paragraph._p.get_or_add_pPr()
    tabs = OxmlElement("w:tabs")
    for value, position in (("center", TEXT_WIDTH_TWIPS // 2), ("right", TEXT_WIDTH_TWIPS)):
        tab = OxmlElement("w:tab")
        tab.set(qn("w:val"), value)
        tab.set(qn("w:pos"), str(position))
        tabs.append(tab)
    _insert_in_order(pPr, tabs)
    spacing = OxmlElement("w:spacing")
    spacing.set(qn("w:before"), "140")
    spacing.set(qn("w:after"), "140")
    _insert_in_order(pPr, spacing)

    run = paragraph.add_run()
    set_run_font(run, size=12)
    run.add_tab()
    paragraph._p.append(etree.fromstring(omml_xml))
    run = paragraph.add_run()
    set_run_font(run, size=12)
    run.add_tab()
    run.add_text(f"({number})")


# --------------------------------------------------------------------------
# equations: LaTeX -> OMML through pandoc
# --------------------------------------------------------------------------
def latex_to_omml(equations):
    workdir = Path(tempfile.mkdtemp(prefix="omml_"))
    markdown = workdir / "equations.md"
    markdown.write_text("\n\n".join(f"${tex}$" for tex in equations), encoding="utf-8")
    docx_path = workdir / "equations.docx"
    subprocess.run(
        [PANDOC, str(markdown), "-o", str(docx_path), "--from", "markdown", "--to", "docx"],
        check=True,
        capture_output=True,
    )
    with zipfile.ZipFile(docx_path) as archive:
        xml = archive.read("word/document.xml")
    tree = etree.fromstring(xml)
    math_ns = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
    word_ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    found = []
    for paragraph in tree.iter(word_ns + "p"):
        for element in paragraph.findall(math_ns + "oMath"):
            found.append(etree.tostring(element, encoding="unicode"))
    if len(found) != len(equations):
        raise RuntimeError(f"pandoc returned {len(found)} equations for {len(equations)} inputs")
    return found


# --------------------------------------------------------------------------
# assembly
# --------------------------------------------------------------------------
def build(update_toc=True):
    document = prepare_document()

    equations = [block[1][0] for block in CONTENU if block[0] == "eq"]
    omml = latex_to_omml(equations)
    equation_iter = iter(omml)

    for kind, payload in CONTENU:
        if kind == "titlepage":
            add_title_page(document, payload)
        elif kind == "toc":
            add_toc(document)
        elif kind == "h1":
            add_heading(document, payload, 1)
        elif kind == "h2":
            add_heading(document, payload, 2)
        elif kind == "h3":
            add_heading(document, payload, 3)
        elif kind == "p":
            add_body(document, payload)
        elif kind == "note":
            add_body(document, payload, size=11, color=GREY_TEXT, space_after=6)
        elif kind == "bul":
            add_list(document, payload, marker="•")
        elif kind == "num":
            add_list(document, payload, marker="–")
        elif kind == "eq":
            add_equation(document, next(equation_iter), payload[1])
        elif kind == "fig":
            add_figure(document, *payload)
        elif kind == "tbl":
            add_table(document, *payload)
        elif kind == "code":
            add_code(document, payload)
        elif kind == "refs":
            for item in payload:
                paragraph = document.add_paragraph(style="List Paragraph")
                paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                paragraph.paragraph_format.left_indent = Inches(0.35)
                paragraph.paragraph_format.first_line_indent = Inches(-0.35)
                paragraph.paragraph_format.space_after = Pt(6)
                add_runs(paragraph, item, size=11)
        elif kind == "pagebreak":
            document.add_page_break()
        else:
            raise ValueError(f"unknown block type: {kind}")

    document.save(OUTPUT)
    print(f"wrote {OUTPUT}")
    if update_toc:
        update_fields()


def update_fields():
    """Ask Word to build the table of contents and repaginate."""
    try:
        import win32com.client  # noqa: PLC0415
    except ImportError:
        print("pywin32 unavailable: the table of contents stays unbuilt")
        return
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = False
    try:
        document = word.Documents.Open(str(OUTPUT))
        for toc in document.TablesOfContents:
            toc.Update()
        document.Fields.Update()
        document.Repaginate()
        document.Save()
        document.Close(False)
        print("table of contents updated")
    finally:
        word.Quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", choices=["zh", "en"], default="zh", help="document language")
    parser.add_argument("--no-word", action="store_true", help="skip the Word field update")
    arguments = parser.parse_args()
    configure(arguments.lang)
    build(update_toc=not arguments.no_word)
