# -*- coding: utf-8 -*-
import os, re, sys, time
import requests
sys.stdout.reconfigure(encoding="utf-8")
OUT = r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\Bibliographie_PDF"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
H = {"User-Agent": UA,
     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
     "Accept-Language": "en-US,en;q=0.9",
     "Sec-Fetch-Dest": "document", "Sec-Fetch-Mode": "navigate",
     "Sec-Fetch-Site": "none", "Upgrade-Insecure-Requests": "1"}
S = requests.Session(); S.headers.update(H)
def log(*a):
    print(*a); sys.stdout.flush()

def save_pdf(r, dest, label):
    if r.status_code == 200 and r.content[:5] == b"%PDF-":
        open(dest, "wb").write(r.content)
        log("   OK [%s] %dB <- %s" % (label, len(r.content), r.url))
        return True
    log("   fail [%s] HTTP %s ct=%s size=%s" % (label, r.status_code, r.headers.get("Content-Type"), len(r.content)))
    return False

def from_pmc_landing(pmcid, dest):
    """Fetch PMC landing page, find citation_pdf_url, then download."""
    url = "https://pmc.ncbi.nlm.nih.gov/articles/%s/" % pmcid
    try:
        r = S.get(url, timeout=60)
        log("   landing %s -> %s (%dB)" % (pmcid, r.status_code, len(r.content)))
        if r.status_code != 200: return False
        m = re.search(r'<meta[^>]+name="citation_pdf_url"[^>]+content="([^"]+)"', r.text)
        if not m:
            m = re.search(r'content="([^"]+\.pdf[^"]*)"[^>]*name="citation_pdf_url"', r.text)
        if m:
            pdfurl = m.group(1)
            log("   citation_pdf_url:", pdfurl)
            r2 = S.get(pdfurl, timeout=120, headers={"Referer": url, "Sec-Fetch-Dest": "document"},
                       allow_redirects=True)
            return save_pdf(r2, dest, pmcid)
        else:
            log("   no citation_pdf_url in landing page")
    except Exception as e:
        log("   pmc landing err", e)
    return False

JOBS = [
 ("10_MartinezVillasenor_2019_UPFall_Dataset.pdf",
  ["https://res.mdpi.com/d_attachment/sensors/sensors-19-01988/article_deploy/sensors-19-01988.pdf",
   "https://res.mdpi.com/sensors/sensors-19-01988/article_deploy/sensors-19-01988.pdf?filename=&attachment=1"],
  "PMC6539235"),
 ("13_Santos_2019_Accelerometer_Fall_CNN.pdf",
  ["https://res.mdpi.com/d_attachment/sensors/sensors-19-01644/article_deploy/sensors-19-01644.pdf"],
  "PMC6480090"),
 ("16_Taramasco_2025_Multimodal_Sensor_Fusion_Fall_Dataset.pdf",
  ["https://peerj.com/articles/19004.pdf?download=1"],
  "PMC11970414"),
]
for fname, cands, pmcid in JOBS:
    dest = os.path.join(OUT, fname)
    log("=== " + fname)
    if os.path.exists(dest) and os.path.getsize(dest) > 100000:
        log("   already present"); continue
    done = False
    for u in cands:
        try:
            r = S.get(u, timeout=90, headers={"Referer": "https://www.google.com/",
                                              "Sec-Fetch-Site": "cross-site"}, allow_redirects=True)
            if save_pdf(r, dest, "mirror"): done = True; break
        except Exception as e:
            log("   mirror err", str(e)[:90])
    if not done:
        done = from_pmc_landing(pmcid, dest)
    if not done:
        log("   -> failed")
    time.sleep(2)
log("ROUND4 DONE")
