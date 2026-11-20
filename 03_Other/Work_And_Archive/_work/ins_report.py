import sys, zipfile
import lxml.etree as ET
sys.stdout.reconfigure(encoding="utf-8")
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
qn = lambda t: "{%s}%s" % (W, t)
z = zipfile.ZipFile(r"C:\Users\13968\Downloads\State of the art - shared (revu2).docx")
root = ET.fromstring(z.read("word/document.xml"))
body = root.find(qn("body"))
paras = [p for p in body.iter(qn("p"))]
pi = 0
count = 0
for p in body:
    if p.tag != qn("p"):
        continue
    ins = p.findall(".//" + qn("ins"))
    dels = p.findall(".//" + qn("del"))
    if ins or dels:
        count += 1
        def txt(el, tag="t"):
            return "".join(t.text or "" for t in el.iter(qn(tag)))
        info = []
        if ins: info.append("INS(" + str(len(ins)) + "): " + " / ".join(txt(i).strip()[:120] for i in ins))
        if dels: info.append("DEL(" + str(len(dels)) + "): " + " / ".join(txt(d, "delText").strip()[:120] for d in dels))
        print(f"P{pi}:")
        for x in info: print("   ", x)
    pi += 1
print("total paragraphs with revisions:", count)
