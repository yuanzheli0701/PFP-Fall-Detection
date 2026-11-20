import sys, zipfile, re
sys.stdout.reconfigure(encoding="utf-8")
z = zipfile.ZipFile(r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\State of the Art v2 中英对照版.docx")
xml = z.read("word/document.xml").decode("utf-8")
print("tblHeader count:", xml.count("tblHeader"))
for m in re.finditer(r"tblHeader", xml):
    print(xml[max(0,m.start()-300):m.end()+80].replace("><", ">\n<")[-500:])
    print("-----")
    break
