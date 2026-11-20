import sys
from docx import Document
sys.stdout.reconfigure(encoding="utf-8")
d = Document(r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\State of the Art 报告-中文全译与公式详解.docx")
print("paragraphs:", len(d.paragraphs), "tables:", len(d.tables))
for p in d.paragraphs[:12]:
    if p.text.strip(): print(repr(p.text[:80]))
print("...")
# count formulas
f = [p.text for p in d.paragraphs if p.text.startswith(("L =", "c_k"))]
print("formula lines:", f)
