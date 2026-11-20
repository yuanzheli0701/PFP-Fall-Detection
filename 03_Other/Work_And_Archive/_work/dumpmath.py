import sys, re
from docx import Document
sys.stdout.reconfigure(encoding="utf-8")
d = Document(r"C:\Users\13968\Downloads\State of the art - shared (revu2).docx")
for i in (81, 86, 95):
    p = d.paragraphs[i]
    xml = p._p.xml
    xml = re.sub(r"<w:rPr>.*?</w:rPr>", "", xml, flags=re.S)
    print(f"====== P{i} ======")
    print(xml[:6000])
    print()
