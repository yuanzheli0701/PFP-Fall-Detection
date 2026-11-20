import sys, fitz
sys.stdout.reconfigure(encoding="utf-8")
doc = fitz.open(r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\State of the Art v2 中英对照版.pdf")
print("pages:", len(doc))
for i, page in enumerate(doc):
    t = page.get_text()
    hits = []
    for k in ["公式详解", "公式索引表", "Table 1", "Table 2", "Table 3"]:
        if k in t: hits.append(k)
    if hits:
        print("page", i+1, hits)
for i in [0, 1, 2]:
    doc[i].get_pixmap(dpi=100).save(rf"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\_work\v2_p{i+1}.png")
print("QA images saved")
