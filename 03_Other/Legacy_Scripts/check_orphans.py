# -*- coding: utf-8 -*-
import re, sys
import docx
sys.stdout.reconfigure(encoding="utf-8")

names = ["Bakshi","Chicco","Droghini","Hadsell","Hermans","Hochreiter","mmFall","Jin","Koch",
         "Kwolek","Mart","Musci","PointNet","Qi","Santos","FaceNet","Schroff","Snell","Prototypical",
         "Taramasco","Tran","Wang","KFall","Yu","UP-Fall"]
for fn in ["State of the art - shared.docx", "State of the art - shared (revu).docx"]:
    print("=" * 80); print("FILE:", fn)
    d = docx.Document(fn)
    print("tables:", len(d.tables))
    for ti, tb in enumerate(d.tables):
        for ri, row in enumerate(tb.rows):
            for ci, cell in enumerate(row.cells):
                t = " ".join(cell.text.split())
                if t:
                    print("  T%d r%d c%d: %s" % (ti, ri, ci, t[:130]))
    # any body text paragraphs mentioning the orphans OUTSIDE the reference list (para index < list start 84)
    paras = [(p.style.name or "", p.text.strip()) for p in d.paragraphs if p.text.strip()]
    # find reference list start (first paragraph matching an author-year entry)
    refstart = None
    for i, (st, t) in enumerate(paras):
        if re.match(r"^Bakshi, S\., & Rajan, S\. \(2021\)", t):
            refstart = i; break
    print("  ref list starts at paragraph #", refstart, "of", len(paras))
    body = paras[:refstart] if refstart else paras
    for nm in ["Kwolek", "Mart\u00ednez", "Villase", "UP-Fall", "Tran", "KFall", "Yu,"]:
        hit = [i for i, (st, t) in enumerate(body) if nm.lower() in t.lower()]
        print("   body mentions %-12s -> %s" % (nm, hit if hit else "NONE"))
