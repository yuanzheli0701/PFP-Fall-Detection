import sys, zipfile, re
sys.stdout.reconfigure(encoding="utf-8")
z = zipfile.ZipFile(r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\State of the Art v2 中英对照版.docx")
xml = z.read("word/document.xml").decode("utf-8")
print("page breaks:", xml.count('w:type="page"'))
i = xml.find("附录")
print(xml[max(0,i-900):i+120].replace("><", ">\n<"))
