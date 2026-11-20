# -*- coding: utf-8 -*-
import sys, zipfile, runpy
import lxml.etree as ET
sys.stdout.reconfigure(encoding="utf-8")

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
qn = lambda t: "{%s}%s" % (W, t)
qnm = lambda t: "{%s}%s" % (M, t)
SRC = r"C:\Users\13968\Downloads\State of the art v2.docx"
WDIR = r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\_work"

C = runpy.run_path(WDIR + r"\v2_content.py")
TR, EQ_EXPLAIN, SMALL_NOTES, TABLE_CN, REF_GLOSS = C["TR"], C["EQ_EXPLAIN"], C["SMALL_NOTES"], C["TABLE_CN"], C["REF_GLOSS"]

NUM = {27:"Ⅰ", 37:"Ⅱ", 57:"Ⅲ", 74:"Ⅳ", 111:"Ⅴ", 119:"Ⅵ", 138:"Ⅶ",
       40:"Ⅱ.1", 43:"Ⅱ.2", 47:"Ⅱ.3", 60:"Ⅲ.1", 64:"Ⅲ.2", 68:"Ⅲ.3",
       75:"Ⅳ.1", 79:"Ⅳ.2", 84:"Ⅳ.3", 89:"Ⅳ.4", 108:"Ⅳ.5",
       92:"Ⅳ.4.a", 95:"Ⅳ.4.b", 103:"Ⅳ.4.c", 125:"Ⅵ.1", 131:"Ⅵ.2"}
FORMULA = {81: "L = y·d² + (1 − y)·max(0, m − d)²",
           86: "L = max(0, ‖f(a) − f(p)‖² − ‖f(a) − f(n)‖² + α)",
           97: "c_k = (1/|S_k|) · Σ_{x_i ∈ S_k} f(x_i)"}

# ---------- parse v2 into ordered blocks ----------
z = zipfile.ZipFile(SRC)
root = ET.fromstring(z.read("word/document.xml"))
body = root.find(qn("body"))

def ptext(p):
    return "".join(t.text or "" for t in p.iter(qn("t"))).strip()

def tbl_rows(tbl):
    rows = []
    for tr in tbl.findall(qn("tr")):
        cells = []
        for tc in tr.findall(qn("tc")):
            cells.append(" ".join(ptext(p) for p in tc.findall(qn("p"))).strip())
        rows.append(cells)
    return rows

blocks = []
pi = 0
ti = 0
for child in body:
    if child.tag == qn("p"):
        sty = ""
        pPr = child.find(qn("pPr"))
        if pPr is not None:
            s = pPr.find(qn("pStyle"))
            if s is not None: sty = s.get(qn("val"))
        txt = ptext(child)
        has_math = child.find(".//" + qnm("oMathPara")) is not None or child.find(".//" + qnm("oMath")) is not None
        if txt or has_math:
            blocks.append(("p", pi, txt, sty, has_math))
        pi += 1
    elif child.tag == qn("tbl"):
        blocks.append(("tbl", ti, tbl_rows(child)))
        ti += 1
# drop cover paragraphs 10-25 (handled separately) and references handled normally
print("blocks:", len(blocks))

# ---------- DOCX ----------
from docx import Document
from docx.enum.text import WD_BREAK
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn as dqn
from docx.oxml import OxmlElement

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(1.8)
sec.top_margin = sec.bottom_margin = Cm(1.8)
st = doc.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(9.5)
st.element.rPr.rFonts.set(dqn("w:eastAsia"), "微软雅黑")

def sr(run, size=9.5, bold=None, italic=None, color=None, east="微软雅黑", en="Calibri"):
    run.font.name = en
    run._element.rPr.rFonts.set(dqn("w:eastAsia"), east)
    run.font.size = Pt(size)
    if bold is not None: run.font.bold = bold
    if italic is not None: run.font.italic = italic
    if color: run.font.color.rgb = color

def set_borders(tbl):
    tblPr = tbl._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge, val, sz, col in [("top","none","0","auto"),("left","none","0","auto"),("bottom","none","0","auto"),
                                ("right","none","0","auto"),("insideH","none","0","auto"),
                                ("insideV","single","4","BFBFBF")]:
        el = OxmlElement("w:" + edge); el.set(dqn("w:val"), val); el.set(dqn("w:sz"), sz); el.set(dqn("w:color"), col)
        borders.append(el)
    tblPr.append(borders)

tbl = doc.add_table(rows=0, cols=2)
tbl.autofit = False
set_borders(tbl)
CW = Cm(8.6)

def cell_w(cell):
    cell.width = CW

def add_row():
    row = tbl.add_row()
    for cell in row.cells:
        cell_w(cell)
    return row

def add_merged_row():
    row = tbl.add_row()
    c = row.cells[0].merge(row.cells[1])
    c.width = Cm(17.2)
    return c

