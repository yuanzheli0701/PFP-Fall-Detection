#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Content blocks of the CNN / LSTM summary document (English edition).

Short, plain-language notes. Block vocabulary (see build_synthese_cnn_lstm.py):
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
    "title": "CNNs and LSTMs for Fall Detection",
    "subtitle": "Summary notes for the QUIDA project",
    "module": "Module IP. 3510",
    "authors": "Written by: Clémence Vergniaud & Yuanzhe Li",
    "supervisor": "Supervised by: Wafa Njima",
    "version": "Version 1.1 (September 2026)",
}

CONTENU = [
    ("titlepage", TITLEPAGE),
    ("pagebreak", None),
    ("toc", None),

    # ------------------------------------------------------------------ 1
    ("h1", "Introduction"),
    ("p", "For the QUIDA project we need two families of networks. The accelerometer gives us short 1D signals, "
          "so we start with a convolutional neural network (CNN). The radar gives us sequences of frames, so we "
          "start with a recurrent network, more precisely an LSTM. These notes summarize how the two work, what "
          "the other common architectures do, and what we should watch out for when we train our baselines. For "
          "a full course on the subject, see Goodfellow et al. (2016)."),
    ("p", "All the numbers below use our setup: three-axis accelerometer at 62.5 Hz, windows of 625 samples "
          "(10 s), so the input tensor has shape (3, 625). The dataset contains 97 windows with a fall and 32 "
          "without, a ratio of about 3:1."),

    # ------------------------------------------------------------------ 2
    ("h1", "Convolutional neural networks"),
    ("h2", "How a convolution works"),
    ("p", "A convolutional layer slides a small filter along the signal. At each position it multiplies the "
          "filter weights by the samples below it and adds a bias:"),
    ("eq", (r"y[i] = \sum_{k=0}^{K-1} w[k]\,x[i+k] + b", "1")),
    ("p", "The filter has K weights, so one output value only looks at K input samples. The same filter is "
          "reused at every position, which keeps the number of parameters independent of the window length. It "
          "also means that a shape in the signal, for example an impact peak, is detected wherever it appears in "
          "the window. This matters here, because the impact does not happen at a fixed time."),
    ("p", "With several input channels, each output channel has one filter per input channel. A layer has "
          "K x C_in x C_out + C_out parameters, so doubling the number of channels multiplies the parameters by "
          "four."),
    ("fig", ("fig_conv1d.png", "Figure 1. A 1D convolution on one of our accelerometer windows. The filter "
                               "reacts strongly at the impact and almost not at all on the flat parts.", 5.2)),

    ("h2", "Output size and receptive field"),
    ("p", "Before stacking layers we need the output length. For an input of length L_in (Dumoulin & Visin, "
          "2016):"),
    ("eq", (r"L_{out} = \left\lfloor \frac{L_{in} + 2P - D(K-1) - 1}{S} \right\rfloor + 1", "2")),
    ("p", "The receptive field is the number of input samples behind one output value. Each layer adds (K-1)DJ "
          "samples to it, where J is the product of the strides used so far. Table 1 computes it for the baseline "
          "of Figure 2."),
    ("tbl", ("Table 1. Receptive field of the baseline, layer by layer.",
             [["Layer", "Settings", "Output length", "Receptive field"],
              ["Input", "3 x 625", "625", "1"],
              ["Conv1d", "K = 5, P = 2", "625", "5"],
              ["MaxPool", "K = 2, S = 2", "312", "6"],
              ["Conv1d", "K = 5, P = 2", "312", "14"],
              ["MaxPool", "K = 2, S = 2", "156", "16"],
              ["Conv1d", "K = 3, P = 1", "156", "24"]],
             [1.0, 1.7, 1.5, 2.1], 10)),
    ("p", "After three convolutions and two poolings the receptive field is 24 samples, about 0.38 s at "
          "62.5 Hz. That covers the impact, but not the whole 10 s window. If we want the network to see the "
          "full window, we have to add layers, use a larger stride, or use the dilated convolutions of "
          "section 4."),

    ("h2", "The baseline we will use"),
    ("fig", ("fig_cnn_arch.png", "Figure 2. The 1D-CNN baseline: three convolutions, two poolings, one global "
                                 "average pooling.", 6.2)),
    ("p", "Figure 2 shows the model we will run first. It has three Conv1d blocks, each with batch "
          "normalization, ReLU and max pooling, followed by a global average pooling head. This gives about "
          "9.3 k trainable parameters, which is small compared to the number of windows we have. We keep three "
          "layers because the dataset is small: a deeper model overfits quickly, and the receptive field is "
          "already large enough for the impact. Wang, Yan & Oates (2017) reached the same conclusion for "
          "time-series classification in general. CNNs are also a standard choice for accelerometer-based fall "
          "detection (Santos et al., 2019; Casilari-Pérez & García-Lagos, 2020)."),
    ("p", "Two limits are worth remembering. Pooling reduces the time resolution, so if we want to react "
          "quickly after the impact we should not stack too many pooling layers. And the receptive field is "
          "fixed when we design the network, so it is a choice we make, not something training can fix."),

    ("h2", "Strengths and limits"),
    ("p", "The main advantages are the small number of parameters, the fast training and the fact that the "
          "model does not care where in the window a shape appears. The main drawbacks are the limited "
          "receptive field, the loss of time resolution caused by pooling, and the fact that it models "
          "long-range dependencies between channels less well than a recurrent network."),

    # ------------------------------------------------------------------ 3
    ("h1", "Recurrent networks and LSTMs"),
    ("h2", "Recurrent networks"),
    ("p", "A recurrent network reads the sequence one step at a time and keeps a hidden state that summarizes "
          "what it has seen so far:"),
    ("eq", (r"h_t = \tanh(W_x x_t + W_h h_{t-1} + b)", "3")),
    ("p", "The weights are reused at every step, so the parameter count does not grow with the sequence length. "
          "We can take the hidden state of the last step to classify the whole window, or an output at every "
          "step if we want an online detector."),
    ("fig", ("fig_rnn_unroll.png", "Figure 3. A recurrent network unrolled in time. The same weights are used "
                                    "at every step.", 5.7)),

    ("h2", "The vanishing gradient problem"),
    ("p", "Training unrolls the whole sequence and multiplies one Jacobian per step:"),
    ("eq", (r"\frac{\partial L}{\partial h_0} = \prod_{t=1}^{T} \frac{\partial h_t}{\partial h_{t-1}}", "4")),
    ("p", "Each factor contains the derivative of tanh, which is at most 1. For a long sequence the product "
          "shrinks towards zero and the first steps receive almost no gradient. This is the vanishing gradient "
          "problem. If the weights are large the product grows instead, which is the exploding gradient "
          "problem. Clipping the gradients solves the second one. The first one is what the LSTM was designed "
          "for (Hochreiter & Schmidhuber, 1997)."),

    ("h2", "The LSTM"),
    ("p", "The LSTM adds a cell state c_t and three gates. A gate is a sigmoid layer, so its output is between "
          "0 and 1 and acts like a valve: 0 closes the flow, 1 lets everything through. The three gates are "
          "computed from the same input:"),
    ("eq", (r"\begin{bmatrix} f_t \\ i_t \\ o_t \end{bmatrix} = \sigma\!\left( W_g \begin{bmatrix} x_t \\ h_{t-1} \end{bmatrix} + b_g \right)", "5")),
    ("p", "The forget gate f_t decides how much of the old cell state we keep, the input gate i_t how much new "
          "information we write, and the output gate o_t how much of the cell state we expose as the hidden "
          "state. The new content comes from a candidate state:"),
    ("eq", (r"\tilde{c}_t = \tanh(W_c x_t + U_c h_{t-1} + b_c)", "6")),
    ("eq", (r"c_t = f_t \odot c_{t-1} + i_t \odot \tilde{c}_t", "7")),
    ("eq", (r"h_t = o_t \odot \tanh(c_t)", "8")),
    ("fig", ("fig_lstm_cell.png", "Figure 4. The LSTM cell. The three gates control what enters and leaves the "
                                   "cell state.", 5.9)),
    ("p", "The important part is the addition in the cell state. When we differentiate it, the leading term is "
          "the forget gate:"),
    ("eq", (r"\frac{\partial c_t}{\partial c_{t-1}} = f_t", "9")),
    ("p", "So the gradient that flows back along the cell state is a product of forget gates. If the network "
          "learns to keep f_t close to 1, the gradient does not shrink. This is not automatic: the network also "
          "learns to set f_t to a small value when a piece of information is no longer useful. The LSTM does "
          "not remove the vanishing gradient problem, it gives the network a path where it can avoid it. Olah "
          "(2015) has a good step-by-step walkthrough, and Greff et al. (2017) compare the many variants that "
          "have been proposed since."),

    ("h2", "GRU, and a PyTorch detail"),
    ("p", "The GRU is a simplified LSTM with two gates instead of three and about 25% fewer parameters (Cho et "
          "al., 2014). On most tasks the two give similar results, so the choice is mostly a matter of what we "
          "can tune. The fall detection papers we use mostly work with LSTMs, so we start there: Lie et al. "
          "(2019) combine a CNN with an LSTM on video data, and Musci et al. (2021) run LSTMs online on a "
          "wearable device."),
    ("p", "One detail to remember when we write the code: nn.LSTM expects (batch, seq_len, features), while "
          "nn.Conv1d expects (batch, channels, length). We have to transpose the tensor between the two. We "
          "should also clip the gradients, because an LSTM can explode as well."),

    # ------------------------------------------------------------------ 4
    ("h1", "Other architectures"),
    ("h2", "Temporal convolutional network (TCN)"),
    ("p", "A TCN is a convolutional network with two changes: the convolution is causal, so it only looks at "
          "the present and the past, and the dilation doubles at every layer (Bai et al., 2018). With K = 3 "
          "and six layers the receptive field is 127 samples, about 2 s, and the network stays parallel, unlike "
          "an RNN. The drawback is that a dilated filter leaves gaps in the signal, so very short impacts can "
          "be missed."),

    ("h2", "Transformer"),
    ("p", "Self-attention lets every position look at every other position directly, so the model can capture "
          "long-range dependencies in one step (Vaswani et al., 2017). The cost is memory and compute that grow "
          "with the square of the sequence length, and a model that has no idea of order unless we add "
          "positional encodings. Transformers also need a lot of data. With 10 subjects, training one from "
          "scratch is probably not realistic, so we keep it for later."),

    ("h2", "Autoencoder"),
    ("p", "An autoencoder compresses the input and reconstructs it. If we train it only on normal activity, a "
          "fall produces a large reconstruction error and can be flagged as an anomaly. This is useful when "
          "fall data is much rarer than normal data. The problem is that there is no clear decision boundary, "
          "so the alarm threshold is hard to choose."),

    ("h2", "Point-cloud networks"),
    ("p", "Radar and LiDAR produce a variable number of 3D points per frame. PointNet and DGCNN are designed "
          "for this kind of input, where the size changes from sample to sample (Qi et al., 2017). For a first "
          "version we can avoid this complexity by summarizing each radar frame with a few statistics before "
          "feeding it to a normal network."),

    ("h2", "Siamese networks and metric learning"),
    ("p", "This is the second route of the project, planned for weeks 3-4. Instead of training a classifier, we "
          "train two branches with shared weights to map inputs into an embedding space, using a contrastive or "
          "triplet loss so that samples of the same class end up close together and different classes far apart "
          "(Hadsell et al., 2006; Koch et al., 2015). To classify, we compare the distance to a few labeled "
          "samples or to class prototypes (Snell et al., 2017). This works with very few examples per class, "
          "which fits our fall data."),

    # ------------------------------------------------------------------ 5
    ("h1", "What we should do"),
    ("h2", "Comparison"),
    ("p", "Table 2 compares the architectures, with the parameter counts estimated for our setup."),
    ("tbl", ("Table 2. Comparison for our setup (625 samples, three axes, one sensor).",
             [["Model", "Parameters", "Training", "Data needed", "Main limitation"],
              ["1D-CNN, 3 layers", "about 9.3 k", "fast, parallel", "low", "limited receptive field"],
              ["LSTM, h = 64", "17 408", "slow, step by step", "medium", "overfits on small data"],
              ["GRU, h = 64", "13 056", "slow", "medium", "same as LSTM"],
              ["TCN, 4 layers", "about 49 k", "fast", "medium", "gaps from dilation"],
              ["Transformer, d = 64", "about 50 k", "parallel", "high", "needs much more data"],
              ["Autoencoder", "depends on the model", "fast", "low, unlabeled", "no clear threshold"]],
             [1.45, 1.25, 1.15, 1.05, 1.4], 9.5)),

    ("h2", "Recommendations for weeks 1-2"),
    ("p", "Figure 5 shows one of our fall windows. The three phases are easy to see: activity before the "
          "impact, free fall and impact, then lying still. The impact itself lasts less than a second, which is "
          "the part the receptive field has to cover."),
    ("fig", ("fig_fall_window.png", "Figure 5. A real fall window from subject_1, accelerometer at 62.5 Hz.",
             5.6)),
    ("bul", [
        "Start with the 1D-CNN of Figure 2. It trains quickly and its results are easy to interpret. Fix the "
        "data split before tuning anything else.",
        "Add a single-layer LSTM with h = 64 as a second baseline. Use exactly the same windows, the same split "
        "and the same metrics, otherwise the comparison means nothing.",
        "Use leave-one-subject-out for both models. Ten folds, then report the mean and the standard deviation, "
        "not one pooled number.",
        "Report recall and F1 first, because missing a fall is worse than a false alarm. Also give the "
        "precision, the false positive rate and the AUC; accuracy alone is misleading with a 3:1 ratio.",
        "Fit the normalization on the training folds only. Statistics computed on the whole dataset leak the "
        "test subjects into training.",
        "Fuse the two sensors late. The accelerometer runs at 62.5 Hz and the radar at 8.3 Hz, so it is much "
        "easier to extract features in each branch and concatenate them than to align the raw signals in time.",
    ]),

    ("h2", "Mistakes to avoid"),
    ("bul", [
        "Splitting windows randomly instead of by subject. Neighbouring windows look almost the same, so the "
        "score would be far too high.",
        "Looking only at accuracy. With 97 fall windows and 32 normal windows, predicting no fall everywhere "
        "already gives a high accuracy.",
        "Normalizing with statistics from the whole dataset before splitting.",
        "Using a bidirectional LSTM or whole-window features for online detection, when the future is not "
        "available at inference time.",
        "Forgetting what pooling and stride do to the receptive field, and then blaming the data when the "
        "network misses the impact.",
    ]),

    # ------------------------------------------------------------------ refs
    ("h1", "References"),
    ("refs", [
        "Bai, S., Kolter, J. Z., & Koltun, V. (2018). An empirical evaluation of generic convolutional and "
        "recurrent networks for sequence modeling. arXiv:1803.01271.",
        "Casilari-Pérez, E., & García-Lagos, F. (2020). A study on the application of convolutional neural "
        "networks to fall detection evaluated with multiple public datasets. Sensors, 20(5), 1466.",
        "Cho, K., van Merriënboer, B., Gulcehre, C., Bahdanau, D., Bougares, F., Schwenk, H., & Bengio, Y. "
        "(2014). Learning phrase representations using RNN encoder-decoder for statistical machine translation. "
        "In EMNLP (pp. 1724-1734).",
        "Dumoulin, V., & Visin, F. (2016). A guide to convolution arithmetic for deep learning. arXiv:1603.07285.",
        "Goodfellow, I., Bengio, Y., & Courville, A. (2016). Deep learning. MIT Press.",
        "Greff, K., Srivastava, R. K., Koutník, J., Steunebrink, B. R., & Schmidhuber, J. (2017). LSTM: A "
        "search space odyssey. IEEE Transactions on Neural Networks and Learning Systems, 28(10), 2222-2232.",
        "Hadsell, R., Chopra, S., & LeCun, Y. (2006). Dimensionality reduction by learning an invariant mapping. "
        "In CVPR (pp. 1735-1742).",
        "Hochreiter, S., & Schmidhuber, J. (1997). Long short-term memory. Neural Computation, 9(8), 1735-1780.",
        "Koch, G., Zemel, R., & Salakhutdinov, R. (2015). Siamese neural networks for one-shot image "
        "recognition. ICML Deep Learning Workshop.",
        "Lie, W.-N., Nguyen, D.-G., & Quek, T. Q. S. (2019). Deep learning for fall detection: 3D-CNN combined "
        "with LSTM on video kinematic data. IEEE Journal of Biomedical and Health Informatics, 23(3), 1075-1084.",
        "Musci, M., De Martini, D., Blago, N., Facchinetti, T., & Piastra, M. (2021). Online fall detection "
        "using recurrent neural networks on smart wearable devices. IEEE Transactions on Emerging Topics in "
        "Computing, 9(3), 1276-1289.",
        "Olah, C. (2015). Understanding LSTM networks. https://colah.github.io/posts/2015-08-Understanding-LSTMs/",
        "Qi, C. R., Su, H., Mo, K., & Guibas, L. J. (2017). PointNet: Deep learning on point sets for 3D "
        "classification and segmentation. In CVPR (pp. 652-660).",
        "Santos, G. L., Endo, P. T., Monteiro, K. H. C., Rocha, E. S., Silva, I., & Lynn, T. (2019). "
        "Accelerometer-based human fall detection using convolutional neural networks. Sensors, 19(7), 1644.",
        "Snell, J., Swersky, K., & Zemel, R. (2017). Prototypical networks for few-shot learning. In NeurIPS, 30.",
        "Taramasco, C., Pineiro, M., Ormeño-Arriagada, P., Robles, D., & Araya, D. (2025). Multimodal dataset "
        "for sensor fusion in fall detection. PeerJ, 13, e19004. https://doi.org/10.7717/peerj.19004",
        "Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, L., & "
        "Polosukhin, I. (2017). Attention is all you need. In NeurIPS, 30.",
        "Wang, Z., Yan, W., & Oates, T. (2017). Time series classification from scratch with deep neural "
        "networks: A strong baseline. In IJCNN (pp. 1578-1585). arXiv:1611.06455.",
    ]),
]
