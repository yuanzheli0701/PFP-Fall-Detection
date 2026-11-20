import io, sys
sys.stdout.reconfigure(encoding="utf-8")
p = r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\_work\render_illus.py"
src = open(p, encoding="utf-8").read()
needle = "p.paragraph_format.space_before = Pt(8)\n"
add = "            p.paragraph_format.keep_with_next = True\n"
if "keep_with_next" in src:
    print("already patched")
else:
    # find the figure-section occurrence (inside the figure block)
    idx = src.find("elif kind == \"figure\":")
    j = src.find(needle, idx)
    if j == -1:
        print("NOT FOUND"); raise SystemExit(1)
    j2 = j + len(needle)
    src = src[:j2] + add + src[j2:]
    open(p, "w", encoding="utf-8", newline="\n").write(src)
    print("patched OK")
