import zipfile, re, sys
sys.stdout.reconfigure(encoding="utf-8")
z = zipfile.ZipFile(r"C:\Users\13968\Downloads\State of the art - shared (revu2).docx")
xml = z.read("word/document.xml").decode("utf-8")
open(r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\_work\document.xml", "w", encoding="utf-8").write(xml)
for key in ["The authors segment", "They do not train", "arm-flapping", "kernel size"]:
    pos = [m.start() for m in re.finditer(re.escape(key), xml)]
    print(key, "->", pos)
