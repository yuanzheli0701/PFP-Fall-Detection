# Bibliographie — détection de chutes (QUIDA)
> 全部链接已核对有效（2026-09-17）。**粗体** = 优先级最高，先读这些。

## A. 基础 — CNN / 深度学习

- **Goodfellow, Bengio, Courville.** *Deep Learning.* MIT Press, 2016. 第 9 章 Convolutional Networks；第 10 章 Sequence Modeling。免费全文：https://www.deeplearningbook.org/
- **Stanford CS231n.** *Convolutional Neural Networks (notes).* https://cs231n.github.io/convolutional-networks/ —— 卷积/池化/感受野最直观的图解，**先看这个**。
- Zhang, Lipton, Li, Smola. *Dive into Deep Learning* (d2l.ai) —— 有可运行代码的教材。CNN 章：https://d2l.ai/chapter_convolutional-neural-networks/index.html
- Dumoulin, Visin. *A guide to convolution arithmetic for deep learning.* arXiv:1603.07285, 2016. https://arxiv.org/abs/1603.07285 —— **只看 stride / padding / dilation 与输出尺寸公式那张图**。
- **Wang, Yan, Oates.** *Time Series Classification from Scratch with Deep Neural Networks: A Strong Baseline.* arXiv:1611.06455, 2016 (IJCNN 2017). https://arxiv.org/abs/1611.06455 —— 三层 1D-CNN 就是强基线，正是你要做的东西。

## B. 基础 — 序列模型 / LSTM

- **Olah, C.** *Understanding LSTM Networks.* 2015. https://colah.github.io/posts/2015-08-Understanding-LSTMs/ —— LSTM 入门首选，训练必读。
- Karpathy, A. *The Unreasonable Effectiveness of Recurrent Neural Networks.* 2015. https://karpathy.github.io/2015/05/21/rnn-effectiveness/ —— 建立直觉。
- Hochreiter, Schmidhuber. *Long Short-Term Memory.* Neural Computation 9(8):1735–1780, 1997. DOI: 10.1162/neco.1997.9.8.1735 —— 原始论文，读引言 + 第 1 节即可。
- Greff et al. *LSTM: A Search Space Odyssey.* arXiv:1503.04069, 2015 (IEEE TNNLS 2017). https://arxiv.org/abs/1503.04069 —— 各超参数重要性排序，**只看结论/表格**。
- d2l.ai LSTM 章（含 PyTorch 实现）：https://d2l.ai/chapter_recurrent-modern/lstm.html

## C. 应用 — 跌倒检测

- **Musci, De Martini, Blago, Facchinetti, Piastra.** *Online Fall Detection using Recurrent Neural Networks.* arXiv:1804.04976, 2018. https://arxiv.org/abs/1804.04976 —— SisFall 上的 LSTM 在线检测；关注滑窗、延迟与精度 trade-off。
- **Casilari-Pérez, García-Lagos.** *A Study on the Application of Convolutional Neural Networks to Fall Detection Evaluated with Multiple Public Datasets.* Sensors 20(5):1466, 2020. DOI: 10.3390/s20051466 —— 多数据集 CNN 评估；关注输入表示、指标、跨数据集泛化。
- Lie, Nguyen, Quek. *Deep Learning for Fall Detection: Three-Dimensional CNN Combined With LSTM on Video Kinematic Data.* IEEE J. Biomed. Health Inform. 23(3), 2019. DOI: 10.1109/JBHI.2018.2808281 —— 「CNN 提空间特征 + LSTM 建时序」的经典范式。
- 综述型（**用 Google Scholar 按下面关键词找最新的**，避免只引老文章）：
  - `fall detection wearable sensors deep learning review`
  - `mmWave radar fall detection deep learning`
  - `LiDAR fall detection point cloud`
  - `thermal camera fall detection`

## D. 数据集

- **Sucerquia, López, Vargas-Bonilla.** *SisFall: A Fall and Movement Dataset.* Sensors 17(1):198, 2017. DOI: 10.3390/s17010198 —— 可穿戴跌倒检测最常用数据集，用来对比你的数据规模与协议。
- **QUIDA**（你的数据）：Open Science Framework (OSF)，无 RGB，4 模态同步。CrossREF 上目前检索不到正式论文，**引用格式请向老师确认**（大概率引用 OSF 项目页 + 伦理批件编号 Universidad Andrés Bello Act 032/2023）。

## E. 度量学习 / 原型分类（第 3–4 周预告，先收藏）

- Hadsell, Chopra, LeCun. *Dimensionality Reduction by Learning an Invariant Mapping.* CVPR 2006. DOI: 10.1109/CVPR.2006.100 —— **对比损失 contrastive loss 的源头**。
- Koch, Zemel, Salakhutdinov. *Siamese Neural Networks for One-shot Image Recognition.* ICML Deep Learning Workshop, 2015. —— 孪生网络经典（可按标题检索 PDF）。
- Schroff, Kalenichenko, Philbin. *FaceNet: A Unified Embedding for Face Recognition and Clustering.* arXiv:1503.03832, 2015. https://arxiv.org/abs/1503.03832 —— **三元组损失 triplet loss** 的代表作。
- Snell, Swersky, Zemel. *Prototypical Networks for Few-shot Learning.* arXiv:1703.05175, 2017. https://arxiv.org/abs/1703.05175 —— 原型分类，正好对应规划里「attribuer les classes par distances, voisins ou prototypes」。