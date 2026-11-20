import sys, zipfile
import lxml.etree as ET
sys.stdout.reconfigure(encoding="utf-8")

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
ns = {"w": W, "m": M}
qn = lambda t: "{%s}%s" % (W, t)
qnm = lambda t: "{%s}%s" % (M, t)

z = zipfile.ZipFile(r"C:\Users\13968\Downloads\State of the art - shared (revu2).docx")
root = ET.fromstring(z.read("word/document.xml"))
body = root.find(qn("body"))

def para_text(p):
    """Text with insertions accepted and deletions rejected."""
    parts = []
    for el in p.iter():
        tag = el.tag
        if tag == qn("t"):
            # skip if inside a w:del
            anc = el.getparent()
            skip = False
            while anc is not None:
                if anc.tag == qn("del"):
                    skip = True; break
                anc = anc.getparent()
            if not skip:
                parts.append(el.text or "")
        elif tag == qnm("t"):
            parts.append(el.text or "")
    return "".join(parts)

def math_linear(p):
    """Linearize OMML roughly into readable tokens."""
    out = []
    for om in p.iter(qnm("oMath")):
        out.append(_lin(om))
    return out

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
    if tag == "sSubSup":
        e = el.find(qnm("e")); sub = el.find(qnm("sub")); sup = el.find(qnm("sup"))
        return _lin(e) + "_(" + _lin(sub) + ")^(" + _lin(sup) + ")"
    if tag == "f":
        num = el.find(qnm("num")); den = el.find(qnm("den"))
        return "(" + _lin(num) + ")/(" + _lin(den) + ")"
    if tag == "d":
        inner = "".join(_lin(c) for c in el.findall(qnm("e")))
        dpr = el.find(qnm("dPr"))
        beg, end = "(", ")"
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
            txt = " ".join(para_text(p).strip() for p in tc.findall(qn("p")))
            cells.append(txt.strip())
        rows.append(cells)
    return rows

out = []
pi = 0
for child in body:
    tag = child.tag
    if tag == qn("p"):
        t = para_text(child).strip()
        maths = ["[EQ] " + m for m in math_linear(child)]
        if t or maths:
            out.append(f"[P{pi}] {t}")
            out.extend("      " + m for m in maths)
        pi += 1
    elif tag == qn("tbl"):
        out.append("=== TABLE ===")
        for r in table_text(child):
            out.append("R: " + " | ".join(r))
        out.append("=== END TABLE ===")
    elif tag == qn("sdt"):
        # TOC: include for reference
        t = " ".join(para_text(p).strip() for p in child.iter(qn("p"))).strip()
        if t:
            out.append("[TOC] " + t[:2000])

open(r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\_work\final_text.txt", "w", encoding="utf-8").write("\n".join(out))
print("OK, lines:", len(out))
# count tracked changes
import re
xml = z.read("word/document.xml").decode("utf-8")
print("w:ins count:", xml.count("<w:ins "))
print("w:del count:", xml.count("<w:del "))
