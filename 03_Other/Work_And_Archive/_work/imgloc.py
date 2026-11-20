import sys
from docx import Document
from docx.oxml.ns import qn
sys.stdout.reconfigure(encoding="utf-8")
d = Document(r"C:\Users\13968\Downloads\State of the art - shared (revu2).docx")
for i, p in enumerate(d.paragraphs):
    blips = p._p.findall(".//" + qn("a:blip"))
    drawings = p._p.findall(".//" + qn("w:drawing"))
    if blips or drawings:
        embeds = [b.get(qn("r:embed")) for b in blips]
        print(f"[P{i}] drawings={len(drawings)} embeds={embeds} text='{p.text.strip()[:80]}'")
# also check headers/footers and any floating anchored images
seen = 0
for part in [d.part]:
    for rel in part.rels.values():
        if "image" in rel.reltype:
            print("REL:", rel.rId, rel.target_ref)
