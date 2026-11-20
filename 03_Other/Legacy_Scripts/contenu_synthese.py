#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Content blocks of the CNN / LSTM summary document.

Block vocabulary (see build_synthese_cnn_lstm.py):
    titlepage  dict       title page
    toc        None       table of contents field
    h1/h2/h3   str        headings (auto-numbered by the template styles)
    p          str        justified body paragraph with first line indent
    note       str        smaller grey paragraph for asides
    bul/num    list[str]  bullet lists
    eq         (latex, number)
    fig        (file, caption, width in inches)
    tbl        (caption, rows, widths in inches, font size)
    code       str        monospace block
    refs       list[str]
    pagebreak  None
"""

TITLEPAGE = {
    "title": "卷积与循环神经网络总结",
    "subtitle": "面向 QUIDA 跌倒检测项目的 CNN、LSTM 及相关架构",
    "module": "Module IP. 3510",
    "authors": "编写：Clémence Vergniaud & Yuanzhe Li",
    "supervisor": "指导：Wafa Njima",
    "version": "Version 1.0（2026 年 9 月）",
}

CONTENU = [
    ("titlepage", TITLEPAGE),
    ("toc", None),

    # ------------------------------------------------------------------ 1
    ("h1", "引言"),
    ("h2", "这份文档要解决什么问题"),
    ("p", "项目要在 QUIDA 数据集上比较两条技术路线：直接训练一个监督分类器，以及先学习一个度量空间、再用距离完成分类。"
          "两条路线都要用到两类基础网络：卷积神经网络（convolutional neural network, CNN）和长短期记忆网络"
          "（long short-term memory, LSTM）。本文把这两类网络以及周边常用结构整理成一份可查阅的材料，"
          "既作为第 1–2 周学习计划的配套笔记，也作为报告技术章节的底稿。"),
    ("h2", "怎么读"),
    ("p", "第 2 章回顾训练一个网络所需的最小知识；第 3 章讲 CNN，第 4 章讲循环网络与 LSTM；第 5 章简要介绍 TCN、Transformer、"
          "自编码器、点云网络和孪生网络，说明它们各自适合什么场景；第 6 章把所有结构放在一起对比，并给出在本项目上的具体建议；"
          "第 7 章是自测清单。公式按 (1)、(2) … 连续编号，符号约定见附录 A。"),
    ("note", "本文所有数值例子都用本项目的设置：加速度计 62.5 Hz，窗口 625 个采样点（10 s），输入为三轴加速度，"
             "即形状 (3, 625) 的张量。"),

    # ------------------------------------------------------------------ 2
    ("h1", "神经网络基础"),
    ("h2", "从线性模型到多层非线性"),
    ("p", "线性分类器只能画出一条直线边界。跌倒与日常动作的差别不在某个瞬时值上，而在「先失重、再冲击、然后静止」这样的局部形状"
          "与前后顺序上。多层网络通过堆叠带非线性激活的层来构造这类特征：每层把上一层的表示做一次线性组合，再经过激活函数。"
          "层数越深，能表达的局部形状越复杂。"),
    ("p", "最常用的激活函数是 ReLU 及其变体，计算便宜且不会饱和，是卷积层的默认选择："),
    ("eq", (r"a = \max(0, z)", "1")),
    ("p", "sigmoid 把输出压到 0–1，用于二分类输出层或门控信号；tanh 输出 −1–1，用于循环网络的候选状态。"
          "后两者在饱和区梯度接近 0，这是第 4 章要处理的问题。"),

    ("h2", "损失函数、梯度与反向传播"),
    ("p", "训练就是让损失函数变小。二分类最常用的是二元交叉熵，其中 N 是样本数，y 取 0 或 1，ŷ 是模型给出的概率："),
    ("eq", (r"L = -\frac{1}{N}\sum_{i=1}^{N}\left[\,y_i \log \hat{y}_i + (1-y_i)\log(1-\hat{y}_i)\,\right]", "2")),
    ("p", "反向传播用链式法则从输出层往回逐层计算损失对每个参数的偏导数，优化器再用这些梯度更新参数："),
    ("eq", (r"\theta \leftarrow \theta - \eta \,\nabla_\theta L(\theta)", "3")),
    ("p", "实践中 Adam 与 AdamW 是最常用的优化器，学习率 η 则是最值得花时间调整的单个超参数。"),

    ("h2", "划分数据与控制过拟合"),
    ("p", "在这类小数据集项目里，划分方式往往比网络结构更决定结论是否成立。下面几条是最容易出错的地方："),
    ("bul", [
        "**按受试者划分。** 同一受试者的窗口不能同时出现在训练集和测试集里，否则模型只需记住这个人的动作风格就能拿高分。"
        "本项目使用留一受试者交叉验证（leave-one-subject-out, LOSO）。",
        "**早停。** 用验证集损失决定何时停止，而不是跑满固定轮数。",
        "**权重衰减与 dropout。** 两种最常用的正则化手段，对只有几百个窗口的数据集尤其重要。",
        "**批归一化。** 把每层输入重新标准化，加快收敛，同时带来轻微的正则化效果。",
        "**类别权重。** 类别不平衡时给少数类更高的损失权重，比事后调整阈值更直接。",
    ]),

    ("h2", "全连接网络为什么不适合长序列"),
    ("p", "把 625 × 3 个采样点直接展平再接一个全连接层，第一层就有 1875 × H 个参数，序列再长一点参数就爆掉。"
          "更根本的问题是它没有利用信号本身的结构：把窗口平移一个采样点会得到完全不同的输入，而相隔 300 个点的两个采样点"
          "在模型眼里和相邻点没有区别。CNN 与循环网络各自用不同方式把「局部性」和「顺序」这两个先验放进结构里。"),

    # ------------------------------------------------------------------ 3
    ("h1", "卷积神经网络"),
    ("h2", "三个核心思想"),
    ("bul", [
        "**局部连接。** 每个输出只看输入的一小段，长度由卷积核大小 K 决定。",
        "**权值共享。** 同一个卷积核在整段信号上滑动，因此参数量与窗口长度无关。",
        "**平移等变性。** 同一个特征出现在窗口的哪个位置，都能被同一个核检测到——对跌倒检测很重要，因为冲击发生的时间点并不固定。",
    ]),

    ("h2", "一维卷积的数学"),
    ("p", "深度学习框架里的「卷积」实际是互相关：卷积核 w 长度为 K，输出第 i 个位置是窗口内 K 个输入的加权和再加偏置："),
    ("eq", (r"y[i] = \sum_{k=0}^{K-1} w[k]\,x[i+k] + b", "4")),
    ("p", "多通道输入时，每个输出通道对所有输入通道各有一个核，输出通道数就是「学多少个不同的特征检测器」："),
    ("eq", (r"y_j[i] = \sum_{c=1}^{C_{in}} \sum_{k=0}^{K-1} w_{j,c}[k]\,x_c[i+k] + b_j", "5")),
    ("p", "这一层的参数量是 K · C_in · C_out + C_out。也就是说，通道数翻倍会让参数量变成四倍，这是设计网络时最需要注意的乘法关系。"
          "图 1 给出一个直观的例子：同一个卷积核在平坦段几乎不响应，在冲击段给出很强的响应。"),
    ("fig", ("fig_conv1d.png", "图 1　一维卷积在真实加速度窗口上的作用：卷积核只在局部形状匹配时产生强响应。", 6.1)),

    ("h2", "超参数一览"),
    ("p", "表 1 汇总了一维卷积层的主要超参数，以及它们在本项目尺度下的含义。"),
    ("tbl", ("表 1　一维卷积的主要超参数。",
             [["超参数", "记号", "作用", "常见取值"],
              ["卷积核大小", "K", "每次观察的采样点数，决定单个特征的跨度", "3、5、7"],
              ["步长", "S", "卷积核移动的间隔；S > 1 同时起到降采样作用", "1（分类）、2（降采样）"],
              ["填充", "P", "在两端补零；P = (K−1)/2 时输出长度不变", "2（K = 5）、1（K = 3）"],
              ["膨胀率", "D", "卷积核元素之间的间隔，用于指数扩大感受野", "1；TCN 用 1, 2, 4, 8…"],
              ["通道数", "C_in, C_out", "学多少个不同的特征检测器", "16 / 32 / 64"],
              ["分组数", "groups", "分组卷积，减少参数与计算量", "1（默认）"]],
             [1.0, 0.85, 2.55, 1.9], 10)),

    ("h2", "输出尺寸与感受野"),
    ("p", "堆叠卷积层之前先要会算输出长度。给定输入长度 L_in，一维卷积的输出为："),
    ("eq", (r"L_{out} = \left\lfloor \frac{L_{in} + 2P - D(K-1) - 1}{S} \right\rfloor + 1", "6")),
    ("p", "感受野（receptive field）指一个输出位置在原始输入上覆盖的采样点数，它是判断网络能不能「看到」一个完整跌倒过程的关键指标。"
          "逐层递推时还要跟踪累积步长 J，即之前所有步长的乘积："),
    ("eq", (r"RF_{out} = RF_{in} + (K-1)\,D\,J, \qquad J_{out} = J \cdot S", "7")),
    ("p", "把公式用在图 2 的基线上，结果如表 2。输入 625 点，经过三层卷积和两次池化后，感受野是 24 个采样点。"),
    ("tbl", ("表 2　感受野逐层计算，输入 625 个采样点（10 s @ 62.5 Hz）。",
             [["层", "配置", "输出长度", "该层之后的感受野"],
              ["输入", "3 × 625", "625", "1"],
              ["Conv1d", "K = 5, S = 1, P = 2", "625", "5"],
              ["MaxPool", "K = 2, S = 2", "312", "6"],
              ["Conv1d", "K = 5, S = 1, P = 2", "312", "14"],
              ["MaxPool", "K = 2, S = 2", "156", "16"],
              ["Conv1d", "K = 3, S = 1, P = 1", "156", "24"]],
             [0.9, 1.9, 1.2, 1.9], 10.5)),
    ("p", "24 个采样点在 62.5 Hz 下约 0.38 s，刚好覆盖「失重—冲击」这一段；但一次跌倒的完整过程（包括冲击后的静止）接近 10 s。"
          "要一次看完整个窗口，只能加深网络、增大步长，或者使用第 5 章的膨胀卷积。"
          "顺带一提，P = (K−1)/2 的「same 卷积」保持长度不变，方便任意堆叠；不加填充时每层会缩短 K−1 个点。"),

    ("h2", "池化与全局平均池化"),
    ("p", "最大池化在局部窗口里取最大值，作用是缩短序列、扩大感受野，并对小的时间抖动更鲁棒。"
          "全局平均池化（global average pooling, GAP）把每个通道的整条特征压成一个数，输出长度与输入长度无关，"
          "从而避免了展平带来的大量参数，也让网络可以接受不同长度的窗口。"),
    ("p", "代价是池化丢弃时间分辨率。如果目标是「冲击发生后 0.5 s 内报警」的在线检测，池化层数不宜过多——"
          "每做一次步长为 2 的池化，时间分辨率就减半。"),

    ("h2", "一个可用的基线结构"),
    ("p", "图 2 是后续实验要用的基线：三层卷积 + 批归一化 + ReLU + 最大池化，最后用 GAP 收尾。"
          "可训练参数约 9.3 k，相对于几百个 10 s 窗口的数据量并不算大。"),
    ("fig", ("fig_cnn_arch.png", "图 2　1D-CNN 基线的数据流、张量形状与逐层感受野。", 6.2)),
    ("p", "为什么是三层而不是更深：数据量小，参数量一旦上千就很容易过拟合，而三层卷积的感受野已经覆盖冲击段。"
          "这也与 Wang, Yan & Oates (2016) 的结论一致——在时间序列分类上，结构简单的全卷积网络就是一个很强的基线。"),

    ("h2", "优缺点"),
    ("bul", [
        "**优点。** 参数少、训练快、容易在嵌入式设备上部署；对局部形状敏感且不要求特征出现在固定位置；"
        "感受野与参数量都能精确计算，便于按窗口长度设计。",
        "**缺点。** 感受野有限，不加深也不膨胀就看不完整段窗口；池化会丢失时间分辨率；"
        "对跨通道的、长期的依赖建模能力弱于循环网络与注意力模型。",
    ]),

    # ------------------------------------------------------------------ 4
    ("h1", "循环神经网络与 LSTM"),
    ("h2", "从 RNN 到 LSTM"),
    ("p", "循环网络把序列逐步处理，每一步用一个隐状态 h_t 概括「到目前为止看到的信息」："),
    ("eq", (r"h_t = \tanh(W_x x_t + W_h h_{t-1} + b)", "8")),
    ("p", "同一组权重在每个时刻复用，因此参数量不随序列长度增长，这是它相对全连接网络的最大优势。"
          "输出既可以取最后一个时刻的隐状态（整段做一次分类），也可以在每个时刻都输出（在线检测）。"),
    ("fig", ("fig_rnn_unroll.png", "图 3　循环网络按时间展开：隐状态把过去的信息带到下一个时刻，权重在各时刻共享。", 5.7)),
    ("p", "代价是训练时必须把整个序列展开，用时间反向传播（backpropagation through time, BPTT）计算梯度："
          "梯度是各时刻雅可比矩阵的连乘。"),
    ("eq", (r"\frac{\partial L}{\partial h_0} = \prod_{t=1}^{T} \frac{\partial h_t}{\partial h_{t-1}}", "9")),
    ("p", "每个因子都含有 W_h 与 tanh 的导数，而 tanh 的导数不超过 1。序列一长，连乘结果就指数衰减，这就是梯度消失；"
          "权重偏大时则会指数增长，即梯度爆炸。梯度爆炸可以用梯度裁剪压住，梯度消失只能靠改结构解决——这正是 LSTM 的动机。"),

    ("h2", "LSTM 的门控机制"),
    ("p", "LSTM 在循环结构之外增加了一条细胞状态 c_t 的通路和三个门。门本身是一个 sigmoid 层，输出在 0 到 1 之间，"
          "逐元素乘在信息流上：0 表示完全关闭，1 表示完全通过。四个小网络读取同样的输入 [h_{t−1}, x_t]："),
    ("eq", (r"f_t = \sigma(W_f x_t + U_f h_{t-1} + b_f)", "10")),
    ("eq", (r"i_t = \sigma(W_i x_t + U_i h_{t-1} + b_i)", "11")),
    ("eq", (r"o_t = \sigma(W_o x_t + U_o h_{t-1} + b_o)", "12")),
    ("eq", (r"\tilde{c}_t = \tanh(W_c x_t + U_c h_{t-1} + b_c)", "13")),
    ("p", "细胞状态与隐状态由门控结果组合得到："),
    ("eq", (r"c_t = f_t \odot c_{t-1} + i_t \odot \tilde{c}_t", "14")),
    ("eq", (r"h_t = o_t \odot \tanh(c_t)", "15")),
    ("fig", ("fig_lstm_cell.png", "图 4　LSTM 单元：三个门控制细胞状态与隐状态之间的信息流。", 5.9)),
    ("bul", [
        "**遗忘门 f_t** 决定旧的细胞状态保留多少。",
        "**输入门 i_t** 与候选状态 c̃_t 决定写入多少新信息。",
        "**输出门 o_t** 决定把多少细胞状态暴露给隐状态 h_t，也就是交给下一层和下一时刻的部分。",
    ]),
    ("p", "用跌倒检测的语言解释：一段日常动作过去之后，遗忘门把无关信息清掉；冲击发生时，输入门打开、写入显著的加速度模式；"
          "如果这段确实被判为跌倒，输出门就在最后几个时刻把结果放出来。门是学出来的，不需要手工设定规则。"),

    ("h2", "为什么 LSTM 能缓解梯度消失"),
    ("p", "关键在式 (14) 的加法结构。把 c_t 对 c_{t−1} 求导，主导项就是遗忘门本身："),
    ("eq", (r"\frac{\partial c_t}{\partial c_{t-1}} = f_t", "16")),
    ("note", "严格地说，f_t 本身通过 h_{t−1} 间接依赖 c_{t−1}，因此这是一条主导路径而不是恒等式。"
             "经典分析把 f_t 视为这条路径上的增益：它由网络自己学习，且可以稳定在 1 附近。"),
    ("p", "反向传播时，沿细胞状态的梯度是各时刻 f_t 的连乘。只要网络学会把 f_t 保持在接近 1，梯度就能几乎无衰减地传回去，"
          "这条路径通常被称为「常数误差传送带」。"),
    ("p", "需要说清楚的是：这不是保证，而是给网络提供了一条它自己可以选择使用的稳定通路。当数据要求遗忘时（例如跌倒已经结束、"
          "该段落不再重要），f_t 会自己变小。相对于原始 RNN，LSTM 把梯度消失从一个结构性问题变成了一个可学习的问题——"
          "这也是本项目中需要保留的一层认识，避免把它讲成「LSTM 不会梯度消失」。"),

    ("h2", "GRU 与常用变体"),
    ("p", "GRU（Cho et al., 2014）把遗忘门和输入门合并成一个更新门 z_t，并引入重置门 r_t，参数量约为 LSTM 的四分之三："),
    ("eq", (r"z_t = \sigma(\cdot), \qquad r_t = \sigma(\cdot)", "17")),
    ("eq", (r"\tilde{h}_t = \tanh\!\big(W_h\,[\,r_t \odot h_{t-1},\, x_t\,]\big)", "18")),
    ("eq", (r"h_t = (1 - z_t)\odot h_{t-1} + z_t \odot \tilde{h}_t", "19")),
    ("p", "多数任务上 GRU 与 LSTM 表现接近，选择往往取决于数据量与调参预算。其他常见变体："),
    ("bul", [
        "**双向 LSTM。** 同时从两个方向读序列，适合离线分析；在线检测不能用，因为未来数据还不存在。",
        "**堆叠多层。** 第 l 层的 h_t 作为第 l+1 层的输入，容量更大，但更容易过拟合，本项目建议先用单层。",
        "**CNN-LSTM 混合。** 先用 CNN 压缩局部形状，再把特征序列交给 LSTM 建模顺序。Lie et al. (2019) 用这个组合处理视频跌倒检测。",
    ]),

    ("h2", "PyTorch 实现要点"),
    ("p", "三个最常见的错误都跟维度有关，写代码前先确认："),
    ("bul", [
        "`nn.LSTM` 的默认输入形状是 `(batch, seq_len, features)`；要传 `(batch, features, seq_len)` 必须先转置。"
        "注意 CNN 用的是 `(batch, channels, length)`，两者正好相反。",
        "不传初始状态 `(h_0, c_0)` 时 PyTorch 自动用全零，通常没问题，但显式写出更清楚。",
        "LSTM 同样会梯度爆炸，训练循环里应加 `clip_grad_norm_`。",
    ]),
    ("p", "参数量可以手算：单层 LSTM 是 4 · h · (d_in + h + 1)，其中 4 对应三个门加候选状态，+1 是偏置项。"
          "h = 64、d_in = 3 时是 17 408 个参数，约为前面 CNN 基线的两倍。"),
    ("code", "self.lstm = nn.LSTM(in_ch, hidden, num_layers=1, batch_first=True)   # 输入 (B, L, C)\nout, (h_n, c_n) = self.lstm(x)\nlogits = self.fc(out[:, -1])                     # 取最后一个时刻\n\nnn.utils.clip_grad_norm_(model.parameters(), 1.0)   # 梯度裁剪"),

    ("h2", "优缺点"),
    ("bul", [
        "**优点。** 理论上可以保留任意长时间的信息，适合「顺序决定含义」的信号；参数量与序列长度无关；"
        "可以在每个时刻输出，天然适合在线检测，也便于显式控制检测延迟。",
        "**缺点。** 训练比 CNN 慢，因为必须逐时刻展开、无法并行；参数更多，小数据集上更容易过拟合；"
        "隐状态是定长向量，超长序列上仍会遗忘早期信息；可解释性也弱一些。",
    ]),

    # ------------------------------------------------------------------ 5
    ("h1", "其他相关结构"),
    ("h2", "时间卷积网络（TCN）"),
    ("p", "TCN 用因果卷积（只看当前和过去）加上逐层翻倍的膨胀率，在不使用循环的前提下把感受野指数扩大，同时保留卷积的并行性："),
    ("eq", (r"y_t = \sum_{k=0}^{K-1} w_k \, x_{t - d\cdot k}", "20")),
    ("p", "膨胀率按 1, 2, 4, 8 … 增长时，K = 3、L 层的感受野是 1 + 2(2^L − 1)：6 层就有 127 个采样点，约 2 s。"
          "代价是膨胀卷积在信号上引入「空洞」，对持续很短的冲击不如密集卷积敏感，而且需要额外调膨胀率与层数。"),

    ("h2", "Transformer 与自注意力"),
    ("p", "自注意力让每个位置直接与序列中的所有位置交互，一步就能建立全局依赖："),
    ("eq", (r"\mathrm{Attention}(Q,K,V) = \mathrm{softmax}\!\left(\frac{QK^{\top}}{\sqrt{d_k}}\right) V", "21")),
    ("p", "多头机制允许同时关注不同的关系。代价是计算与显存随序列长度平方增长，而且模型没有内建的顺序概念，需要位置编码；"
          "它对数据量的要求也是所有结构中最高的一类。625 个采样点的窗口在计算上完全可行，"
          "但 10 个受试者的数据量通常不足以从头训练 Transformer——这是本项目不把它作为主力的原因。"),

    ("h2", "自编码器"),
    ("p", "自编码器把输入压到低维再重建，训练目标是最小化重建误差，不需要任何标签。只用正常动作训练时，"
          "跌倒会因为重建误差大而被判为异常。它适合「只有正常数据」的场景，也可以用作无标签预训练；"
          "缺点是没有显式的类别边界，报警阈值不容易定，也不便直接报告 F1 之类的指标。"),

    ("h2", "点云网络"),
    ("p", "雷达与 LiDAR 每帧输出数量可变的三维点。PointNet（Qi et al., 2017）用共享的多层感知机逐点提特征，"
          "再用对称函数（最大池化）把点聚合成固定长度的向量，因此对点的排列顺序不变；DGCNN 进一步在特征空间建图做局部聚合。"
          "它们解决的是「输入大小不固定」的问题，是雷达与 LiDAR 分支的候选方案。"
          "本项目的第一步先把雷达帧聚合成固定长度的统计量，结构上更简单，也更容易与加速度计分支对齐。"),

    ("h2", "孪生网络与度量学习（预告）"),
    ("p", "前面所有网络最后都接一个固定的分类头。孪生网络改成两个共享权重的分支，把输入映射到嵌入空间，"
          "再用对比损失或三元组损失训练「同类靠近、异类远离」。分类时用最近邻或原型距离比较，"
          "只需少量新样本就能工作。这部分是第 3–4 周的主题，这里只说明它与本章的关系："
          "CNN 与 LSTM 是骨干网络，度量学习换掉的是训练目标与分类方式，两者可以自由组合。"),

    # ------------------------------------------------------------------ 6
    ("h1", "对比与在本项目上的选择"),
    ("h2", "结构对比"),
    ("p", "表 3 把本章涉及的结构放在一起比较，参数量的例子都用本项目的设置估算（输入 625 点、三轴、单分支）。"),
    ("tbl", ("表 3　主要网络结构对比。“参数量”一列按本项目设置估算：1D-CNN 为图 2 的三层结构，LSTM 与 GRU 取 h = 64，"
             "TCN 为 4 层 64 通道，Transformer 为 d = 64 的单层编码器。",
             [["结构", "归纳偏置", "参数量", "数据需求", "训练速度", "主要缺点"],
              ["1D-CNN", "局部性、平移等变", "≈ 9.3 k", "低", "快（可并行）", "感受野有限"],
              ["LSTM", "顺序、可变长记忆", "17.4 k", "中", "慢（逐时刻展开）", "过拟合风险，不可并行"],
              ["GRU", "同 LSTM", "13.1 k", "中", "慢", "同上，门控更简单"],
              ["TCN", "因果、膨胀卷积", "≈ 49 k", "中", "快", "空洞效应，超参数多"],
              ["Transformer", "全局注意力", "≈ 50 k", "高", "中（可并行）", "无顺序先验，最吃数据"],
              ["自编码器", "低维重构", "视结构而定", "低（无标签）", "快", "无类别边界，阈值难定"]],
             [1.15, 1.5, 0.95, 1.05, 1.15, 1.5], 9.5)),
    ("fig", ("fig_compare.png", "图 5　各结构的参数量与可覆盖的时间范围对比（循环网络没有固定的感受野上限）。", 6.2)),

    ("h2", "在 QUIDA 项目上的具体建议"),
    ("p", "数据方面：加速度计窗口为 3 × 625（三轴 × 10 s @ 62.5 Hz），标签为 0/1。"
          "图 6 是其中一次真实的跌倒：冲击前是日常动作，中间是自由下落与冲击，之后是躺卧静止。"
          "三个阶段在数值上差别很大，而冲击段的持续时间只有零点几秒——这正是感受野要覆盖的目标。"),
    ("fig", ("fig_fall_window.png", "图 6　一次真实跌倒的 10 s 窗口：冲击前、冲击、冲击后静止三个阶段。", 5.5)),
    ("p", "实测共有 97 个含跌倒的窗口和 32 个不含跌倒的窗口，比例约 3:1，与数据集说明文档里写的 1:3 并不一致，报告里应按实测描述。"
          "在此基础上，第 1–2 周的建议是："),
    ("bul", [
        "**第一基线用 1D-CNN。** 先固定划分，再调结构；参数少、训练快、结论容易解释。",
        "**第二基线用单层 LSTM（h = 64）。** 与 CNN 使用完全相同的窗口、划分与指标，这样差异才能归因到结构本身。",
        "**两者都用 LOSO。** 10 折，报告每折结果与均值 ± 标准差，而不是把所有窗口混在一起算一个总数。",
        "**主指标用召回率与 F1。** 漏报一次跌倒的代价远高于误报；同时报告精确率、假阳性率与 AUC，accuracy 只作参考。",
        "**归一化只在训练折上拟合。** 全量数据的均值方差会把测试集信息泄漏进训练；按受试者分别归一化值得作为一个对照实验。",
        "**融合放在特征层。** 加速度计 62.5 Hz、雷达 8.3 Hz，先在各自分支上提特征再做拼接（late fusion），"
        "比强行把原始信号在时间上对齐容易得多。",
    ]),

    ("h2", "常见错误"),
    ("bul", [
        "用随机窗口划分代替按受试者划分：相邻窗口高度相关，分数会明显虚高。",
        "只看 accuracy：类别不平衡时，全部预测为「非跌倒」也能得到很高的准确率。",
        "训练前对全量数据做归一化：测试集统计量泄漏进训练。",
        "用双向 LSTM 或整窗统计做在线检测：在线时未来信息并不存在。",
        "忽略池化与步长对感受野的影响：网络「看不到」完整的冲击段，却误以为是数据不够。",
    ]),

    # ------------------------------------------------------------------ 7
    ("h1", "自测清单"),
    ("p", "下面这些问题覆盖了本文的核心内容。能在不查资料的情况下答出来，说明这一轮的学习可以结束；答不上来的点标出来，下一轮补。"),
    ("tbl", ("表 4　自测清单。",
             [["#", "问题", "章节", "答题要点"],
              ["1", "为什么卷积比全连接更适合长序列？", "2.4, 3.1", "参数量与长度无关；局部连接加权值共享"],
              ["2", "输入 625 点、K = 5、S = 1、P = 2，输出多长？", "3.4", "625，same 卷积不改变长度"],
              ["3", "三层 K = 5 的卷积叠加后感受野多大？", "3.4", "13，即 1 + 3 × 4"],
              ["4", "池化对感受野和时间分辨率各有什么影响？", "3.5", "感受野按累积步长加速增长；分辨率下降"],
              ["5", "LSTM 三个门各控制什么？", "4.2", "遗忘旧状态、写入新信息、决定输出多少给 h_t"],
              ["6", "细胞状态与隐状态的区别？", "4.3", "c 是内部长记忆，h 是对外暴露并被下一层读取"],
              ["7", "为什么 LSTM 能缓解梯度消失？", "4.3", "加法路径使梯度为 f_t 的连乘，f_t ≈ 1 时不衰减"],
              ["8", "CNN 与 LSTM 的输入张量形状分别是什么？", "4.5", "(B, C, L) 与 (B, L, C)"],
              ["9", "为什么必须按受试者划分？", "2.3, 6.2", "相邻窗口相关，随机划分会泄漏信息"],
              ["10", "类别不平衡时为什么不能用 accuracy？", "6.2", "全预测为多数类即可得到高准确率"]],
             [0.35, 2.6, 0.85, 2.5], 10)),

    # ------------------------------------------------------------------ A
    ("h1", "附录 A　符号表"),
    ("tbl", ("表 5　本文常用符号。",
             [["符号", "含义", "符号", "含义"],
              ["x, x_t", "输入信号 / 第 t 个时刻的输入", "W, U, b", "权重矩阵与偏置；U 连接隐状态到门"],
              ["C_in, C_out", "输入、输出通道（特征图）数", "σ", "sigmoid 函数"],
              ["K, S, P, D", "卷积核大小、步长、填充、膨胀率", "⊙", "逐元素乘积"],
              ["L_in, L_out", "卷积前后的序列长度", "h_t, c_t", "第 t 个时刻的隐状态与细胞状态"],
              ["RF", "感受野（覆盖的原始采样点数）", "f_t, i_t, o_t", "遗忘门、输入门、输出门"],
              ["J", "累积步长，用于感受野递推", "ŷ, y", "预测概率与真实标签"],
              ["N, B, T", "样本数、批大小、序列长度", "η", "学习率"]],
             [1.05, 2.35, 1.05, 2.35], 10)),

    # ------------------------------------------------------------------ B
    ("h1", "附录 B　代码骨架"),
    ("p", "以下三段代码对应第 3、4 章的结构，可以直接放进实验脚本。注意两处张量形状的差别，以及类别权重与梯度裁剪。"),
    ("p", "CNN 基线（输入 (B, 3, 625)）："),
    ("code", "import torch\nimport torch.nn as nn\n\nclass CNN1D(nn.Module):\n    \"\"\"三层一维卷积基线，输入 (B, 3, 625)。\"\"\"\n    def __init__(self, in_ch=3, n_classes=2):\n        super().__init__()\n        self.features = nn.Sequential(\n            nn.Conv1d(in_ch, 16, 5, padding=2), nn.BatchNorm1d(16), nn.ReLU(),\n            nn.MaxPool1d(2),\n            nn.Conv1d(16, 32, 5, padding=2), nn.BatchNorm1d(32), nn.ReLU(),\n            nn.MaxPool1d(2),\n            nn.Conv1d(32, 64, 3, padding=1), nn.BatchNorm1d(64), nn.ReLU(),\n        )\n        self.head = nn.Sequential(\n            nn.AdaptiveAvgPool1d(1), nn.Flatten(), nn.Linear(64, n_classes))\n\n    def forward(self, x):            # x: (B, 3, 625)\n        return self.head(self.features(x))"),
    ("p", "LSTM 基线（输入 (B, 625, 3)，最后一个时刻输出）："),
    ("code", "class LSTMClassifier(nn.Module):\n    def __init__(self, in_ch=3, hidden=64, n_classes=2, num_layers=1):\n        super().__init__()\n        self.lstm = nn.LSTM(in_ch, hidden, num_layers=num_layers, batch_first=True)\n        self.fc = nn.Linear(hidden, n_classes)\n\n    def forward(self, x):            # x: (B, 625, 3)\n        out, (h_n, c_n) = self.lstm(x)\n        return self.fc(out[:, -1])   # 取最后一个时刻"),
    ("p", "训练循环的两个必要细节："),
    ("code", "criterion = nn.CrossEntropyLoss(weight=class_weights)   # 类别不平衡\noptimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)\n\nfor x, y in train_loader:\n    optimizer.zero_grad()\n    loss = criterion(model(x), y)\n    loss.backward()\n    nn.utils.clip_grad_norm_(model.parameters(), 1.0)     # 防止梯度爆炸\n    optimizer.step()"),

    # ------------------------------------------------------------------ refs
    ("h1", "参考文献"),
    ("refs", [
        "Bai, S., Kolter, J. Z., & Koltun, V. (2018). An empirical evaluation of generic convolutional and recurrent "
        "networks for sequence modeling. arXiv:1803.01271.",
        "Casilari-Pérez, E., & García-Lagos, F. (2020). A study on the application of convolutional neural networks to "
        "fall detection evaluated with multiple public datasets. Sensors, 20(5), 1466.",
        "Cho, K., van Merriënboer, B., Gulcehre, C., Bahdanau, D., Bougares, F., Schwenk, H., & Bengio, Y. (2014). "
        "Learning phrase representations using RNN encoder-decoder for statistical machine translation. In EMNLP (pp. 1724–1734).",
        "Dumoulin, V., & Visin, F. (2016). A guide to convolution arithmetic for deep learning. arXiv:1603.07285.",
        "Goodfellow, I., Bengio, Y., & Courville, A. (2016). Deep learning. MIT Press.",
        "Greff, K., Srivastava, R. K., Koutník, J., Steunebrink, B. R., & Schmidhuber, J. (2017). LSTM: A search space "
        "odyssey. IEEE Transactions on Neural Networks and Learning Systems, 28(10), 2222–2232.",
        "Hadsell, R., Chopra, S., & LeCun, Y. (2006). Dimensionality reduction by learning an invariant mapping. In CVPR (pp. 1735–1742).",
        "Hochreiter, S., & Schmidhuber, J. (1997). Long short-term memory. Neural Computation, 9(8), 1735–1780.",
        "Koch, G., Zemel, R., & Salakhutdinov, R. (2015). Siamese neural networks for one-shot image recognition. "
        "ICML Deep Learning Workshop.",
        "Lie, W.-N., Nguyen, D.-G., & Quek, T. Q. S. (2019). Deep learning for fall detection: 3D-CNN combined with LSTM "
        "on video kinematic data. IEEE Journal of Biomedical and Health Informatics, 23(3), 1075–1084.",
        "Musci, M., De Martini, D., Blago, N., Facchinetti, T., & Piastra, M. (2021). Online fall detection using recurrent "
        "neural networks on smart wearable devices. IEEE Transactions on Emerging Topics in Computing, 9(3), 1276–1289.",
        "Olah, C. (2015). Understanding LSTM networks. https://colah.github.io/posts/2015-08-Understanding-LSTMs/",
        "Qi, C. R., Su, H., Mo, K., & Guibas, L. J. (2017). PointNet: Deep learning on point sets for 3D classification "
        "and segmentation. In CVPR (pp. 652–660).",
        "Santos, G. L., Endo, P. T., Monteiro, K. H. C., Rocha, E. S., Silva, I., & Lynn, T. (2019). Accelerometer-based "
        "human fall detection using convolutional neural networks. Sensors, 19(7), 1644.",
        "Snell, J., Swersky, K., & Zemel, R. (2017). Prototypical networks for few-shot learning. In NeurIPS, 30.",
        "Taramasco, C., Pineiro, M., Ormeño-Arriagada, P., Robles, D., & Araya, D. (2025). Multimodal dataset for sensor "
        "fusion in fall detection. PeerJ, 13, e19004. https://doi.org/10.7717/peerj.19004",
        "Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, Ł., & Polosukhin, I. (2017). "
        "Attention is all you need. In NeurIPS, 30.",
        "Wang, Z., Yan, W., & Oates, T. (2017). Time series classification from scratch with deep neural networks: "
        "A strong baseline. In IJCNN (pp. 1578–1585). arXiv:1611.06455.",
    ]),
]
