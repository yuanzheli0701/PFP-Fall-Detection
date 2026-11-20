import sys, fitz
sys.stdout.reconfigure(encoding="utf-8")
doc = fitz.open(r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\State of the Art 报告-中文全译-图文对照版.pdf")
for i in [3, 4, 9]:
    pix = doc[i].get_pixmap(dpi=100)
    pix.save(rf"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\_work\qa_{i+1}.png")
    print("saved page", i+1)
