# -*- coding: utf-8 -*-
import json, os, re, sys
import docx
sys.stdout.reconfigure(encoding="utf-8")

DOC = "State of the art - shared (revu).docx"
d = docx.Document(DOC)

# 1) collect headings & paragraphs with section tracking
sections = []
cur = "(avant sections)"
for p in d.paragraphs:
    t = p.text.strip()
    if not t: continue
    st = (p.style.name or "")
    if st.lower().startswith("heading") or re.match(r"^\d+(\.\d+)*\.?\s+[A-Z]", t):
        # ignore the References entries themselves later
        if len(t) < 90 and not re.match(r"^[A-Z][a-z]+,\s", t):
            cur = t
    sections.append((cur, t))

# 2) reference keys -> regex to find in-text mentions
REFS = [
 ("Bakshi & Rajan (2021)",   r"Bakshi"),
 ("Chicco (2021)",           r"Chicco"),
 ("Droghini et al. (2018)",  r"Droghini"),
 ("Hadsell, Chopra & LeCun (2006)", r"Hadsell"),
 ("Hermans, Beyer & Leibe (2017)",  r"Hermans"),
 ("Hochreiter & Schmidhuber (1997)", r"Hochreiter"),
 ("Jin, Sengupta & Cao (2020)", r"\bJin\b"),
 ("Koch, Zemel & Salakhutdinov (2015)", r"Koch"),
 ("Kwolek & Kepski (2014)",  r"Kwolek"),
 ("Martinez-Villasenor et al. (2019)", r"Mart[ií]nez"),
 ("Musci et al. (2021)",     r"Musci"),
 ("Qi et al. (2017)",        r"\bQi\b"),
 ("Santos et al. (2019)",    r"Santos"),
 ("Schroff, Kalenichenko & Philbin (2015)", r"Schroff"),
 ("Snell, Swersky & Zemel (2017)", r"Snell"),
 ("Taramasco et al. (2025)", r"Taramasco"),
 ("Tran et al. (2018)",      r"\bTran\b"),
 ("Wang et al. (2019)",      r"Wang et al\.?,?\s*\(?2019"),
 ("Wang, Ellul & Azzopardi (2020)", r"Wang et al\.?,?\s*\(?2020"),
 ("Yu, Jang & Xiong (2021)", r"\bYu\b"),
]

# stop at references section to avoid counting the list itself
cut = None
for i, (sec, t) in enumerate(sections):
    if t.strip().lower() in ("references", "i. references"):
        cut = i; break
body = sections[:cut] if cut else sections

out = {}
for name, pat in REFS:
    hits = []
    for sec, t in body:
        if re.search(pat, t):
            hits.append(sec)
    # dedupe consecutive
    seen, hits2 = set(), []
    for h in hits:
        if h not in seen:
            seen.add(h); hits2.append(h)
    out[name] = hits2

print(json.dumps(out, ensure_ascii=False, indent=1))
json.dump(out, open("_cite_map_tmp.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\nSECTIONS FOUND:", sorted({s for s, _ in body})[:40])
