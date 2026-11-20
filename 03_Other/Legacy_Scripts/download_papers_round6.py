# -*- coding: utf-8 -*-
import os, sys, time, urllib.parse
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

def openalex(doi):
    try:
        r = S.get("https://api.openalex.org/works/doi:" + urllib.parse.quote(doi),
                  params={"mailto": "research@example.com"}, timeout=60)
        log("   openalex:", r.status_code)
        if r.status_code == 200:
            j = r.json()
            locs = []
            b = j.get("best_oa_location")
            if b: locs.append(b)
            for l in (j.get("locations") or []):
                if l.get("is_oa"): locs.append(l)
            out = []
            for l in locs:
                if l.get("pdf_url"): out.append(l["pdf_url"])
                if l.get("landing_page_url"): out.append(l["landing_page_url"])
            # dedupe
            seen, res = set(), []
            for u in out:
                if u not in seen:
                    seen.add(u); res.append(u)
            return j.get("open_access", {}).get("is_oa"), res
    except Exception as e:
        log("   openalex err", str(e)[:120])
    return None, []

def try_dl(url, dest, label):
    try:
        r = S.get(url, timeout=120, allow_redirects=True, headers={"Accept": "application/pdf,*/*"})
    except Exception as e:
        log("   dl err [%s] %s" % (label, str(e)[:100])); return False
    if r.status_code == 200 and r.content[:5] == b"%PDF-":
        open(dest, "wb").write(r.content)
        log("   OK [%s] %dB <- %s" % (label, len(r.content), r.url))
        return True
    log("   fail [%s] HTTP %s ct=%s size=%s" % (label, r.status_code, r.headers.get("Content-Type"), len(r.content)))
    return False

CAND = {
 # extra hand-picked candidates tried before OpenAlex
 "16_Taramasco_2025_Multimodal_Sensor_Fusion_Fall_Dataset.pdf": [
   "https://web.archive.org/web/2025id_/https://peerj.com/articles/19004.pdf",
   "https://europepmc.org/api/fulltextRepo?pprId=PMC11970414&type=FILE&fileName=EMS.pdf",
 ],
 "09_Kwolek_Kepski_2014_Fall_Detection_Embedded_Depth.pdf": [
   "https://web.archive.org/web/2020id_/http://home.agh.edu.pl/~kwolek/papers/kwolek_kepski_cmpb2014.pdf",
   "https://web.archive.org/web/2020id_/http://home.agh.edu.pl/~kwolek/",
 ],
}

for fname, doi in DOIS.items():
    dest = os.path.join(OUT, fname)
    if os.path.exists(dest) and os.path.getsize(dest) > 100000:
        log("=== %s already present" % fname); continue
    log("=== %s (%s)" % (fname, doi))
    done = False
    for u in CAND.get(fname, []):
        if u.endswith("/") or "web.archive.org" in u and not u.lower().endswith(".pdf"):
            continue
        if try_dl(u, dest, "wayback"): done = True; break
    if not done:
        is_oa, urls = openalex(doi)
        log("   is_oa =", is_oa)
        for u in urls: log("   loc:", u)
        for u in urls:
            if u and u.lower().split("?")[0].endswith(".pdf"):
                if try_dl(u, dest, "openalex"): done = True; break
    if not done:
        log("   -> no free PDF found")
    time.sleep(1)
log("ROUND6 DONE")
