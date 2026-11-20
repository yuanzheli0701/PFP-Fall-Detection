# -*- coding: utf-8 -*-
import json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
D = r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\Bibliographie_PDF"

OK = [
 ("04_Hadsell_Chopra_LeCun_2006_Dimensionality_Reduction_Invariant_Mapping.pdf",
  "Hadsell, Chopra & LeCun (2006) - Dimensionality Reduction by Learning an Invariant Mapping (CVPR)",
  "https://yann.lecun.com/exdb/publis/pdf/hadsell-chopra-lecun-06.pdf", "作者官方主页(Yann LeCun)"),
 ("05_Hermans_2017_Triplet_Loss_Person_ReID.pdf",
  "Hermans, Beyer & Leibe (2017) - In Defense of the Triplet Loss for Person Re-Identification (arXiv)",
  "https://arxiv.org/abs/1703.07737", "arXiv 开放获取"),
 ("06_Hochreiter_Schmidhuber_1997_LSTM.pdf",
  "Hochreiter & Schmidhuber (1997) - Long Short-Term Memory (Neural Computation)",
  "https://www.bioinf.jku.at/publications/older/2604.pdf", "作者机构 JKU Linz 官方副本"),
 ("07_Jin_2020_mmFall.pdf",
  "Jin, Sengupta & Cao (2020) - mmFall (IEEE TASE 的 arXiv 预印本 Preprint)",
  "https://arxiv.org/abs/2003.02386", "arXiv 开放获取"),
 ("08_Koch_2015_Siamese_OneShot_Image_Recognition.pdf",
  "Koch, Zemel & Salakhutdinov (2015) - Siamese Neural Networks for One-shot Image Recognition (ICML Workshop)",
  "https://www.cs.utoronto.ca/~rsalakhu/papers/oneshot1.pdf", "多伦多大学作者主页"),
 ("10_MartinezVillasenor_2019_UPFall_Dataset.pdf",
  "Martinez-Villasenor et al. (2019) - UP-Fall Detection Dataset: A Multimodal Approach (Sensors, MDPI)",
  "https://www.mdpi.com/1424-8220/19/9/1988", "开放获取期刊 MDPI (官方 PDF)"),
 ("11_Musci_2021_Online_Fall_Detection_RNN_Wearable.pdf",
  "Musci et al. (2021) - Online Fall Detection using RNN on Smart Wearable Devices (IEEE TETC 的 arXiv 预印本)",
  "https://arxiv.org/abs/1804.04976", "arXiv 开放获取(预印本)"),
 ("12_Qi_2017_PointNet.pdf",
  "Qi et al. (2017) - PointNet: Deep Learning on Point Sets (CVPR)",
  "https://arxiv.org/abs/1612.00593", "arXiv 开放获取"),
 ("13_Santos_2019_Accelerometer_Fall_CNN.pdf",
  "Santos et al. (2019) - Accelerometer-Based Human Fall Detection Using CNN (Sensors, MDPI)",
  "https://www.mdpi.com/1424-8220/19/7/1644", "开放获取期刊 MDPI (官方 PDF)"),
 ("14_Schroff_2015_FaceNet.pdf",
  "Schroff, Kalenichenko & Philbin (2015) - FaceNet (CVPR)",
  "https://arxiv.org/abs/1503.03832", "arXiv 开放获取"),
 ("15_Snell_2017_Prototypical_Networks.pdf",
  "Snell, Swersky & Zemel (2017) - Prototypical Networks for Few-shot Learning (NeurIPS)",
  "https://arxiv.org/abs/1703.05175", "arXiv 开放获取"),
 ("16_Taramasco_2025_Multimodal_Sensor_Fusion_Fall_Dataset.pdf",
  "Taramasco et al. (2025) - Multimodal dataset for sensor fusion in fall detection (PeerJ)",
  "https://doi.org/10.7717/peerj.19004", "开放获取期刊 PeerJ (经 Wayback Machine 官方存档)"),
 ("18_Wang_2019_Deep_Learning_Sensor_Activity_Survey.pdf",
  "Wang et al. (2019) - Deep Learning for Sensor-based Activity Recognition: A Survey (PRL, arXiv 预印本)",
  "https://arxiv.org/abs/1707.03502", "arXiv 开放获取"),
 ("19_Wang_Ellul_Azzopardi_2020_Elderly_Fall_Detection_Survey.pdf",
  "Wang, Ellul & Azzopardi (2020) - Elderly Fall Detection Systems: A Literature Survey (Frontiers in Robotics and AI)",
  "https://doi.org/10.3389/frobt.2020.00071", "开放获取期刊 Frontiers"),
 ("20_Yu_2021_KFall.pdf",
  "Yu, Jang & Xiong (2021) - KFall dataset (Frontiers in Aging Neuroscience)",
  "https://doi.org/10.3389/fnagi.2021.692865", "开放获取期刊 Frontiers"),
]

