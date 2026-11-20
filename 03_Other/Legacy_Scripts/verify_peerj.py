# -*- coding: utf-8 -*-
import os, sys
sys.stdout.reconfigure(encoding="utf-8")
try:
    import pypdf
except ImportError:
    import PyPDF2 as pypdf
p = r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\Bibliographie_PDF\16_Taramasco_2025_Multimodal_Sensor_Fusion_Fall_Dataset.pdf"
r = pypdf.PdfReader(p)
for i in (1, 2):
    txt = " ".join((r.pages[i].extract_text() or "").split())
    print("--- page", i+1, ":", txt[:400])
    print()
