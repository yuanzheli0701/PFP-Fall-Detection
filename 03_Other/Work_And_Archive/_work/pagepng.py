import sys, fitz
sys.stdout.reconfigure(encoding="utf-8")
doc = fitz.open(r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\_work\preview.pdf")
print("pages:", len(doc))
for i in [0, 1]:
    page = doc[i]
    pix = page.get_pixmap(dpi=110)
    pix.save(rf"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\_work\page{i+1}.png")
    print("saved page", i+1, pix.width, "x", pix.height)
