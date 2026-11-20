import sys, os
sys.stdout.reconfigure(encoding="utf-8")
import win32com.client
src = r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\State of the Art v2 中英对照版.docx"
dst = r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\State of the Art v2 中英对照版.pdf"
word = win32com.client.Dispatch("Word.Application")
word.Visible = False
doc = word.Documents.Open(src, ReadOnly=True)
doc.SaveAs(dst, FileFormat=17)
doc.Close(False)
word.Quit()
print("PDF saved:", os.path.exists(dst), os.path.getsize(dst))
