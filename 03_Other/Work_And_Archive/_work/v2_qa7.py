import sys, fitz
sys.stdout.reconfigure(encoding="utf-8")
doc = fitz.open(r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\State of the Art v2 中英对照版.pdf")
print("pages:", len(doc))
for i, page in enumerate(doc):
    t = page.get_text()
    first = (t.strip().splitlines() or [""])[0][:60]
    print(i+1, "|", first)
for i in [11, 12, 13]:
    doc[i].get_pixmap(dpi=110).save(rf"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\_work\v2_s{i+1}.png")
