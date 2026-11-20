import zipfile, re, sys
import lxml.etree as ET
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\13968\Downloads\State of the art v2.docx"
z = zipfile.ZipFile(p)
print("== ZIP entries ==")
for n in z.namelist():
    print("  ", n, z.getinfo(n).file_size)
xml = z.read("word/document.xml").decode("utf-8")
print("== counts ==")
print("w:ins:", xml.count("<w:ins "), " w:del:", xml.count("<w:del "))
print("oMathPara:", xml.count("<m:oMathPara"), " oMath:", xml.count("<m:oMath>"))
print("w:tbl:", xml.count("<w:tbl>"), " w:drawing:", xml.count("<w:drawing>"))
