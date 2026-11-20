# -*- coding: utf-8 -*-
import os, sys, time, urllib.parse, re
import requests
sys.stdout.reconfigure(encoding="utf-8")
OUT = r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\Bibliographie_PDF"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
S = requests.Session(); S.headers.update({"User-Agent": UA, "Accept": "*/*"})
def log(*a):
    print(*a); sys.stdout.flush()

def cdx(urlglob, filt=".*pdf.*", limit=300):
    try:
        r = S.get("http://web.archive.org/cdx/search/cdx",
                  params={"url": urlglob, "output": "text", "fl": "original,timestamp",
                          "filter": "original:" + filt, "collapse": "urlkey", "limit": limit},
                  timeout=120)
        if r.status_code == 200:
            return [l.split(" ") for l in r.text.strip().splitlines() if l.strip()]
    except Exception as e:
        log("   cdx err", str(e)[:100])
    return []

def try_dl(url, dest, label):
    try:
        r = S.get(url, timeout=120, allow_redirects=True, headers={"Accept": "application/pdf,*/*"})
    except Exception as e:
        log("   dl err [%s] %s" % (label, str(e)[:90])); return False
    if r.status_code == 200 and r.content[:5] == b"%PDF-":
        open(dest, "wb").write(r.content)
        log("   OK [%s] %dB <- %s" % (label, len(r.content), r.url))
        return True
    log("   fail [%s] HTTP %s ct=%s size=%s" % (label, r.status_code, r.headers.get("Content-Type"), len(r.content)))
    return False

# --- Kwolek: list archived PDFs on his AGH page
log("### Kwolek AGH page: archived PDFs")
dest = os.path.join(OUT, "09_Kwolek_Kepski_2014_Fall_Detection_Embedded_Depth.pdf")
rows = cdx("home.agh.edu.pl/~kwolek*")
for orig, ts in rows[:80]:
    log("   ", ts, orig)
cands = [o for o, t in rows if re.search(r"(fall|cmpb|depth).*\.pdf", o, re.I)] or [o for o, t in rows]
for o in cands[:12]:
    ts = [t for oo, t in rows if oo == o][0]
    if try_dl("https://web.archive.org/web/%sid_/%s" % (ts, o), dest, "kwolek"): break

# --- Tran 2018: extra S2 title variants
log("### Tran 2018: S2 variants")
for q in ["multi-modal multi-view dataset human fall analysis modality",
          "Multi-modal Multi-View Dataset Human Fall Analysis"]:
    try:
        r = S.get("https://api.semanticscholar.org/graph/v1/paper/search",
                  params={"query": q, "fields": "title,year,openAccessPdf", "limit": 5}, timeout=60)
        if r.status_code == 200:
            for d in r.json().get("data", []):
                log("   ", d.get("year"), d.get("title")[:88], "| oa:", (d.get("openAccessPdf") or {}).get("url"))
        time.sleep(2)
    except Exception as e:
        log("   err", str(e)[:90])

# --- Chicco site quick check
log("### Chicco site: archived PDFs")
rows2 = cdx("davidechicco.it*", filt=".*(siamese|chapter|overview).*", limit=100)
for orig, ts in rows2[:40]:
    log("   ", ts, orig)
log("ROUND7 DONE")
