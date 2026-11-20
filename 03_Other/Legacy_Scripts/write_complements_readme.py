# -*- coding: utf-8 -*-
import os, sys
sys.stdout.reconfigure(encoding="utf-8")
D = r"C:\Users\13968\Documents\ChatGPT\PFP _ Fall detection\Bibliographie_PDF"
SUB = os.path.join(D, "Complements")

md = []
md.append("# 补充文献(工作书目 / 评审建议新增)")
md.append("")
md.append("来源: `etat_de_lart/bibliographie.md` 及 `Revue_State_of_the_art.md` §1.6 建议补充的引用。均为免费公开版本。")
md.append("")
md.append("## 评审明确建议加入报告的 2 篇(A 类)")
md.append("- `A1_Wang_Yan_Oates_2016_..._arXiv1611.06455.pdf` — Wang, Yan & Oates (2016/2017), *Time Series Classification from Scratch with Deep Neural Networks: A Strong Baseline* (IJCNN 2017)。→ 支撑报告 §4.1 的「小 1D-CNN 基线」选择。")
md.append("- `A2_Baltrusaitis_2019_..._arXiv1705.09406.pdf` — Baltrusaitis, Ahuja & Morency (2019), *Multimodal Machine Learning: A Survey and Taxonomy* (IEEE TPAMI 41(2))。→ early / intermediate / late fusion 分类体系的标准出处,用于报告 §5。")
md.append("")
md.append("## 基础方法参考(B 类)")
md.append("- `B1_Dumoulin_Visin_2016_..._arXiv1603.07285.pdf` — 卷积算术指南(stride / padding / 输出尺寸公式)。")
md.append("- `B2_Greff_2015_..._arXiv1503.04069.pdf` — LSTM 超参数重要性排序(IEEE TNNLS 2017)。")
md.append("")
md.append("## 跌倒检测 / 数据集(C 类)")
md.append("- `C1_CasilariPerez_GarciaLagos_2020_..._Sensors.pdf` — 多数据集 CNN 评估(Sensors 20(5):1466, MDPI 开放获取)。")
md.append("- `C2_Sucerquia_2017_SisFall_Dataset_Sensors.pdf` — SisFall 数据集(Sensors 17(1):198, MDPI 开放获取)。")
md.append("")
md.append("## 付费未下载")
md.append("- Lie, Nguyen & Quek (2019), *Deep Learning for Fall Detection: 3D CNN + LSTM on Video Kinematic Data* (IEEE JBHI) — https://doi.org/10.1109/JBHI.2018.2808281 (无免费版本)")
md.append("- 在线教程类(Goodfellow 教材、CS231n、d2l.ai、Olah / Karpathy 博客)为网页形式,无需下载,链接见 `etat_de_lart/bibliographie.md`。")
md.append("")
open(os.path.join(SUB, "LISTE_COMPLEMENTS.md"), "w", encoding="utf-8").write("\n".join(md))

# append pointer section to main list
main = os.path.join(D, "LISTE_ARTICLES.md")
txt = open(main, encoding="utf-8").read()
if "Complements" not in txt:
    txt += "\n## 子文件夹\n- `Complements/` — 工作书目与评审建议补充的免费文献(6 篇)+ `LISTE_COMPLEMENTS.md`\n- `Correspondance_rapport_PDF.md` — 报告 20 条参考文献 ↔ PDF 对照表\n"
    open(main, "w", encoding="utf-8").write(txt)
print("written")
print(open(os.path.join(SUB, "LISTE_COMPLEMENTS.md"), encoding="utf-8").read())
