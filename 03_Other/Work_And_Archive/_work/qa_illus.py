import sys, fitz
sys.stdout.reconfigure(encoding="utf-8")
doc = fitz.open(r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\State of the Art 报告-中文全译-图文对照版.pdf")
print("pages:", len(doc))
for i, page in enumerate(doc):
    t = page.get_text()
    n_img = len(page.get_images(full=True))
    if "图1." in t or "图2a." in t or "图3." in t or "图4." in t or "图5." in t or "图6." in t or "图7." in t:
        marks = [m for m in ["图1.", "图2a.", "图2b.", "图3.", "图4.", "图5.", "图6.", "图7."] if m in t]
        print("page", i+1, "images:", n_img, marks)