def para(cell, text, **kw):
    p = cell.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    if text:
        sr(p.add_run(text), **kw)
    return p

def set_cell_margins(cell, top=40, bottom=40, left=60, right=60):
    tcPr = cell._tc.get_or_add_tcPr()
    mar = OxmlElement("w:tcMar")
    for tag, val in [("top", top), ("bottom", bottom), ("start", left), ("end", right)]:
        el = OxmlElement("w:" + tag); el.set(dqn("w:w"), str(val)); el.set(dqn("w:type"), "dxa"); mar.append(el)
    tcPr.append(mar)

# title row
c = add_merged_row()
p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
sr(p.add_run("Fall Detection through Metric Learning on Limited Multimodal Data"), size=15, bold=True)
p2 = c.add_paragraph(); p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
sr(p2.add_run("基于度量学习的有限多模态数据跌倒检测"), size=13, bold=True)
p3 = c.add_paragraph(); p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
sr(p3.add_run("中英对照版 · State of the Art v2 ｜ 汇报人：Clémence Vergniaud & Yuanzhe Li（李元哲） ｜ 导师：Wafa Njima ｜ 模块 IP. 3510 ｜ 版本 1.2"), size=8.5, color=RGBColor(0x60,0x60,0x60))

# note row
c = add_merged_row()
para(c, "本版说明：左栏为英文原文逐段照录（v2），右栏为中文翻译。3 个显示公式（Ⅳ.2 / Ⅳ.3 / Ⅳ.4.b）与全部段内小式子均在原位给出中文详解；文末附「公式索引表」。", size=8.5, italic=True, color=RGBColor(0x70,0x70,0x70))

# contents row
c = add_merged_row()
para(c, "目录 Contents：Ⅰ 引言 Introduction ｜ Ⅱ 传感模态 Sensing modalities ｜ Ⅲ 监督深度学习 Supervised deep learning ｜ Ⅳ 度量学习 Metric learning ｜ Ⅴ 多模态融合 Sensor fusion ｜ Ⅵ 方法与评估方法选择 Synthesis & choices ｜ Ⅶ 参考文献 References ｜ 附 公式索引 Formula index", size=8.5, bold=True, color=RGBColor(0x1F,0x3B,0x5C))

for blk in blocks:
    if blk[0] == "tbl":
        ti, rows = blk[1], blk[2]
        c = add_merged_row()
        para(c, "英文原表 / English table:", size=8.5, bold=True, color=RGBColor(0x1F,0x3B,0x5C))
        et = c.add_table(rows=len(rows), cols=len(rows[0])); et.style = "Table Grid"
        for i, r in enumerate(rows):
            for j, v in enumerate(r):
                cell2 = et.cell(i, j); cell2.text = ""
                pr = cell2.paragraphs[0]; pr.paragraph_format.space_after = Pt(0)
                sr(pr.add_run(v), size=8, bold=(i == 0))
        para(c, "中文翻译（表）：", size=8.5, bold=True, color=RGBColor(0x1F,0x3B,0x5C))
        header, cnrows = TABLE_CN[ti]
        ct = c.add_table(rows=len(cnrows)+1, cols=len(header)); ct.style = "Table Grid"
        for j, v in enumerate(header):
            cell2 = ct.cell(0, j); cell2.text = ""
            pr = cell2.paragraphs[0]; pr.paragraph_format.space_after = Pt(0)
            sr(pr.add_run(v), size=8, bold=True)
        for i, r in enumerate(cnrows, start=1):
            for j, v in enumerate(r):
                cell2 = ct.cell(i, j); cell2.text = ""
                pr = cell2.paragraphs[0]; pr.paragraph_format.space_after = Pt(0)
                sr(pr.add_run(v), size=8)
        continue

    _, pi, txt, sty, has_math = blk
    if pi in (10, 11, 12, 21, 22, 25):
        continue  # cover handled
    if pi in FORMULA:  # formula rows: left formula, right explanation
        row = add_row()
        left, right = row.cells[0], row.cells[1]
        set_cell_margins(left); set_cell_margins(right)
        p = left.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(6); p.paragraph_format.space_after = Pt(6)
        sr(p.add_run(FORMULA[pi]), size=11.5, bold=True, en="Cambria Math")
        expl = EQ_EXPLAIN[pi]
        first = True
        for line in expl:
            pp = right.paragraphs[0] if first else right.add_paragraph()
            first = False
            pp.paragraph_format.space_after = Pt(1)
            sr(pp.add_run(line), size=8.5, bold=line.startswith("【"), color=(RGBColor(0x8B,0x1A,0x1A) if line.startswith("【") else None))
        continue
    if sty in ("Titre1", "Titre2", "Titre3"):
        num = NUM.get(pi, "")
        cn = TR.get(pi, txt)
        cn_name = cn.split(" ", 1)[1] if " " in cn else cn
        c = add_merged_row()
        para(c, f"{num}. {txt}　｜　{cn_name}", size=(12.5 if sty=="Titre1" else 11 if sty=="Titre2" else 10.5), bold=True, color=RGBColor(0x1F,0x3B,0x5C))
        continue
    if not txt:
        continue
    if pi in TR or pi in REF_GLOSS:
        row = add_row()
        left, right = row.cells[0], row.cells[1]
        set_cell_margins(left); set_cell_margins(right)
        p = left.paragraphs[0]; p.paragraph_format.space_after = Pt(2)
        sr(p.add_run(txt), size=9)
        cn = TR.get(pi, REF_GLOSS.get(pi, ""))
        p = right.paragraphs[0]; p.paragraph_format.space_after = Pt(2)
        sr(p.add_run(cn), size=9)
        if pi in SMALL_NOTES:
            pp = right.add_paragraph(); pp.paragraph_format.space_after = Pt(2)
            sr(pp.add_run(SMALL_NOTES[pi]), size=8, italic=True, color=RGBColor(0x8B,0x5A,0x00))
        continue
    print("SKIP untranslated P%d: %s" % (pi, txt[:60]))

