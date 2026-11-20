# -*- coding: utf-8 -*-
"""Find and download free (open-access) versions of the reference papers."""
import json, os, re, sys, time, urllib.parse
import requests

OUT_DIR = r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\Bibliographie_PDF"
os.makedirs(OUT_DIR, exist_ok=True)

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
HEAD = {"User-Agent": UA, "Accept": "application/pdf,text/html,*/*"}
EMAIL = "paper.download@example.com"

REFS = [
 dict(key="01_Bakshi_Rajan_2021_FewShot_Fall_Siamese",
      title="Few-shot fall detection using shallow siamese network", year=2021,
      authors="Bakshi, Rajan"),
 dict(key="02_Chicco_2021_Siamese_Neural_Networks_Overview",
      title="Siamese neural networks: An overview", year=2021, authors="Chicco"),
 dict(key="03_Droghini_2018_FewShot_Siamese_Audio_Fall",
      title="Few-shot siamese neural networks employing audio features for human-fall detection", year=2018,
      authors="Droghini"),
 dict(key="04_Hadsell_Chopra_LeCun_2006_Dimensionality_Reduction_Invariant_Mapping",
      title="Dimensionality reduction by learning an invariant mapping", year=2006, authors="Hadsell"),
 dict(key="05_Hermans_2017_Triplet_Loss_Person_ReID",
      title="In defense of the triplet loss for person re-identification", year=2017,
      authors="Hermans", arxiv="1703.07737"),
 dict(key="06_Hochreiter_Schmidhuber_1997_LSTM",
      title="Long short-term memory", year=1997, authors="Hochreiter"),
 dict(key="07_Jin_2020_mmFall",
      title="mmFall: Fall detection using 4-D mmWave radar and a hybrid variational RNN autoencoder", year=2020,
      authors="Jin"),
 dict(key="08_Koch_2015_Siamese_OneShot_Image_Recognition",
      title="Siamese neural networks for one-shot image recognition", year=2015, authors="Koch"),
 dict(key="09_Kwolek_Kepski_2014_Fall_Detection_Embedded_Depth",
      title="Human fall detection on embedded platform using depth maps and wireless accelerometer", year=2014,
      authors="Kwolek"),
 dict(key="10_MartinezVillasenor_2019_UPFall_Dataset",
      title="UP-Fall detection dataset: A multimodal approach", year=2019,
      authors="Martinez-Villasenor", doi="10.3390/s19091988"),
 dict(key="11_Musci_2021_Online_Fall_Detection_RNN_Wearable",
      title="Online fall detection using recurrent neural networks on smart wearable devices", year=2021,
      authors="Musci"),
 dict(key="12_Qi_2017_PointNet",
      title="PointNet: Deep learning on point sets for 3D classification and segmentation", year=2017,
      authors="Qi", arxiv="1612.00593"),
 dict(key="13_Santos_2019_Accelerometer_Fall_CNN",
      title="Accelerometer-based human fall detection using convolutional neural networks", year=2019,
      authors="Santos", doi="10.3390/s19071644"),
 dict(key="14_Schroff_2015_FaceNet",
      title="FaceNet: A unified embedding for face recognition and clustering", year=2015,
      authors="Schroff", arxiv="1503.03832"),
 dict(key="15_Snell_2017_Prototypical_Networks",
      title="Prototypical networks for few-shot learning", year=2017,
      authors="Snell", arxiv="1703.05175"),
 dict(key="16_Taramasco_2025_Multimodal_Sensor_Fusion_Fall_Dataset",
      title="Multimodal dataset for sensor fusion in fall detection", year=2025,
      authors="Taramasco", doi="10.7717/peerj.19004"),
 dict(key="17_Tran_2018_MultiModal_MultiView_Fall_Dataset",
      title="A multi-modal multi-view dataset for human fall analysis and preliminary investigation on modality", year=2018,
      authors="Tran"),
 dict(key="18_Wang_2019_Deep_Learning_Sensor_Activity_Survey",
      title="Deep learning for sensor-based activity recognition: A survey", year=2019,
      authors="Wang", arxiv="1707.03502"),
 dict(key="19_Wang_Ellul_Azzopardi_2020_Elderly_Fall_Detection_Survey",
      title="Elderly fall detection systems: A literature survey", year=2020,
      authors="Wang", doi="10.3389/frobt.2020.00071"),
 dict(key="20_Yu_2021_KFall",
      title="A large-scale open motion dataset (KFall) and benchmark algorithms for detecting pre-impact fall of the elderly using wearable inertial sensors", year=2021,
      authors="Yu", doi="10.3389/fnagi.2021.692865"),
]

S = requests.Session()
S.headers.update(HEAD)

def log(*a):
    print(*a); sys.stdout.flush()

def is_pdf(content: bytes) -> bool:
    return content[:5] == b"%PDF-"

