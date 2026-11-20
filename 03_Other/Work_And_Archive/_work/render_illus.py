# -*- coding: utf-8 -*-
import sys, runpy
sys.stdout.reconfigure(encoding="utf-8")

W = r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\_work"
FIG = r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\figures"
EN = FIG + r"\en"
g1 = runpy.run_path(W + r"\content.py")
g2 = runpy.run_path(W + r"\content2.py")
BLOCKS = g1["BLOCKS"] + g2["BLOCKS2"]

# ---- figure insertions: (paragraph prefix, [ (img path, caption), ... ]) ----
FIG1 = (EN + r"\fig_fall_window.png", "图1. 真实跌倒窗口（QUIDA · subject_1 · 加速度计 62.5 Hz · 10 秒窗）：撞击峰值 69.2 m/s²；前段平稳 → 自由落体与撞击 → 跌倒后静止——正文 Ⅱ.1「自由落体 → 尖锐撞击峰值 → 静止期」的真实样例。")
FIG2A = (FIG + r"\fenetre_chute_subject1.png", "图2a. QUIDA 原始记录示例（法文标注）：subject_1 的跌倒窗口（fenêtre 6 · chute = 跌倒），撞击瞬间 x 轴约 38 m/s²。")
FIG2B = (FIG + r"\fenetre_neutre_subject1.png", "图2b. 同一受试者的非跌倒窗口（fenêtre 1 · neutre = 非跌倒）：只有日常活动的起伏，没有「尖峰 + 随后静止」的跌倒形态——分类器要区分的正是这两种模式。")
FIG3 = (EN + r"\fig_conv1d.png", "图3. 一维卷积示意：滤波核 w = [−0.5, −1, 0, +1, +0.5]（K = 5）沿时间滑动；平坦段几乎无响应，撞击处响应最强——对应正文 Ⅲ.1「滤波器检测局部模式」。")
FIG4 = (EN + r"\fig_cnn_arch.png", "图4. 1D-CNN 基线结构：3 层卷积 + 2 次池化 + 全局平均池化 + 全连接，约 9.3k 参数；红框 RF 为感受野（最终 24 点 ≈ 62.5 Hz 下 0.38 秒）——呼应正文 Ⅲ.1 的参数量与感受野段落。")
FIG5 = (EN + r"\fig_rnn_unroll.png", "图5. RNN 按时间展开：隐状态 h_t 把过去的信息逐帧传递；每一步复用同一组权重（权重共享）——对应正文 Ⅲ.2「逐步处理序列、保留内部记忆」。")
FIG6 = (EN + r"\fig_lstm_cell.png", "图6. LSTM 单元：遗忘门 / 输入门 / 输出门控制单元状态 c（「信息高速公路」）；c_t = f_t ⊙ c_t−1 + i_t ⊙ c̃_t，h_t = o_t ⊙ tanh(c_t)——对应 revu2 新增的 LSTM 门控段落。")
FIG7 = (EN + r"\fig_compare.png", "图7. 基线架构量化对比（来自配套《Synthese_CNN_LSTM》文档）：参数量 1D-CNN 9.3k ＜ LSTM 17.4k ＜ TCN/Transformer ≈ 50k；时间跨度 1D-CNN 仅 24 点，循环网络可覆盖整窗——支撑「加速度计用 CNN 抓撞击、雷达用 LSTM 看时序」的选型逻辑（Ⅵ.1）。")

INSERTS = [
    ("三轴加速度计是跌倒检测中最成熟的模态", [FIG1]),
    ("QUIDA 由 10 名年轻受试者录制", [FIG2A, FIG2B]),
    ("一维 CNN 让学到的滤波器", [FIG3]),
    ("卷积层由卷积核大小", [FIG4]),
    ("循环神经网络逐步处理序列", [FIG5]),
    ("LSTM 单元在时间步之间", [FIG6]),
    ("监督基线。对加速度计", [FIG7]),
]

# build new block list
new_blocks = []
new_blocks.append(("note", "本版说明：以下是《中文全译与公式详解》的图文对照版。原报告正文本身不含插图（仅封面校徽）；本版已按章节插入 figures/ 文件夹中的 7 处配套插图（共 8 张）。图注均为中文，可直接对照正文阅读。"))
pending = {k: v for k, v in [(p, f) for p, f in INSERTS]}
used = set()
for kind, payload in BLOCKS:
    new_blocks.append((kind, payload))
    if kind == "p":
        for prefix, figs in INSERTS:
            if prefix in used:
                continue
            if payload.startswith(prefix):
                new_blocks.append(("figure", figs))
                used.add(prefix)
missing = [p for p, f in INSERTS if p not in used]
if missing:
    print("WARNING: insertion anchors not found:", missing)
print("figures inserted:", len(used), "of", len(INSERTS))
BLOCKS = new_blocks

TITLE = "State of the Art 报告 · 中文全译与公式详解（图文对照版）"
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
    elif kind == "figure":
        for path, cap in payload:
            url = path.replace("\\", "/")
            md.append(f"\n![{cap[:40]}]({url})\n")
            md.append(f"*{cap}*\n")

md_path = r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\State of the Art 报告-中文全译-图文对照版.md"
with open(md_path, "w", encoding="utf-8") as f:
    f.write("\n".join(md))
print("MD written:", md_path)

# ---------- DOCX ----------
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

doc = Document()
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
            cell = t.cell(0, j); cell.text = ""
            set_run(cell.paragraphs[0].add_run(str(h)), size=10, bold=True)
        for i, r in enumerate(rows, start=1):
            for j, c in enumerate(r):
                cell = t.cell(i, j); cell.text = ""
                set_run(cell.paragraphs[0].add_run(str(c)), size=10)
        doc.add_paragraph()
    elif kind == "figure":
        for path, cap in payload:
            p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.keep_with_next = True
            r = p.add_run(); r.add_picture(path, width=Cm(15.5))
            c = doc.add_paragraph(); c.alignment = WD_ALIGN_PARAGRAPH.CENTER
            c.paragraph_format.space_after = Pt(12)
            set_run(c.add_run(cap), size=9.5, italic=True, color=RGBColor(0x50, 0x50, 0x50))

docx_path = r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\State of the Art 报告-中文全译-图文对照版.docx"
doc.save(docx_path)
print("DOCX written:", docx_path)
