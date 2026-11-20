import sys, fitz
sys.stdout.reconfigure(encoding="utf-8")
doc = fitz.open(r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\State of the Art v2 中英对照版.pdf")
print("pages:", len(doc))
for i, page in enumerate(doc):
    t = page.get_text()
    hits = [k for k in ["公式索引表","公式详解①","公式详解②","公式详解③"] if k in t]
    first = (t.strip().splitlines() or [""])[0][:60]
    print(i+1, "|", first, "|", hits)
