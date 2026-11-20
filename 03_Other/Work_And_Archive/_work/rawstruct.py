import sys
from docx import Document
from docx.oxml.ns import qn
sys.stdout.reconfigure(encoding="utf-8")
d = Document(r"C:\Users\13968\Downloads\State of the art - shared (revu2).docx")
body = d.element.body

def text_of(el):
    return "".join(t.text or "" for t in el.iter(qn("w:t")))

idx = 0
for child in body.iterchildren():
    tag = child.tag.split("}")[1]
    if tag == "p":
        t = text_of(child).strip()
        has_math = child.find(".//" + qn("m:oMath")) is not None
        flag = "MATH " if has_math else ""
        print(f"{idx:3d} p  {flag}{t[:150]!r}")
        idx += 1
    elif tag == "tbl":
        print(f"    TBL")
    elif tag == "sdt":
        # descend
        print(f"    SDT-BEGIN")
        for sub in child.iter(qn("w:p")):
            t = text_of(sub).strip()
            if t: print(f"      sdt-p {t[:150]!r}")
        print(f"    SDT-END")
    else:
        print(f"    {tag}")
