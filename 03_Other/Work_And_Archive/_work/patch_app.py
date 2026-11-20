import io
P = r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\_work\v2_render.py"
s = io.open(P, encoding="utf-8").read()

start = s.index("# formula index appendix (own page)")
end = s.index("OUT = r")
old = s[start:end]

new = '''# formula index appendix: top-level block on its own page (header row repeats)
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

'''

s = s[:start] + new + s[end:]
io.open(P, "w", encoding="utf-8").write(s)
print("appendix restructured")
