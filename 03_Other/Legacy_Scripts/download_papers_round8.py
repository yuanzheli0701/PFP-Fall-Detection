# -*- coding: utf-8 -*-
import sys, re
import requests
sys.stdout.reconfigure(encoding="utf-8")
S = requests.Session(); S.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"})
def log(*a): print(*a); sys.stdout.flush()

def cdx(prefix):
    try:
        r = S.get("http://web.archive.org/cdx/search/cdx",
                  params={"url": prefix, "matchType": "prefix", "output": "text",
                          "fl": "original,timestamp", "collapse": "urlkey", "limit": 400}, timeout=120)
        log("  cdx status", r.status_code, "lines", len(r.text.splitlines()))
        return [tuple(l.split(" ")) for l in r.text.strip().splitlines() if l.strip()]
    except Exception as e:
        log("  cdx err", str(e)[:100]); return []

log("### Kwolek AGH (prefix)")
rows = cdx("home.agh.edu.pl/~kwolek/")
for o, t in rows[:60]:
    log("   ", t, o)

log("### Chicco site (prefix, pdf only)")
rows2 = cdx("https://www.davidechicco.it/")
pdfs = [(o, t) for o, t in rows2 if o.lower().endswith(".pdf")]
log("   total archived:", len(rows2), "pdfs:", len(pdfs))
for o, t in pdfs[:60]:
    log("   ", t, o)
log("FINAL CHECK DONE")
