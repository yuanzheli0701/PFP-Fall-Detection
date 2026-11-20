import zipfile, sys
import lxml.etree as ET
sys.stdout.reconfigure(encoding="utf-8")
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
qn = lambda t: "{%s}%s" % (W, t)
z = zipfile.ZipFile(r"C:\Users\13968\Downloads\State of the art - shared (revu2).docx")
root = ET.fromstring(z.read("word/document.xml"))
body = root.find(qn("body"))

# map comment id -> text
croot = ET.fromstring(z.read("word/comments.xml"))
comments = {}
for c in croot.iter(qn("comment")):
    cid = c.get(qn("id"))
    txt = "".join(t.text or "" for t in c.iter(qn("t"))).strip()
    comments[cid] = txt

# walk body paragraphs; find comment ranges
for p in body.iter(qn("p")):
    starts = p.findall(".//" + qn("commentRangeStart"))
    ends = p.findall(".//" + qn("commentRangeEnd"))
    if starts or ends:
        # get paragraph text and locate range: crude approach - marked text between markers
        parts = []
        active = []
        for el in p.iter():
            if el.tag == qn("commentRangeStart"):
                active.append(el.get(qn("id")))
            elif el.tag == qn("commentRangeEnd"):
                if active: active.pop()
            elif el.tag == qn("t") and active:
                parts.append(el.text or "")
        ptext = "".join(t.text or "" for t in p.iter(qn("t")))
        print("MARKED:", "".join(parts)[:150])
        print("  FULL PARA:", ptext[:150])
        for cid in list(dict.fromkeys([s.get(qn("id")) for s in starts])):
            print(f"  COMMENT[{cid}]: {comments.get(cid,'?')}")
        print()
