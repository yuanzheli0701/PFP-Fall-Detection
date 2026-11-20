import sys
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\_work\v2_content.py"
lines = open(p, encoding="utf-8").read().split("\n")
# find the line starting with '135:' and insert '}' after it
for i, ln in enumerate(lines):
    if ln.startswith('135: "最后，将以两种方式'):
        lines.insert(i+1, "}")
        break
open(p, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
import ast
ast.parse(open(p, encoding="utf-8").read())
print("fixed and syntax OK")
