import sys
from docx import Document
from docx.oxml.ns import qn
sys.stdout.reconfigure(encoding="utf-8")
d = Document(r"C:\Users\13968\Downloads\State of the art - shared (revu2).docx")
body = d.element.body
pi = 0; ti = 0
for child in body.iterchildren():
    tag = child.tag.split("}")[1]
    if tag == "p":
        # find its index among paragraphs
        txt = "".join(t.text or "" for t in child.iter(qn("w:t")))
        if txt.strip():
            print(f"P{pi}: {txt.strip()[:60]}")
        pi += 1
    elif tag == "tbl":
        print(f"  >>> TABLE {ti} <<<")
        ti += 1
