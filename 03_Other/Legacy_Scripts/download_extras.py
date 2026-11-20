# -*- coding: utf-8 -*-
import os, sys, time, urllib.parse
import requests
sys.stdout.reconfigure(encoding="utf-8")
SUB = r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\Bibliographie_PDF\Complements"
os.makedirs(SUB, exist_ok=True)
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
S = requests.Session(); S.headers.update({"User-Agent": UA, "Accept": "application/pdf,*/*"})
def log(*a): print(*a); sys.stdout.flush()

def dl(url, dest, label, referer=None):
    h = {}
    if referer: h["Referer"] = referer
    try:
        r = S.get(url, timeout=120, headers=h, allow_redirects=True)
    except Exception as e:
        log("   ERR [%s] %s" % (label, str(e)[:90])); return False
    if r.status_code == 200 and r.content[:5] == b"%PDF-":
        open(dest, "wb").write(r.content)
        log("   OK [%s] %dB <- %s" % (label, len(r.content), r.url)); return True
    log("   fail [%s] HTTP %s ct=%s" % (label, r.status_code, r.headers.get("Content-Type"))); return False

JOBS = [
 ("A1_Wang_Yan_Oates_2016_Time_Series_Classification_Strong_Baseline_arXiv1611.06455.pdf",
  ["https://arxiv.org/pdf/1611.06455"], None),
 ("A2_Baltrusaitis_2019_Multimodal_Machine_Learning_Survey_Taxonomy_arXiv1705.09406.pdf",
  ["https://arxiv.org/pdf/1705.09406"], None),
 ("B1_Dumoulin_Visin_2016_Guide_Convolution_Arithmetic_arXiv1603.07285.pdf",
  ["https://arxiv.org/pdf/1603.07285"], None),
 ("B2_Greff_2015_LSTM_Search_Space_Odyssey_arXiv1503.04069.pdf",
  ["https://arxiv.org/pdf/1503.04069"], None),
 ("C1_CasilariPerez_GarciaLagos_2020_CNN_Fall_Detection_Multiple_Datasets_Sensors.pdf",
  ["https://mdpi-res.com/d_attachment/sensors/sensors-20-01466/article_deploy/sensors-20-01466.pdf"], "https://www.mdpi.com/"),
 ("C2_Sucerquia_2017_SisFall_Dataset_Sensors.pdf",
  ["https://mdpi-res.com/d_attachment/sensors/sensors-17-00198/article_deploy/sensors-17-00198.pdf"], "https://www.mdpi.com/"),
]
for fname, urls, ref in JOBS:
    dest = os.path.join(SUB, fname)
    log("=== " + fname)
    if os.path.exists(dest) and os.path.getsize(dest) > 50000:
        log("   already present"); continue
    for u in urls:
        if dl(u, dest, "direct", ref): break
    time.sleep(1)

# Lie et al. 2019 JBHI — check OA
log("### Lie et al. 2019 (IEEE JBHI) OA check")
for api, q in [("https://api.openalex.org/works/doi:", "10.1109/jbhi.2018.2808281")]:
    try:
        r = S.get(api + urllib.parse.quote(q), params={"mailto": "research@example.com"}, timeout=60)
        j = r.json()
        oa = j.get("open_access", {})
        log("   is_oa:", oa.get("is_oa"), "| best:", (j.get("best_oa_location") or {}).get("pdf_url"))
    except Exception as e:
        log("   err", str(e)[:90])
try:
    r = S.get("https://api.semanticscholar.org/graph/v1/paper/DOI:" + urllib.parse.quote("10.1109/JBHI.2018.2808281"),
              params={"fields": "title,openAccessPdf"}, timeout=60)
    j = r.json()
    log("   S2:", j.get("title"), "| oa:", (j.get("openAccessPdf") or {}).get("url"))
except Exception as e:
    log("   s2 err", str(e)[:90])
log("EXTRA DOWNLOAD DONE")
