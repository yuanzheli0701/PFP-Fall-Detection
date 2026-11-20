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
pi = 0
ti = 0
for child in body:
    if child.tag == qn("p"):
        st = child.find(qn("pPr"))
        sty = ""
        if st is not None:
            s = st.find(qn("pStyle"))
            if s is not None: sty = s.get(qn("val"))
        txt = "".join(t.text or "" for t in child.iter(qn("t"))).strip()
        has_math = child.find(qnm("oMath")) is not None
        if txt or has_math:
            print(f"P{pi} [{sty}] {'MATH' if has_math else ''} {txt[:70]}")
        pi += 1
    elif child.tag == qn("tbl"):
        print(f"   >> TABLE {ti}")
        ti += 1
    elif child.tag == qn("sdt"):
        print("   >> SDT (TOC)")
