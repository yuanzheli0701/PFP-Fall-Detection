import zipfile, sys
import lxml.etree as ET
sys.stdout.reconfigure(encoding="utf-8")
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
qn = lambda ns, t: "{%s}%s" % (ns, t)
z = zipfile.ZipFile(r"C:\Users\13968\Downloads\State of the art - shared (revu2).docx")
for part in ["word/comments.xml", "word/footnotes.xml", "word/endnotes.xml", "word/header1.xml", "word/footer1.xml"]:
    root = ET.fromstring(z.read(part))
    txts = []
    for el in root.iter():
        if el.tag.endswith("}t") and el.text and el.text.strip():
            txts.append(el.text.strip())
    print("=== " + part + " ===")
    print(" | ".join(txts)[:1500] if txts else "(empty)")
    print()
