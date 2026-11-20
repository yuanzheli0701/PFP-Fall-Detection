import sys
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\_work\v2_content.py"
for i, line in enumerate(open(p, encoding="utf-8"), 1):
    n = line.count('"')
    if n % 2 == 1:
        print(i, n, repr(line[:120]))
