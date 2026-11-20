# -*- coding: utf-8 -*-
import re, sys
import docx
sys.stdout.reconfigure(encoding="utf-8")

for fn in ["State of the art - shared.docx", "State of the art - shared (revu).docx"]:
    print("=" * 90)
    print("FILE:", fn)
    d = docx.Document(fn)
    paras = [p.text.strip() for p in d.paragraphs]
    # locate references section
    idx = None
    for i, t in enumerate(paras):
        if re.match(r"^(I+\.|[0-9]+[\.\)]?)\s*References\s*$", t, re.I):
            idx = i; break
    print("paragraphs:", len(paras), "| references section starts at:", idx)
    if idx is not None:
        for t in paras[idx:idx+40]:
            if t:
                print("  REF>", t[:200])
    # in-text citations
    text = "\n".join(paras)
    cites = set()
    for m in re.finditer(r"([A-Z][A-Za-z\u00C0-\u024F\-]+(?:\s*(?:&|and|et)\s*[A-Z][A-Za-z\u00C0-\u024F\-]+)?(?:\s+et\s+al\.?)?)\s*\((\d{4})\)", text):
        cites.add((m.group(1).strip(), m.group(2)))
    print("  --- in-text citations (%d):" % len(cites))
    for a, y in sorted(cites, key=lambda x: x[1]):
        print("   ", a, y)
