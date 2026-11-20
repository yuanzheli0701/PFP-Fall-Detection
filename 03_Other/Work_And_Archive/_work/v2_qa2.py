import sys, fitz
sys.stdout.reconfigure(encoding="utf-8")
doc = fitz.open(r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\State of the Art v2 中英对照版.pdf")
for i in [5, 6, 12]:
    doc[i].get_pixmap(dpi=100).save(rf"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\_work\v2_q{i+1}.png")
    print("saved", i+1)
