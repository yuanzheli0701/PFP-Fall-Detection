import docx, sys, json
sys.stdout.reconfigure(encoding="utf-8")
path = r"C:\Users\13968\Downloads\State of the art - shared (revu2).docx"
d = docx.Document(path)
print("PARAGRAPHS:", len(d.paragraphs), " TABLES:", len(d.tables), " SECTIONS:", len(d.sections))
for i,p in enumerate(d.paragraphs):
    t = p.text.strip()
    if t:
        print(f"[P{i}] ({p.style.name}) {t}")
for ti,tb in enumerate(d.tables):
    print(f"=== TABLE {ti} ({len(tb.rows)}x{len(tb.columns)}) ===")
    for ri,row in enumerate(tb.rows):
        cells = [c.text.replace("\n"," / ").strip() for c in row.cells]
        print(f"R{ri}: " + " | ".join(cells))
