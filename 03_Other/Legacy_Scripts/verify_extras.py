# -*- coding: utf-8 -*-
import glob, os, sys
sys.stdout.reconfigure(encoding="utf-8")
try:
    import pypdf
except ImportError:
    import PyPDF2 as pypdf
SUB = r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\Bibliographie_PDF\Complements"
for p in sorted(glob.glob(os.path.join(SUB, "*.pdf"))):
    r = pypdf.PdfReader(p)
    t = " ".join((r.pages[0].extract_text() or "").split())
    print("###", os.path.basename(p), "| pages:", len(r.pages))
    print("   ", t[:190])
    print()