PAYWALLED = [
 ("Bakshi & Rajan (2021) - Few-shot fall detection using shallow siamese network (IEEE MeMeA)",
  "https://doi.org/10.1109/MeMeA52024.2021.9478605", "IEEE Xplore,需付费订阅,无免费版本"),
 ("Chicco (2021) - Siamese Neural Networks: An Overview (Springer, 书籍章节)",
  "https://doi.org/10.1007/978-1-0716-0826-5_3", "Springer,书籍章节需付费,无免费版本"),
 ("Droghini et al. (2018) - Few-shot siamese neural networks employing audio features (ACM ICPRAI)",
  "https://doi.org/10.1145/3243250.3243268", "ACM Digital Library,需付费,无免费版本"),
 ("Kwolek & Kepski (2014) - Human fall detection on embedded platform (Elsevier CMPB)",
  "https://doi.org/10.1016/j.cmpb.2014.09.005", "Elsevier,需付费,无免费版本"),
 ("Tran et al. (2018) - A multi-modal multi-view dataset for human fall analysis (IEEE ICPR)",
  "https://doi.org/10.1109/ICPR.2018.8546308", "IEEE Xplore,需付费,无免费版本"),
]

lines = []
lines.append("# 参考文献 PDF 清单 (Bibliographie - Detection de chutes)")
lines.append("")
lines.append("下载日期: 2026-09-28 | 文件夹: Bibliographie_PDF")
lines.append("")
lines.append("## 已下载(免费/开放获取)— 共 %d 篇" % len(OK))
lines.append("")
for f, desc, url, src in OK:
    p = os.path.join(D, f)
    mb = round(os.path.getsize(p)/1e6, 2) if os.path.exists(p) else 0
    lines.append("- `%s` (%.2f MB)" % (f, mb))
    lines.append("  - %s" % desc)
    lines.append("  - 来源: %s — %s" % (src, url))
lines.append("")
lines.append("## 未下载(付费订阅,按要求跳过)— 共 %d 篇" % len(PAYWALLED))
lines.append("")
for i, (desc, url, why) in enumerate(PAYWALLED, 1):
    lines.append("%d. %s" % (i, desc))
    lines.append("   - %s" % why)
    lines.append("   - 链接(如需自行通过学校图书馆获取): %s" % url)
lines.append("")
lines.append("## 备注")
lines.append("- 标注 \"arXiv 预印本\" 的文件是正式发表版本的作者预印本,内容基本一致,但页码/排版可能与期刊版不同。")
lines.append("- 所有文件均为免费公开来源(arXiv、MDPI、Frontiers、PeerJ、作者官方主页),未使用任何付费或非授权渠道。")
open(os.path.join(D, "LISTE_ARTICLES.md"), "w", encoding="utf-8").write("\n".join(lines))

report = [{"paper": f, "description": d, "source": s, "url": u, "status": "downloaded"}
          for f, d, u, s in OK] + \
         [{"paper": d, "source": w, "url": u, "status": "paywalled - skipped"}
          for d, u, w in PAYWALLED]
json.dump(report, open(os.path.join(D, "_download_report.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("README + report written")
print("Files now in folder:")
for n in sorted(os.listdir(D)):
    print("  ", n)