# formula index appendix: top-level block on its own page (header row repeats)
doc.add_paragraph()
_pb = doc.add_paragraph()
_pb.add_run().add_break(WD_BREAK.PAGE)
_h = doc.add_paragraph()
sr(_h.add_run("附录 · 公式索引表 Formula Index（公式 ↔ 位置 ↔ 一句话含义）"), size=12, bold=True, color=RGBColor(0x1F,0x3B,0x5C))
idx_header = ["公式", "位置（章节 / 段落）", "一句话含义"]
idx_rows = [
    ["①  L = y·d² + (1 − y)·max(0, m − d)²", "Ⅳ.2 孪生网络与对比损失（P81）", "同类拉近（d²）、异类推远到间隔 m 为止"],
    ["②  L = max(0, ‖f(a)−f(p)‖² − ‖f(a)−f(n)‖² + α)", "Ⅳ.3 三元组网络与三元组损失（P86）", "锚点离正样本至少比离负样本近 α（相对约束）"],
    ["③  c_k = (1/|S_k|)·Σ f(x_i)", "Ⅳ.4.b 基于原型的分类（P97）", "类原型 = 该类参考嵌入的均值；按最近原型分类"],
    ["④  K×C + 1", "Ⅲ.1 基于 CNN 的方法（P62）", "单个卷积滤波器的权重数（核长×通道+1 偏置）"],
    ["⑤  K−1；2(K−1)", "Ⅲ.1（P62）", "感受野每层增量；过步长-2 池化后增量翻倍"],
    ["⑥  N²/2（N² 量级）", "Ⅳ.1 原理（P77）", "N 个样本可组成的样本对数量级"],
    ["⑦  P×K", "Ⅳ.3（P87）", "每批 P 类 × 每类 K 样本的平衡采样"],
    ["⑧  c_t = f_t⊙c_(t−1) + i_t⊙c̃_t；h_t = o_t⊙tanh(c_t)", "Ⅲ.2 基于 LSTM 的方法（P66）", "LSTM 单元状态/输出更新（⊙=逐元素相乘）"],
    ["⑨  62.5 ÷ 8.3 ≈ 7.5", "Ⅴ 多模态传感器融合（P116）", "两传感器采样率之比（早期融合的障碍）"],
    ["⑩  1 : 3", "Ⅱ.3 QUIDA 数据集（P55）", "跌倒:非跌倒 窗口比例（类别不平衡来源）"],
]
it = doc.add_table(rows=len(idx_rows)+1, cols=3); it.style = "Table Grid"
it.autofit = False
IW = [Cm(6.0), Cm(4.6), Cm(6.6)]
for _r in it.rows:
    for _j, _c in enumerate(_r.cells):
        _c.width = IW[_j]
for j, v in enumerate(idx_header):
    cell2 = it.cell(0, j); cell2.text = ""
    pr = cell2.paragraphs[0]; pr.paragraph_format.space_after = Pt(0)
    sr(pr.add_run(v), size=8.5, bold=True)
_HDR = OxmlElement("w:tblHeader")
it.rows[0]._tr.get_or_add_trPr().append(_HDR)
for i, r in enumerate(idx_rows, start=1):
    for j, v in enumerate(r):
        cell2 = it.cell(i, j); cell2.text = ""
        pr = cell2.paragraphs[0]; pr.paragraph_format.space_after = Pt(0)
        sr(pr.add_run(v), size=8.5, en=("Cambria Math" if j == 0 else "Calibri"))
doc.add_paragraph()

OUT = r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\State of the Art v2 中英对照版.docx"
doc.save(OUT)
print("DOCX saved:", OUT)
