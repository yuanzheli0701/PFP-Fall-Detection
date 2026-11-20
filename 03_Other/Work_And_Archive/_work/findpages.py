import sys, fitz
sys.stdout.reconfigure(encoding="utf-8")
doc = fitz.open(r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\_work\preview.pdf")
for i, page in enumerate(doc):
    t = page.get_text()
    hits = [k for k in ["公式1", "公式2", "公式3", "表 1.", "表 2.", "表 3.", "附录A", "附录B", "附录C"] if k in t]
    if hits:
        print(i+1, hits)
