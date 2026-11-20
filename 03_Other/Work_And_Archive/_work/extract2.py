import sys
from docx import Document
from docx.oxml.ns import qn
sys.stdout.reconfigure(encoding="utf-8")
path = r"C:\Users\13968\Downloads\State of the art - shared (revu2).docx"
d = Document(path)

def omml_text(el):
    # crude but reliable: collect all m:t text
    return "".join(t.text or "" for t in el.iter(qn("m:t")))

out = []
for i, p in enumerate(d.paragraphs):
    runs = []
    has_math = False
    for child in p._p.iter():
        if child.tag == qn("m:oMath") or child.tag == qn("m:oMathPara"):
            has_math = True
    txt = p.text.strip()
    if has_math:
        maths = [omml_text(m) for m in p._p.iter(qn("m:oMath"))]
        out.append(f"[P{i}] (MATH) text='{txt}' || " + " || ".join(maths))
    elif txt:
        out.append(f"[P{i}] ({p.style.name}) {txt}")

out.append("")
out.append("### IMAGES ###")
import zipfile
z = zipfile.ZipFile(path)
for n in z.namelist():
    if "media" in n:
        out.append(n + " size=" + str(z.getinfo(n).file_size))

with open(r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\_work\full_text.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("written", len(out), "lines")
