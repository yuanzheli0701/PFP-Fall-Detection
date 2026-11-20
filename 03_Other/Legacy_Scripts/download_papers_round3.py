# -*- coding: utf-8 -*-
import io, os, re, sys, tarfile, time, urllib.parse, xml.etree.ElementTree as ET
import requests
sys.stdout.reconfigure(encoding="utf-8")
OUT = r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\Bibliographie_PDF"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
S = requests.Session(); S.headers.update({"User-Agent": UA})
def log(*a):
    print(*a); sys.stdout.flush()

def pmc_oa_pdf(pmcid, dest):
    """Use NCBI OA web service to get the OA package and extract the PDF."""
    try:
        r = S.get("https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi", params={"id": pmcid}, timeout=60)
        log("   oa.fcgi:", r.status_code, r.text[:300].replace("\n", " "))
        if r.status_code != 200:
            return False
        root = ET.fromstring(r.text)
        links = root.findall(".//link")
        hrefs = [l.get("href") for l in links]
        for href in hrefs:
            if not href: continue
            url = href.replace("ftp://", "https://")
            if url.endswith(".tar.gz"):
                rr = S.get(url, timeout=120)
                if rr.status_code != 200:
                    log("   pkg", url, "->", rr.status_code); continue
                tf = tarfile.open(fileobj=io.BytesIO(rr.content), mode="r:gz")
                pdfs = [m for m in tf.getmembers() if m.name.lower().endswith(".pdf")]
                if pdfs:
                    data = tf.extractfile(pdfs[0]).read()
                    if data[:5] == b"%PDF-":
                        open(dest, "wb").write(data)
                        log("   extracted %s (%dB) from %s" % (pdfs[0].name, len(data), url))
                        return True
            elif url.endswith(".pdf"):
                rr = S.get(url, timeout=120)
                if rr.status_code == 200 and rr.content[:5] == b"%PDF-":
                    open(dest, "wb").write(rr.content)
                    log("   got %dB from %s" % (len(rr.content), url))
                    return True
    except Exception as e:
        log("   pmc_oa err", e)
    return False

JOBS = [
 ("10_MartinezVillasenor_2019_UPFall_Dataset.pdf", "PMC6539235"),
 ("13_Santos_2019_Accelerometer_Fall_CNN.pdf", "PMC6480090"),
 ("16_Taramasco_2025_Multimodal_Sensor_Fusion_Fall_Dataset.pdf", "PMC11970414"),
]
for fname, pmcid in JOBS:
    log("=== " + fname + "  (" + pmcid + ")")
    ok = pmc_oa_pdf(pmcid, os.path.join(OUT, fname))
    if not ok:
        log("   -> OA service failed")
    time.sleep(1)

# Kwolek: check personal page for a free copy
log("=== Kwolek homepage scan")
try:
    r = S.get("http://home.agh.edu.pl/~kwolek/", timeout=40)
    log("   status", r.status_code, len(r.text))
    links = re.findall(r'href=["\']([^"\']+)["\']', r.text)
    for l in links:
        if "pdf" in l.lower() or "pub" in l.lower():
            log("   link:", l)
except Exception as e:
    log("   err", e)

# arXiv search for Tran multi-modal multi-view fall dataset
log("=== arXiv search Tran multi-modal multi-view")
try:
    q = urllib.parse.quote('all:"multi-modal multi-view dataset for human fall"')
    r = S.get("http://export.arxiv.org/api/query?search_query=%s&max_results=5" % q, timeout=40)
    ids = re.findall(r"<id>http://arxiv.org/abs/([^<]+)</id>", r.text)
    log("   ids:", ids)
    titles = re.findall(r"<title>([^<]+)</title>", r.text)
    for t in titles: log("   title:", t[:110])
except Exception as e:
    log("   err", e)
log("ROUND3 DONE")
