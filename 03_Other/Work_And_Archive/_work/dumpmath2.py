import sys
from docx import Document
from docx.oxml.ns import qn
sys.stdout.reconfigure(encoding="utf-8")
d = Document(r"C:\Users\13968\Downloads\State of the art - shared (revu2).docx")

def walk(el, depth=0):
    tag = el.tag.split("}")[1]
    if tag == "t":
        return [("  "*depth) + "T:" + repr(el.text)]
    out = []
    if tag in ("sSub","sSup","sSubSup","f","nary","d","acc","bar","rad"):
        out.append(("  "*depth) + "<" + tag + ">")
        for ch in el:
            out += walk(ch, depth+1)
        return out
    for ch in el:
        out += walk(ch, depth)
    return out

p = d.paragraphs[86]
for om in p._p.iter(qn("m:oMath")):
    print("\n".join(walk(om)))
