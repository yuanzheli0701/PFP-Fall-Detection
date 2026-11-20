# -*- coding: utf-8 -*-
import re, sys
import docx
sys.stdout.reconfigure(encoding="utf-8")
d = docx.Document("State of the art - shared (revu).docx")
paras = [p.text.strip() for p in d.paragraphs]
print("TOTAL", len(paras))
for i, t in enumerate(paras[-45:], start=len(paras)-45):
    if t:
        print("[%3d] %s" % (i, t[:170]))
