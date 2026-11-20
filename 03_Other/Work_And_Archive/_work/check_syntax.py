import sys, ast, traceback
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\_work\v2_content.py"
src = open(p, encoding="utf-8").read()
try:
    ast.parse(src)
    print("OK")
except SyntaxError as e:
    print("SyntaxError line", e.lineno, "col", e.offset, "msg:", e.msg)
    lines = src.splitlines()
    for i in range(max(0, e.lineno-6), min(len(lines), e.lineno+3)):
        print(f"{i+1:4d}| {lines[i][:110]}")
