# -*- coding: utf-8 -*-
import re, sys
import docx
sys.stdout.reconfigure(encoding="utf-8")
d = docx.Document("State of the art - shared (revu).docx")
paras = [(p.style.name or "", p.text.strip()) for p in d.paragraphs if p.text.strip()]
probes = {
 "Kwolek": [r"Kwolek", r"embedded platform", r"depth map", r"wireless accelerometer"],
 "Martinez / UP-Fall": [r"UP-Fall", r"UP Fall", r"Mart[ií]nez"],
 "Tran / multi-modal multi-view": [r"multi-modal multi-view", r"multimodal multi-view", r"Tran"],
 "Yu / KFall": [r"KFall", r"K-Fall", r"pre-impact"],
 "Wang & Oates 2016": [r"Oates", r"from scratch", r"Strong Baseline"],
 "Baltrusaitis / fusion taxonomy": [r"Baltrusaitis", r"taxonomy", r"early.*fusion.*late"],
}
for label, pats in probes.items():
    print("### " + label)
    for i, (st, t) in enumerate(paras):
        for pat in pats:
            if re.search(pat, t, re.I):
                print("   [%3d] (%s) %s" % (i, st, t[:150]))
                break
    print()
