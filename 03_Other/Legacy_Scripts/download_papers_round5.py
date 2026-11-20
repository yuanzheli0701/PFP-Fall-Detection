# -*- coding: utf-8 -*-
import os, sys, time, json
import requests
sys.stdout.reconfigure(encoding="utf-8")
OUT = r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\Bibliographie_PDF"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
S = requests.Session(); S.headers.update({"User-Agent": UA, "Accept": "*/*"})
def log(*a):
    print(*a); sys.stdout.flush()

DOIS = {
 "16_Taramasco_2025_Multimodal_Sensor_Fusion_Fall_Dataset.pdf": "10.7717/peerj.19004",
 "01_Bakshi_Rajan_2021_FewShot_Fall_Siamese.pdf": "10.1109/memea52024.2021.9478605",
 "02_Chicco_2021_Siamese_Neural_Networks_Overview.pdf": "10.1007/978-1-0716-0826-5_3",
 "03_Droghini_2018_FewShot_Siamese_Audio_Fall.pdf": "10.1145/3243250.3243268",
 "09_Kwolek_Kepski_2014_Fall_Detection_Embedded_Depth.pdf": "10.1016/j.cmpb.2014.09.005",
 "17_Tran_2018_MultiModal_MultiView_Fall_Dataset.pdf": "10.1109/icpr.2018.8546308",
}

def fatcat_files(doi):
    try:
        r = S.get("https://api.fatcat.wiki/v0/release/lookup",
                  params={"doi": doi, "expand": "files", "hide": "abstracts,refs"}, timeout=60)
        log("   fatcat:", r.status_code)
        if r.status_code == 200:
            j = r.json()
            urls = []
            for f in (j.get("files") or []):
                for u in (f.get("urls") or []):
                    urls.append(u.get("url"))
            return urls
    except Exception as e:
        log("   fatcat err", str(e)[:120])
    return []

def try_dl(url, dest, label):
    try:
        r = S.get(url, timeout=120, allow_redirects=True,
                  headers={"Accept": "application/pdf,*/*"})
    except Exception as e:
        log("   dl err [%s] %s" % (label, str(e)[:100])); return False
    if r.status_code == 200 and r.content[:5] == b"%PDF-":
        open(dest, "wb").write(r.content)
        log("   OK [%s] %dB <- %s" % (label, len(r.content), r.url))
        return True
    log("   fail [%s] HTTP %s ct=%s size=%s" % (label, r.status_code, r.headers.get("Content-Type"), len(r.content)))
    return False

for fname, doi in DOIS.items():
    dest = os.path.join(OUT, fname)
    if os.path.exists(dest) and os.path.getsize(dest) > 100000:
        log("=== %s already present" % fname); continue
    log("=== %s (%s)" % (fname, doi))
    urls = fatcat_files(doi)
    for u in urls:
        log("   candidate:", u)
    done = False
    for u in urls:
        if u.lower().endswith(".pdf") or "pdf" in u.lower():
            if try_dl(u, dest, "fatcat"):
                done = True; break
    if not done and urls:
        for u in urls[:3]:
            if try_dl(u, dest, "fatcat-any"):
                done = True; break
    if not done:
        log("   -> no OA file via fatcat")
    time.sleep(1)
log("ROUND5 DONE")
