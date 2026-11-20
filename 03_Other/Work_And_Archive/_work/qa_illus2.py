import sys, fitz
sys.stdout.reconfigure(encoding="utf-8")
doc = fitz.open(r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\State of the Art 报告-中文全译-图文对照版.pdf")
for i, page in enumerate(doc):
    t = page.get_text()
    n = len(page.get_images(full=True))
    caps = [m for m in ["图1.", "图2a.", "图2b.", "图3.", "图4.", "图5.", "图6.", "图7."] if m in t]
    if n or caps:
        print(f"page {i+1:2d}  images={n}  captions={caps}")
