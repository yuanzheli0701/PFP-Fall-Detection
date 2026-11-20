# -*- coding: utf-8 -*-
import json, os, sys, time, urllib.parse
import requests

sys.stdout.reconfigure(encoding="utf-8")
OUT = r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\Bibliographie_PDF"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
H = {"User-Agent": UA, "Accept": "application/pdf,text/html;q=0.9,*/*;q=0.8",
     "Accept-Language": "en-US,en;q=0.9"}
S = requests.Session(); S.headers.update(H)

def log(*a):
    print(*a); sys.stdout.flush()

def dl(url, path, referer=None):
    hh = dict(H)
    if referer: hh["Referer"] = referer
    try:
        r = S.get(url, timeout=90, headers=hh, allow_redirects=True)
    except Exception as e:
        return False, "ERR " + str(e)[:100]
    if r.status_code != 200:
        return False, "HTTP %s" % r.status_code
    if r.content[:5] != b"%PDF-":
        return False, "not pdf (%s, %dB)" % (r.headers.get("Content-Type"), len(r.content))
    open(path, "wb").write(r.content)
    return True, "%dB <- %s" % (len(r.content), r.url)

def europepmc_by_doi(doi):
    try:
        r = S.get("https://www.ebi.ac.uk/europepmc/webservices/rest/search",
                  params={"query": 'DOI:"%s"' % doi, "format": "json", "resultType": "core"}, timeout=60)
        if r.status_code == 200:
            res = r.json().get("resultList", {}).get("result", [])
            if res: return res[0]
    except Exception as e:
        log("   epmc err", e)
    return None

def s2_by_doi(doi):
    try:
        r = S.get("https://api.semanticscholar.org/graph/v1/paper/DOI:" + urllib.parse.quote(doi),
                  params={"fields": "title,openAccessPdf,externalIds"}, timeout=60)
        if r.status_code == 200: return r.json()
    except Exception: pass
    return None

def try_list(cands, dest, label):
    for u, ref in cands:
        ok, msg = dl(u, dest, referer=ref)
        log("   [%s] %s -> %s" % (label, u, msg))
        if ok: return u
    return None

JOBS = [
 dict(key="06", fname="06_Hochreiter_Schmidhuber_1997_LSTM.pdf",
      cands=[("https://www.bioinf.jku.at/publications/older/2604.pdf", None),
             ("https://web.archive.org/web/2023id_/https://www.bioinf.jku.at/publications/older/2604.pdf", None)]),
 dict(key="08", fname="08_Koch_2015_Siamese_OneShot_Image_Recognition.pdf",
      cands=[("https://www.cs.utoronto.ca/~rsalakhu/papers/oneshot1.pdf", None),
             ("https://www.cs.cmu.edu/~rsalakhu/papers/oneshot1.pdf", None),
             ("https://web.archive.org/web/2022id_/http://www.cs.utoronto.ca/~rsalakhu/papers/oneshot1.pdf", None)]),
 dict(key="04", fname="04_Hadsell_Chopra_LeCun_2006_Dimensionality_Reduction_Invariant_Mapping.pdf",
      cands=[("http://yann.lecun.com/exdb/publis/pdf/hadsell-chopra-lecun-06.pdf", None),
             ("https://web.archive.org/web/2019id_/http://yann.lecun.com/exdb/publis/pdf/hadsell-chopra-lecun-06.pdf", None),
             ("https://web.archive.org/web/2023id_/http://yann.lecun.com/exdb/publis/pdf/hadsell-chopra-lecun-06.pdf", None)]),
 dict(key="20", fname="20_Yu_2021_KFall.pdf", doi="10.3389/fnagi.2021.692865",
      cands=[("https://www.frontiersin.org/journals/aging-neuroscience/articles/10.3389/fnagi.2021.692865/pdf", "https://www.frontiersin.org/"),
             ("https://www.frontiersin.org/articles/10.3389/fnagi.2021.692865/pdf", "https://www.frontiersin.org/")]),
 dict(key="10", fname="10_MartinezVillasenor_2019_UPFall_Dataset.pdf", doi="10.3390/s19091988",
      cands=[("https://www.mdpi.com/1424-8220/19/9/1988/pdf", "https://www.mdpi.com/")]),
 dict(key="13", fname="13_Santos_2019_Accelerometer_Fall_CNN.pdf", doi="10.3390/s19071644",
      cands=[("https://www.mdpi.com/1424-8220/19/7/1644/pdf", "https://www.mdpi.com/")]),
 dict(key="16", fname="16_Taramasco_2025_Multimodal_Sensor_Fusion_Fall_Dataset.pdf", doi="10.7717/peerj.19004",
      cands=[("https://peerj.com/articles/19004.pdf", "https://peerj.com/articles/19004/")]),
 dict(key="02", fname="02_Chicco_2021_Siamese_Neural_Networks_Overview.pdf", doi="10.1007/978-1-0716-0826-5_3", cands=[]),
 dict(key="01", fname="01_Bakshi_Rajan_2021_FewShot_Fall_Siamese.pdf", doi="10.1109/memea52024.2021.9478605", cands=[]),
 dict(key="03", fname="03_Droghini_2018_FewShot_Siamese_Audio_Fall.pdf", doi="10.1145/3243250.3243268", cands=[]),
 dict(key="07", fname="07_Jin_2020_mmFall.pdf", doi="10.1109/tase.2020.3042158", cands=[]),
 dict(key="09", fname="09_Kwolek_Kepski_2014_Fall_Detection_Embedded_Depth.pdf", doi="10.1016/j.cmpb.2014.09.005", cands=[]),
 dict(key="17", fname="17_Tran_2018_MultiModal_MultiView_Fall_Dataset.pdf", doi="10.1109/icpr.2018.8546308", cands=[]),
]

log("##### ROUND 2")
for job in JOBS:
    dest = os.path.join(OUT, job["fname"])
    log("=== " + job["fname"])
    got = try_list(job["cands"], dest, "direct")
    if not got and job.get("doi"):
        rec = europepmc_by_doi(job["doi"])
        if rec:
            pmcid = rec.get("pmcid")
            log("   EuropePMC: pmcid=%s isOpenAccess=%s" % (pmcid, rec.get("isOpenAccess")))
            if pmcid and str(rec.get("isOpenAccess", "")).upper() == "Y":
                for u in ["https://www.ebi.ac.uk/europepmc/webservices/rest/%s/fullTextPDF" % pmcid,
                          "https://europepmc.org/articles/%s?pdf=render" % pmcid,
                          "https://pmc.ncbi.nlm.nih.gov/articles/%s/pdf/" % pmcid]:
                    ok, msg = dl(u, dest, referer="https://europepmc.org/")
                    log("   [%s] %s -> %s" % (pmcid, u, msg))
                    if ok: got = u; break
        rec2 = s2_by_doi(job["doi"])
        if rec2:
            pdf = (rec2.get("openAccessPdf") or {}).get("url")
            log("   S2 exact: %s | oa=%s" % ((rec2.get("title") or "")[:80], pdf))
            if pdf and not got:
                ok, msg = dl(pdf, dest)
                log("   [S2] %s -> %s" % (pdf, msg))
                if ok: got = pdf
    if not got:
        log("   -> still not available for free")
    time.sleep(1)
log("ROUND2 DONE")