def try_download(url, path, expect_pdf=True):
    try:
        r = S.get(url, timeout=60, allow_redirects=True)
    except Exception as e:
        return False, f"request error: {e}"
    if r.status_code != 200:
        return False, f"HTTP {r.status_code}"
    ctype = r.headers.get("Content-Type", "")
    if expect_pdf and (not is_pdf(r.content)):
        return False, f"not a PDF (content-type={ctype}, {len(r.content)} bytes)"
    with open(path, "wb") as f:
        f.write(r.content)
    return True, f"{len(r.content)} bytes from {r.url}"

def arxiv_candidates(arxid):
    return [f"https://arxiv.org/pdf/{arxid}", f"https://arxiv.org/pdf/{arxid}v1"]

def arxiv_search(title):
    q = urllib.parse.quote(f'ti:"{title}"')
    url = f"http://export.arxiv.org/api/query?search_query={q}&max_results=5"
    try:
        r = S.get(url, timeout=40)
        ids = re.findall(r"<id>http://arxiv.org/abs/([^<]+)</id>", r.text)
        return [i for i in ids if i and not i.endswith("/api/query")]
    except Exception:
        return []

def s2_search(title):
    url = ("https://api.semanticscholar.org/graph/v1/paper/search?query="
           + urllib.parse.quote(title) + "&fields=title,year,externalIds,openAccessPdf&limit=5")
    for attempt in range(4):
        try:
            r = S.get(url, timeout=40)
            if r.status_code == 200:
                return r.json().get("data", [])
            time.sleep(4 + attempt * 4)
        except Exception:
            time.sleep(4)
    return []

def unpaywall(doi):
    try:
        r = S.get(f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi)}?email={EMAIL}", timeout=40)
        if r.status_code == 200:
            j = r.json()
            out = []
            best = j.get("best_oa_location")
            if best:
                out.append(best)
            for loc in (j.get("oa_locations") or []):
                if loc not in out:
                    out.append(loc)
            return out
    except Exception:
        pass
    return []

def crossref_doi(title):
    try:
        r = S.get("https://api.crossref.org/works",
                  params={"query.bibliographic": title, "rows": 3,
                          "select": "DOI,title,issued,type"}, timeout=40)
        if r.status_code == 200:
            items = r.json()["message"]["items"]
            for it in items:
                t = (it.get("title") or [""])[0].lower()
                if title.lower()[:40] in t or t[:40] in title.lower():
                    return it.get("DOI")
    except Exception:
        pass
    return None

report = []

for ref in REFS:
    key, title = ref["key"], ref["title"]
    dest = os.path.join(OUT_DIR, key + ".pdf")
    if os.path.exists(dest) and os.path.getsize(dest) > 20000:
        log(f"[skip] {key} already downloaded")
        report.append((key, "OK (already present)", ""))
        continue
    log(f"=== {key} :: {title}")
    done = False

    # 1) arXiv id known / found by title
    arxids = []
    if ref.get("arxiv"):
        arxids.append(ref["arxiv"])
    try:
        arxids += arxiv_search(title)
    except Exception:
        pass
    for a in dict.fromkeys(arxids):
        for u in arxiv_candidates(a):
            ok, msg = try_download(u, dest)
            log(f"   arXiv {a}: {msg}")
            if ok:
                report.append((key, "OK arXiv", f"https://arxiv.org/abs/{a}")); done = True; break
        if done: break

    # 2) DOI -> Unpaywall
    if not done:
        doi = ref.get("doi") or crossref_doi(title)
        if doi:
            log(f"   DOI: {doi}")
            for loc in unpaywall(doi):
                for field in ("url_for_pdf", "url"):
                    u = loc.get(field)
                    if not u: continue
                    ok, msg = try_download(u, dest)
                    log(f"   Unpaywall [{field}] {u}: {msg}")
                    if ok:
                        report.append((key, "OK Unpaywall", u)); done = True; break
                if done: break

    # 3) Semantic Scholar openAccessPdf
    if not done:
        for hit in s2_search(title):
            pdf = (hit.get("openAccessPdf") or {}).get("url")
            if not pdf:
                continue
            ok, msg = try_download(pdf, dest)
            log(f"   S2 {pdf}: {msg}")
            if ok:
                report.append((key, "OK SemanticScholar", pdf)); done = True; break
            time.sleep(1)

    if not done:
        report.append((key, "PAYWALLED / not found", ""))
        log("   -> no free version found")
    time.sleep(1)

log("\n================ SUMMARY ================")
for k, s, u in report:
    log(f"{s:28s} | {k} | {u}")

with open(os.path.join(OUT_DIR, "_download_report.json"), "w", encoding="utf-8") as f:
    json.dump([{"paper": k, "status": s, "url": u} for k, s, u in report],
              f, ensure_ascii=False, indent=2)
