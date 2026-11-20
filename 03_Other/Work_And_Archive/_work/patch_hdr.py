import io
P = r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\_work\v2_render.py"
s = io.open(P, encoding="utf-8").read()

old = '''it = c.add_table(rows=len(idx_rows)+1, cols=3); it.style = "Table Grid"
for j, v in enumerate(idx_header):
    cell2 = it.cell(0, j); cell2.text = ""
    pr = cell2.paragraphs[0]; pr.paragraph_format.space_after = Pt(0)
    sr(pr.add_run(v), size=8.5, bold=True)'''

new = '''it = c.add_table(rows=len(idx_rows)+1, cols=3); it.style = "Table Grid"
for j, v in enumerate(idx_header):
    cell2 = it.cell(0, j); cell2.text = ""
    pr = cell2.paragraphs[0]; pr.paragraph_format.space_after = Pt(0)
    sr(pr.add_run(v), size=8.5, bold=True)
_HDR = OxmlElement("w:tblHeader")
it.rows[0]._tr.get_or_add_trPr().append(_HDR)'''

assert old in s, "anchor not found"
s = s.replace(old, new)
io.open(P, "w", encoding="utf-8").write(s)
print("patched")
