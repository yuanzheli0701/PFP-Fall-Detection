# -*- coding: utf-8 -*-
import sys, zipfile
import lxml.etree as ET
sys.stdout.reconfigure(encoding="utf-8")

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
qn = lambda t: "{%s}%s" % (W, t)
qnm = lambda t: "{%s}%s" % (M, t)

z = zipfile.ZipFile(r"C:\Users\13968\Downloads\State of the art v2.docx")
root = ET.fromstring(z.read("word/document.xml"))
body = root.find(qn("body"))

def para_text(p):
    parts = []
    for el in p.iter():
        if el.tag == qn("t"):
            parts.append(el.text or "")
        elif el.tag == qnm("t"):
            parts.append(el.text or "")
    return "".join(parts)

def _lin(el):
    tag = el.tag.split("}")[1]
    if tag == "t":
        return el.text or ""
    if tag == "sSup":
        e = el.find(qnm("e")); sup = el.find(qnm("sup"))
        return _lin(e) + "^(" + _lin(sup) + ")"
    if tag == "sSub":
        e = el.find(qnm("e")); sub = el.find(qnm("sub"))
        return _lin(e) + "_(" + _lin(sub) + ")"
    if tag == "f":
        num = el.find(qnm("num")); den = el.find(qnm("den"))
        return "(" + _lin(num) + ")/(" + _lin(den) + ")"
    if tag == "d":
        inner = "".join(_lin(c) for c in el.findall(qnm("e")))
        dpr = el.find(qnm("dPr")); beg, end = "(", ")"
        if dpr is not None:
            b = dpr.find(qnm("begChr")); e2 = dpr.find(qnm("endChr"))
            if b is not None: beg = b.get(qnm("val"))
            if e2 is not None: end = e2.get(qnm("val"))
        return beg + inner + end
    if tag == "nary":
        sub = el.find(qnm("sub")); sup = el.find(qnm("sup")); e = el.find(qnm("e"))
        return "\u2211" + "_{" + (_lin(sub) if sub is not None else "") + "}" + ("^{" + _lin(sup) + "}" if sup is not None and _lin(sup) else "") + " " + _lin(e)
    out = []
    for ch in el:
        out.append(_lin(ch))
    return "".join(out)

def table_text(tbl):
    rows = []
    for tr in tbl.findall(qn("tr")):
        cells = []
        for tc in tr.findall(qn("tc")):
            cells.append(" ".join(para_text(p).strip() for p in tc.findall(qn("p"))).strip())
        rows.append(cells)
    return rows

out = []
pi = 0
for child in body:
    tag = child.tag
    if tag == qn("p"):
        t = para_text(child).strip()
        maths = ["[EQ] " + _lin(m) for m in child.iter(qnm("oMath"))]
        if t or maths:
            out.append(f"[P{pi}] {t}")
            for m in maths:
                out.append("      " + m)
        pi += 1
    elif tag == qn("tbl"):
        out.append("=== TABLE ===")
        for r in table_text(child):
            out.append("R: " + " | ".join(r))
        out.append("=== END TABLE ===")
    elif tag == qn("sdt"):
        t = " ".join(para_text(p).strip() for p in child.iter(qn("p"))).strip()
        if t:
            out.append("[TOC] " + t[:2500])

open(r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\_work\v2_text.txt", "w", encoding="utf-8").write("\n".join(out))
print("lines:", len(out))

# header/footer
for part in ["word/header1.xml", "word/footer1.xml"]:
    r = ET.fromstring(z.read(part))
    txt = " | ".join((t.text or "").strip() for t in r.iter(qn("t")) if (t.text or "").strip())
    print(part, "->", txt[:200])
