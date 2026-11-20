# -*- coding: utf-8 -*-
import json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
D = r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\Bibliographie_PDF"
report = json.load(open(os.path.join(D, "_download_report.json"), encoding="utf-8"))
have = {r["description"].split(" - ")[0]: r for r in report if r["status"] == "downloaded"}

ROWS = [
 ("1",  "Bakshi & Rajan (2021)",            "Few-shot fall detection using shallow siamese network", "Few-shot fall detection"),
 ("2",  "Chicco (2021)",                    "Siamese neural networks: An overview", "Siamese networks and contrastive loss"),
 ("3",  "Droghini et al. (2018)",           "Few-shot siamese neural networks employing audio features", "Few-shot fall detection"),
 ("4",  "Hadsell, Chopra & LeCun (2006)",   "Dimensionality reduction by learning an invariant mapping", "Siamese networks and contrastive loss"),
 ("5",  "Hermans, Beyer & Leibe (2017)",    "In defense of the triplet loss for person re-identification", "Triplet networks and triplet loss"),
 ("6",  "Hochreiter & Schmidhuber (1997)",  "Long short-term memory", "LSTM-based approaches"),
 ("7",  "Jin, Sengupta & Cao (2020)",       "mmFall", "Ambient sensors: mmWave radar ; LSTM-based approaches"),
 ("8",  "Koch, Zemel & Salakhutdinov (2015)","Siamese neural networks for one-shot image recognition", "Principle ; Siamese networks and contrastive loss"),
 ("9",  "Kwolek & Kepski (2014)",           "Human fall detection on embedded platform", "Tableau 1 - URFall"),
 ("10", "Martinez-Villasenor et al. (2019)","UP-Fall detection dataset", "Tableau 1 - UP-Fall"),
 ("11", "Musci et al. (2021)",              "Online fall detection using RNN on smart wearable devices", "LSTM-based approaches"),
 ("12", "Qi et al. (2017)",                 "PointNet", "Ambient sensors: mmWave radar"),
 ("13", "Santos et al. (2019)",             "Accelerometer-based human fall detection using CNN", "CNN-based approaches"),
 ("14", "Schroff, Kalenichenko & Philbin (2015)", "FaceNet", "Triplet networks and triplet loss"),
 ("15", "Snell, Swersky & Zemel (2017)",    "Prototypical networks for few-shot learning", "Principle ; Prototype-based classification"),
 ("16", "Taramasco et al. (2025)",          "Multimodal dataset for sensor fusion in fall detection", "Introduction ; Sensing modalities ; Public datasets ; Multimodal sensor fusion"),
 ("17", "Tran et al. (2018)",               "A multi-modal multi-view dataset for human fall analysis", "Tableau 1 - CMDFall"),
 ("18", "Wang, Chen, Hao, Peng & Hu (2019)","Deep learning for sensor-based activity recognition: A survey", "Supervised deep learning for fall detection"),
 ("19", "Wang, Ellul & Azzopardi (2020)",   "Elderly fall detection systems: A literature survey", "Multimodal sensor fusion"),
 ("20", "Yu, Jang & Xiong (2021)",          "A large-scale open motion dataset (KFall)", "Tableau 1 - KFall"),
]

FILE_BY_NUM = {
 "4": "04_Hadsell_Chopra_LeCun_2006_Dimensionality_Reduction_Invariant_Mapping.pdf",
 "5": "05_Hermans_2017_Triplet_Loss_Person_ReID.pdf",
 "6": "06_Hochreiter_Schmidhuber_1997_LSTM.pdf",
 "7": "07_Jin_2020_mmFall.pdf",
 "8": "08_Koch_2015_Siamese_OneShot_Image_Recognition.pdf",
 "10": "10_MartinezVillasenor_2019_UPFall_Dataset.pdf",
 "11": "11_Musci_2021_Online_Fall_Detection_RNN_Wearable.pdf",
 "12": "12_Qi_2017_PointNet.pdf",
 "13": "13_Santos_2019_Accelerometer_Fall_CNN.pdf",
 "14": "14_Schroff_2015_FaceNet.pdf",
 "15": "15_Snell_2017_Prototypical_Networks.pdf",
 "16": "16_Taramasco_2025_Multimodal_Sensor_Fusion_Fall_Dataset.pdf",
 "18": "18_Wang_2019_Deep_Learning_Sensor_Activity_Survey.pdf",
 "19": "19_Wang_Ellul_Azzopardi_2020_Elderly_Fall_Detection_Survey.pdf",
 "20": "20_Yu_2021_KFall.pdf",
}
PAYWALL_DOI = {
 "1": "https://doi.org/10.1109/MeMeA52024.2021.9478605",
 "2": "https://doi.org/10.1007/978-1-0716-0826-5_3",
 "3": "https://doi.org/10.1145/3243250.3243268",
 "9": "https://doi.org/10.1016/j.cmpb.2014.09.005",
 "17": "https://doi.org/10.1109/ICPR.2018.8546308",
}
NOTE = {
 "7": "arXiv 预印本(与期刊版内容一致)",
 "11": "arXiv 预印本(期刊版为 IEEE TETC 2021)",
 "18": "arXiv 预印本(期刊版为 Pattern Recognition Letters 119)",
}

L = []
L.append("# 对照表 — 报告参考文献 ↔ 已下载 PDF")
L.append("")
L.append("来源文档: `State of the art - shared (revu).docx`(20 条参考文献) | 生成日期: 2026-09-28")
L.append("")
L.append("| # | 参考文献 | 报告中的引用位置 | PDF | 文件 |")
L.append("|---|---|---|---|---|")
for num, cite, title, where in ROWS:
    f = FILE_BY_NUM.get(num)
    mark = "✅" if f else "❌ 付费"
    cell = ("`%s`" % f) if f else "[%s](%s)" % (PAYWALL_DOI[num], PAYWALL_DOI[num])
    if num in NOTE:
        cell += "<br><sub>%s</sub>" % NOTE[num]
    L.append("| %s | %s | %s | %s | %s |" % (num, cite, where, mark, cell))
L.append("")
L.append("**统计**: 20 篇中 15 篇已配 PDF(75%);5 篇因付费订阅未下载(No. 1, 2, 3, 9, 17),DOI 链接见上表。")
L.append("")
L.append("## 备注")
L.append("- No. 9、10、17、20 只在数据集对比表(Tableau 1)中被引用,正文未单独讨论 —— 若要消减参考文献可优先考虑这 4 条。")
L.append("- No. 11、18、7 下载的是作者预印本(arXiv),页码与期刊版不同,引用页码时需以正式版为准。")
L.append("- 评审建议补充的参考文献(尚未配 PDF):Wang, Yan & Oates (2016, arXiv:1611.06455);以及 early/intermediate/late fusion 分类体系的出处。")
open(os.path.join(D, "Correspondance_rapport_PDF.md"), "w", encoding="utf-8").write("\n".join(L))
print("\n".join(L))
