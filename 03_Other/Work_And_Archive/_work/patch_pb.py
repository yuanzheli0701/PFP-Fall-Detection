import io
P = r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\_work\v2_render.py"
s = io.open(P, encoding="utf-8").read()

old = '''# formula index appendix
c = add_merged_row()
para(c, "附录 · 公式索引表 Formula Index（公式 ↔ 位置 ↔ 一句话含义）", size=12, bold=True, color=RGBColor(0x1F,0x3B,0x5C))'''

new = '''# formula index appendix (own page)
c = add_merged_row()
_p0 = c.paragraphs[0]
_p0.add_run().add_break(WD_BREAK.PAGE)
para(c, "附录 · 公式索引表 Formula Index（公式 ↔ 位置 ↔ 一句话含义）", size=12, bold=True, color=RGBColor(0x1F,0x3B,0x5C))'''

assert old in s, "anchor not found"
s = s.replace(old, new)

if "WD_BREAK" not in s.split("\n")[0:40].__str__():
    pass
# ensure import
s = s.replace("from docx.shared import", "from docx.enum.text import WD_BREAK\nfrom docx.shared import", 1)
io.open(P, "w", encoding="utf-8").write(s)
print("patched; WD_BREAK import present:", "WD_BREAK" in s)
