import zipfile, sys
sys.stdout.reconfigure(encoding="utf-8")
z = zipfile.ZipFile(r"C:\Users\13968\Downloads\State of the art - shared (revu2).docx")
for n in z.namelist():
    print(n)
