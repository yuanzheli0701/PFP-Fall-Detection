import sys
from docx import Document
from docx.oxml.ns import qn
sys.stdout.reconfigure(encoding="utf-8")
d = Document(r"C:\Users\13968\Downloads\State of the art - shared (revu2).docx")
for i in range(50, 70):
    p = d.paragraphs[i]
    print(f"[{i}] style={p.style.name} text={p.text[:200]!r}")
