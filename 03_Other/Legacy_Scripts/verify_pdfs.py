# -*- coding: utf-8 -*-
import glob, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
try:
    import pypdf
except ImportError:
    import PyPDF2 as pypdf
D = r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\Bibliographie_PDF"
for p in sorted(glob.glob(os.path.join(D, "*.pdf"))):
    r = pypdf.PdfReader(p)
    txt = " ".join(((r.pages[0].extract_text() or "")).split())
    print("### " + os.path.basename(p), "| pages:", len(r.pages), "| size:", round(os.path.getsize(p)/1e6, 2), "MB")
    print("    " + txt[:230])
    print()
