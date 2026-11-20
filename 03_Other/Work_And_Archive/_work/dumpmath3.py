import sys, re
from docx import Document
from docx.oxml.ns import qn
sys.stdout.reconfigure(encoding="utf-8")
d = Document(r"C:\Users\13968\Downloads\State of the art - shared (revu2).docx")

def walk(el, depth=0):
    tag = el.tag.split("}")[1]
    if tag == "t":
        return [("  "*depth) + "T:" + repr(el.text)]
    if tag == "dPr":
        # print delimiter characters and separators
        beg = el.find(qn("m:begChr")); end = el.find(qn("m:endChr")); sep = el.find(qn("m:sepChr"))
        info = []
        if beg is not None: info.append("beg=" + repr(beg.get(qn("m:val"))))
        if end is not None: info.append("end=" + repr(end.get(qn("m:val"))))
        if sep is not None: info.append("sep=" + repr(sep.get(qn("m:val"))))
        return [("  "*depth) + "DPR " + " ".join(info)] if info else []
    out = []
    if tag in ("sSub","sSup","sSubSup","f","nary","d","acc","bar","rad","e","sub","sup","num","den"):
        out.append(("  "*depth) + "<" + tag + ">")
        for ch in el:
            out += walk(ch, depth+1)
        return out
    for ch in el:
        out += walk(ch, depth)
    return out

for idx in (86, 81, 95):
    p = d.paragraphs[idx]
    print(f"##### P{idx} #####")
    for om in p._p.iter(qn("m:oMath")):
        print("\n".join(walk(om)))
    print()
