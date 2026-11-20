import sys, fitz
sys.stdout.reconfigure(encoding="utf-8")
doc = fitz.open(r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\_work\preview.pdf")
for i in [3, 11, 15]:
    pix = doc[i].get_pixmap(dpi=105)
    pix.save(rf"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\_work\chk{i+1}.png")
    print("saved", i+1)
