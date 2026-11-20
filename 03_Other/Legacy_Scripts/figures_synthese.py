#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Figures for the CNN / LSTM summary documents (Chinese and English).

Generates six figures per language:
  fig_conv1d.png       1D convolution on a real accelerometer window
  fig_cnn_arch.png     1D-CNN baseline: shapes and receptive field growth
  fig_rnn_unroll.png   RNN unrolled over time
  fig_lstm_cell.png    LSTM cell: gates and cell state
  fig_compare.png      Parameter count and temporal span per architecture
  fig_fall_window.png  Real fall window from subject_1 with its three phases

Chinese figures go to figures/, English ones to figures/en/.

Usage:  python scripts/figures_synthese.py            (Chinese)
        python scripts/figures_synthese.py --lang en  (English)
"""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures"

for candidate in (r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simhei.ttf"):
    try:
        font_manager.fontManager.addfont(candidate)
    except Exception:
        pass

plt.rcParams.update(
    {
        "font.sans-serif": ["Microsoft YaHei", "Segoe UI", "SimHei", "DejaVu Sans"],
        "axes.unicode_minus": False,
        "figure.dpi": 200,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
        "axes.edgecolor": "#4a5568",
        "axes.labelcolor": "#2d3748",
        "text.color": "#2d3748",
        "xtick.color": "#4a5568",
        "ytick.color": "#4a5568",
        "axes.titlesize": 12,
        "axes.labelsize": 11,
        "font.size": 10.5,
    }
)

BLUE = "#2b6cb0"
ORANGE = "#dd6b20"
GREEN = "#2f855a"
PURPLE = "#6b46c1"
GREY = "#718096"
LIGHT = "#edf2f7"
RED = "#c53030"
WHITE_BOX = dict(boxstyle="square,pad=0.15", fc="white", ec="none")

L = {
    "zh": {
        "conv_title": "一维卷积：同一个卷积核滑过整段信号",
        "conv_input": "输入信号 $x$（加速度模长）",
        "conv_window": "窗口位置 $i$",
        "acc": "加速度 (m/s$^2$)",
        "conv_output": "输出 $y$（卷积核的响应）",
        "conv_strong": "冲击处响应最强\n（这里检测到跌倒特征）",
        "conv_flat": "平坦处响应接近 0",
        "time": "时间 (s)",
        "conv_kernel": "卷积核 $w$ = [-0.5, -1, 0, +1, +0.5]，$K$ = 5",
        "cnn_input": "输入",
        "cnn_rf": "感受野 {}",
        "cnn_title": "1D-CNN 基线：三层卷积 + 全局平均池化",
        "cnn_footer": "可训练参数约 9.3 k。最终感受野 24 个采样点，在 62.5 Hz 下约 0.38 s，"
                      "足以覆盖冲击瞬间，但覆盖不了整段 10 s 窗口。",
        "rnn_share": "同一组权重 $W_x, W_h$ 在每个时刻重复使用（参数共享）",
        "rnn_title": "循环神经网络展开：隐状态 $h_t$ 把过去的信息带到下一个时刻",
        "lstm_highway": "细胞状态：信息高速公路",
        "lstm_forget": "遗忘门\n$f_t$",
        "lstm_input": "输入门\n$i_t$",
        "lstm_candidate": "候选状态\n$\\tilde{c}_t$",
        "lstm_output": "输出门\n$o_t$",
        "lstm_inputs": "输入 $[h_{t-1}, x_t]$",
        "lstm_hint": "三个 sigmoid 门决定信息去留，一个 tanh 生成候选内容；四个小网络共用输入 $[h_{t-1}, x_t]$。",
        "lstm_title": "LSTM 单元：门控与细胞状态",
        "models": ["1D-CNN\n(3 层)", "LSTM\n(h=64)", "GRU\n(h=64)", "TCN\n(4 层, K=3)", "Transformer\n(d=64, 1 层)"],
        "cmp_y1": "可训练参数（对数刻度）",
        "cmp_t1": "参数量",
        "cmp_y2": "可覆盖的采样点数（输入窗口 = 625）",
        "cmp_t2": "时序依赖范围",
        "cmp_note": "* 循环网络没有固定的感受野上限；这里按一个窗口的长度截断，实际范围受训练数据与优化限制。",
        "fw_peak": "冲击峰值 {:.1f} m/s$^2$",
        "fw_p1": "冲击前\n日常动作",
        "fw_p2": "自由下落\n与冲击",
        "fw_p3": "冲击后\n躺卧静止",
        "fw_title": "一次真实跌倒的 10 s 窗口（subject_1，加速度计 62.5 Hz）",
        "axes3": ["x 轴", "y 轴", "z 轴"],
        "magnitude": "模长 $\\|a\\|$",
    },
    "en": {
        "conv_title": "1D convolution: one filter slides along the whole window",
        "conv_input": "Input signal $x$ (acceleration magnitude)",
        "conv_window": "window position $i$",
        "acc": "Acceleration (m/s$^2$)",
        "conv_output": "Output $y$ (filter response)",
        "conv_strong": "Strongest response at the impact\n(the fall signature shows up here)",
        "conv_flat": "Almost no response on flat sections",
        "time": "Time (s)",
        "conv_kernel": "Filter $w$ = [-0.5, -1, 0, +1, +0.5], $K$ = 5",
        "cnn_input": "Input",
        "cnn_rf": "RF {}",
        "cnn_title": "1D-CNN baseline: three convolutional layers + global average pooling",
        "cnn_footer": "About 9.3 k trainable parameters. The final receptive field is 24 samples, about 0.38 s at 62.5 Hz: "
                      "enough to cover the impact, not the whole 10 s window.",
        "rnn_share": "The same weights $W_x, W_h$ are reused at every step (weight sharing)",
        "rnn_title": "An RNN unrolled in time: the hidden state $h_t$ carries past information forward",
        "lstm_highway": "Cell state: the information highway",
        "lstm_forget": "Forget gate\n$f_t$",
        "lstm_input": "Input gate\n$i_t$",
        "lstm_candidate": "Candidate\n$\\tilde{c}_t$",
        "lstm_output": "Output gate\n$o_t$",
        "lstm_inputs": "Inputs $[h_{t-1}, x_t]$",
        "lstm_hint": "Three sigmoid gates decide what is kept or written; one tanh proposes new content. "
                     "All four small networks read the same input $[h_{t-1}, x_t]$.",
        "lstm_title": "The LSTM cell: gates and cell state",
        "models": ["1D-CNN\n(3 layers)", "LSTM\n(h=64)", "GRU\n(h=64)", "TCN\n(4 layers, K=3)", "Transformer\n(d=64, 1 layer)"],
        "cmp_y1": "Trainable parameters (log scale)",
        "cmp_t1": "Parameter count",
        "cmp_y2": "Samples covered (window = 625)",
        "cmp_t2": "Temporal span",
        "cmp_note": "* Recurrent networks have no fixed receptive-field limit; the bar is truncated at one window length. "
                    "The effective span depends on the training data and on optimisation.",
        "fw_peak": "Impact peak {:.1f} m/s$^2$",
        "fw_p1": "Pre-impact\nactivity",
        "fw_p2": "Free fall\nand impact",
        "fw_p3": "Post-impact\nlying still",
        "fw_title": "A real 10 s fall window (subject_1, accelerometer at 62.5 Hz)",
        "axes3": ["x axis", "y axis", "z axis"],
        "magnitude": "Magnitude $\\|a\\|$",
        "models_short": ["1D-CNN\n3 layers", "LSTM\nh=64", "GRU\nh=64", "TCN\n4 layers", "Transformer\nd=64"],
    },
}

LANG = "zh"


def t(key):
    return L[LANG][key]


def output_dir():
    return OUT if LANG == "zh" else OUT / "en"


def load_accelerometer(subject=1, segment=3):
    """Return time (s), the three axes and the magnitude of one 10 s window."""
    path = ROOT / "data_raw" / f"subject_{subject}" / "accelerometer.csv"
    raw = np.genfromtxt(path, delimiter=",")
    block = raw[segment * 625 : (segment + 1) * 625]
    time = block[:, 0] - block[0, 0]
    axes = block[:, 1:4]
    return time, axes, np.linalg.norm(axes, axis=1)


def rounded_box(ax, x, y, w, h, text, facecolor, edgecolor, fontsize=9.5):
    ax.add_patch(
        FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.02,rounding_size=0.06",
            linewidth=1.2, facecolor=facecolor, edgecolor=edgecolor,
        )
    )
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize, color="#1a202c")


def arrow(ax, start, end, color=GREY, lw=1.3, connectionstyle="arc3,rad=0", style="-|>"):
    ax.add_patch(
        FancyArrowPatch(
            start, end, arrowstyle=style, mutation_scale=12,
            color=color, lw=lw, connectionstyle=connectionstyle,
        )
    )


def figure_conv1d():
    """A learned filter slides along the signal and reacts to local shapes."""
    time, _, magnitude = load_accelerometer()
    kernel = np.array([-0.5, -1.0, 0.0, 1.0, 0.5])
    output = np.correlate(magnitude, kernel, mode="same")

    fig, (top, bottom) = plt.subplots(
        2, 1, figsize=(9.2, 5.0), sharex=True, gridspec_kw={"height_ratios": [1.35, 1]}
    )

    top.plot(time, magnitude, color=BLUE, lw=1.6, label=t("conv_input"))
    label_heights = (1.12, 0.90) if LANG == "en" else (1.06, 1.06)
    for (center, color), height in zip(((2.4, GREY), (3.75, ORANGE)), label_heights):
        start = np.searchsorted(time, center - 0.04)
        stop = np.searchsorted(time, center + 0.04)
        top.axvspan(time[start], time[stop], color=color, alpha=0.25, lw=0)
        top.annotate(
            t("conv_window"),
            xy=(center, magnitude[stop] + 3),
            xytext=(center, magnitude.max() * height),
            ha="center", fontsize=9.5, color=color,
            arrowprops=dict(arrowstyle="-", color=color, lw=1.0),
        )
    top.set_ylabel(t("acc"))
    top.set_ylim(0, magnitude.max() * 1.25)
    top.set_title(t("conv_title"), pad=8)
    top.legend(loc="upper right", frameon=False, fontsize=9.5)
    top.grid(alpha=0.18, lw=0.6)

    bottom.plot(time, output, color=GREEN, lw=1.6, label=t("conv_output"))
    for center, color in ((2.4, GREY), (3.75, ORANGE)):
        idx = int(np.argmin(np.abs(time - center)))
        bottom.plot(time[idx], output[idx], "o", color=color, ms=6, zorder=5)
    bottom.annotate(
        t("conv_strong"),
        xy=(3.75, output.max()),
        xytext=(5.2, output.max() * 0.78),
        fontsize=9.5, color=ORANGE,
        arrowprops=dict(arrowstyle="->", color=ORANGE, lw=1.2),
    )
    bottom.annotate(
        t("conv_flat"),
        xy=(2.4, output[int(np.argmin(np.abs(time - 2.4)))]),
        xytext=(0.4, output.max() * 0.45),
        fontsize=9.5, color=GREY,
        arrowprops=dict(arrowstyle="->", color=GREY, lw=1.2),
    )
    bottom.set_xlabel(t("time"))
    bottom.set_ylabel("$y$")
    bottom.legend(loc="upper left", frameon=False, fontsize=9.5)
    bottom.grid(alpha=0.18, lw=0.6)
    bottom.text(
        0.985, 0.9 if LANG == "zh" else 0.10, t("conv_kernel"), transform=bottom.transAxes, ha="right",
        fontsize=9, color=PURPLE,
        bbox=dict(boxstyle="round,pad=0.35", fc=LIGHT, ec=PURPLE, lw=0.8),
    )

    fig.tight_layout()
    fig.savefig(output_dir() / "fig_conv1d.png")
    plt.close(fig)


def figure_cnn_arch():
    """Baseline pipeline: tensor shapes and the growth of the receptive field."""
    fig, ax = plt.subplots(figsize=(11.6, 5.0))
    ax.set_xlim(-0.1, 17.2)
    ax.set_ylim(-0.7, 6.0)
    ax.axis("off")

    steps = [
        (t("cnn_input") + "\n3 x 625", LIGHT, GREY, ""),
        ("Conv1d\n16, K=5\nP=2", "#ebf8ff", BLUE, "5"),
        ("MaxPool\n2", "#f0fff4", GREEN, "6"),
        ("Conv1d\n32, K=5\nP=2", "#ebf8ff", BLUE, "14"),
        ("MaxPool\n2", "#f0fff4", GREEN, "16"),
        ("Conv1d\n64, K=3\nP=1", "#ebf8ff", BLUE, "24"),
        ("GAP\n\u2192 64", "#faf5ff", PURPLE, "24"),
        ("FC\n\u2192 2", "#fffaf0", ORANGE, ""),
    ]
    shapes = ["3 x 625", "16 x 625", "16 x 312", "32 x 312", "32 x 156", "64 x 156", "64 x 1", "2"]

    width, height = 1.9, 1.05
    for index, (label, face, edge, receptive) in enumerate(steps):
        row, col = divmod(index, 4)
        x = 0.35 + col * 4.15
        y = 3.75 - row * 2.8
        rounded_box(ax, x, y, width, height, label, face, edge, fontsize=9)
        ax.text(x + width / 2, y - 0.28, shapes[index], ha="center", va="center", fontsize=8.5, color=GREY)
        if receptive:
            ax.text(
                x + width / 2, y + height + 0.16, t("cnn_rf").format(receptive),
                ha="center", va="bottom", fontsize=8.5, color=RED,
                bbox=dict(boxstyle="round,pad=0.18", fc="#fff5f5", ec=RED, lw=0.7),
            )
        if index == 3:
            start = (x + width / 2, y)
            end = (0.35 + width / 2, 0.95 + height)
            route_y = 2.62
            ax.plot([start[0], start[0]], [start[1], route_y], color=GREY, lw=1.3)
            ax.plot([start[0], end[0]], [route_y, route_y], color=GREY, lw=1.3)
            arrow(ax, (end[0], route_y), end, color=GREY)
        elif index < len(steps) - 1 and divmod(index + 1, 4)[0] == row:
            next_x = 0.35 + (col + 1) * 4.15
            arrow(ax, (x + width, y + height / 2), (next_x - 0.02, y + height / 2))

    ax.text(0.35, 5.6, t("cnn_title"), fontsize=12, color="#1a202c")
    ax.text(0.35, -0.35, t("cnn_footer"), fontsize=9.5, color=GREY)
    fig.savefig(output_dir() / "fig_cnn_arch.png")
    plt.close(fig)


def figure_rnn_unroll():
    """The same cell reused at every time step, with a state carried along."""
    fig, ax = plt.subplots(figsize=(9.4, 4.3))
    ax.set_xlim(-0.4, 10.6)
    ax.set_ylim(-0.5, 4.6)
    ax.axis("off")

    xs = [1.1, 3.5, 5.9, 8.3]
    for index, x in enumerate(xs):
        rounded_box(ax, x - 0.5, 1.75, 1.0, 0.95, f"$h_{index}$", "#ebf8ff", BLUE, fontsize=12)
        ax.text(x, 0.75, f"$x_{index}$", ha="center", va="center", fontsize=12, color=GREEN)
        arrow(ax, (x, 1.05), (x, 1.72), color=GREEN)
        arrow(ax, (x, 2.72), (x, 3.28), color=PURPLE)
        ax.text(x, 3.5, f"$\\hat{{y}}_{index}$", ha="center", va="center", fontsize=11, color=PURPLE)
        if index < len(xs) - 1:
            arrow(ax, (x + 0.52, 2.22), (xs[index + 1] - 0.52, 2.22), color=ORANGE, lw=1.6)

    ax.add_patch(
        FancyBboxPatch(
            (0.35, 1.5), 8.6, 1.45,
            boxstyle="round,pad=0.02,rounding_size=0.06",
            fc="none", ec=ORANGE, lw=1.4, ls=(0, (5, 3)),
        )
    )
    if LANG == "en":
        ax.text(10.55, 0.22, t("rnn_share"), ha="right", va="center", fontsize=9.5, color=ORANGE)
    else:
        ax.text(4.65, 1.24, t("rnn_share"), ha="center", va="top", fontsize=9.5, color=ORANGE)
    ax.text(0.35, 4.35, t("rnn_title"), fontsize=11.5, color="#1a202c")
    ax.text(
        -0.3, 0.15, "$h_t = \\tanh(W_x x_t + W_h h_{t-1} + b)$", fontsize=11, color="#1a202c",
        bbox=dict(boxstyle="round,pad=0.35", fc=LIGHT, ec=GREY, lw=0.8),
    )
    fig.savefig(output_dir() / "fig_rnn_unroll.png")
    plt.close(fig)


def figure_lstm_cell():
    """Gates and the cell-state highway."""
    fig, ax = plt.subplots(figsize=(10.6, 5.6))
    ax.set_xlim(0, 13.0)
    ax.set_ylim(0, 7.0)
    ax.axis("off")

    y_cell = 5.15
    y_gate_bottom, y_gate_top = 3.05, 3.9
    y_bus = 1.5

    arrow(ax, (0.7, y_cell), (12.55, y_cell), color=BLUE, lw=2.4)
    ax.text(0.7, y_cell + 0.28, "$c_{t-1}$", fontsize=12, color=BLUE)
    ax.text(12.35, y_cell + 0.28, "$c_t$", fontsize=12, color=BLUE, ha="center")
    ax.text(4.0, y_cell + 0.34, t("lstm_highway"), fontsize=9.5, color=BLUE, ha="center")

    gate_x = {"forget": 2.6, "input": 4.95, "candidate": 7.45, "output": 10.35}
    gates = [
        ("forget", r"$\sigma$", t("lstm_forget"), "#fff5f5", RED),
        ("input", r"$\sigma$", t("lstm_input"), "#f0fff4", GREEN),
        ("candidate", "tanh", t("lstm_candidate"), "#faf5ff", PURPLE),
        ("output", r"$\sigma$", t("lstm_output"), "#fffaf0", ORANGE),
    ]
    for key, symbol, label, face, edge in gates:
        x = gate_x[key]
        rounded_box(ax, x - 0.68, y_gate_bottom, 1.36, y_gate_top - y_gate_bottom, symbol, face, edge, fontsize=12)
        ax.text(x, y_gate_bottom - 0.12, label, ha="center", va="top", fontsize=9.5, color=edge, bbox=WHITE_BOX)
        arrow(ax, (x, y_bus), (x, y_gate_bottom - 0.02), color=edge, lw=1.0, style="-")

    arrow(ax, (0.7, y_bus), (12.55, y_bus), color=GREY, lw=1.6)
    ax.text(0.7, y_bus + 0.22, t("lstm_inputs"), fontsize=10.5, color=GREY)

    arrow(ax, (gate_x["forget"], y_gate_top), (gate_x["forget"], y_cell - 0.24), color=RED, lw=1.3)
    ax.add_patch(Circle((gate_x["forget"], y_cell), 0.24, fc="white", ec=RED, lw=1.5, zorder=5))
    ax.text(gate_x["forget"], y_cell, r"$\odot$", ha="center", va="center", fontsize=13, color=RED, zorder=6)

    branch_y = 4.5
    ax.plot([gate_x["input"], gate_x["input"]], [y_gate_top, branch_y], color=GREEN, lw=1.3)
    ax.plot([gate_x["input"], 6.2], [branch_y, branch_y], color=GREEN, lw=1.3)
    arrow(ax, (6.2, branch_y), (6.2, y_cell - 0.24), color=GREEN, lw=1.3)
    ax.plot([gate_x["candidate"], gate_x["candidate"]], [y_gate_top, branch_y], color=PURPLE, lw=1.3)
    ax.plot([gate_x["candidate"], 6.2], [branch_y, branch_y], color=PURPLE, lw=1.3)
    ax.add_patch(Circle((6.2, y_cell), 0.24, fc="white", ec=PURPLE, lw=1.5, zorder=5))
    ax.text(6.2, y_cell, "$+$", ha="center", va="center", fontsize=13, color=PURPLE, zorder=6)

    out_x = 11.35
    ax.plot([out_x, out_x], [y_cell, y_cell - 0.32], color=BLUE, lw=1.3)
    ax.add_patch(Circle((out_x, y_cell - 0.55), 0.23, fc="white", ec=BLUE, lw=1.2, zorder=5))
    ax.text(out_x, y_cell - 0.55, "tanh", ha="center", va="center", fontsize=7.5, color=BLUE, zorder=6)
    arrow(ax, (out_x, y_cell - 0.78), (out_x, y_cell - 1.22), color=BLUE, lw=1.3)
    ax.plot([gate_x["output"], gate_x["output"]], [y_gate_top, y_cell - 1.0], color=ORANGE, lw=1.3)
    ax.plot([gate_x["output"], out_x], [y_cell - 1.0, y_cell - 1.0], color=ORANGE, lw=1.3)
    ax.add_patch(Circle((out_x, y_cell - 1.0), 0.24, fc="white", ec=ORANGE, lw=1.5, zorder=5))
    ax.text(out_x, y_cell - 1.0, r"$\odot$", ha="center", va="center", fontsize=13, color=ORANGE, zorder=6)
    ax.text(out_x + 0.36, y_cell - 1.42, "$h_t$", fontsize=12, color=BLUE, va="center")

    ax.text(
        6.5, 0.72,
        "$c_t = f_t \\odot c_{t-1} + i_t \\odot \\tilde{c}_t$        $h_t = o_t \\odot \\tanh(c_t)$",
        fontsize=11.5, color="#1a202c", ha="center",
    )
    ax.text(6.5, 0.2, t("lstm_hint"), fontsize=9.5, color=GREY, ha="center")
    ax.text(0.2, 6.62, t("lstm_title"), fontsize=12, color="#1a202c")
    fig.savefig(output_dir() / "fig_lstm_cell.png")
    plt.close(fig)


def figure_compare():
    """What each family costs and how far it can look back."""
    models = t("models_short") if LANG == "en" else t("models")
    params = [9_300, 17_408, 13_056, 49_408, 49_664]
    span = [24, 625, 625, 127, 625]
    colors = [BLUE, ORANGE, GREEN, PURPLE, "#b7791f"]

    fig, (left, right) = plt.subplots(1, 2, figsize=((12.4, 4.5) if LANG == "en" else (11.2, 4.2)))

    bars = left.bar(models, params, color=colors, width=0.6)
    left.set_yscale("log")
    left.set_ylim(5_000, 130_000)
    left.set_ylabel(t("cmp_y1"))
    left.set_title(t("cmp_t1"), pad=10)
    left.grid(axis="y", alpha=0.18, lw=0.6)
    left.set_axisbelow(True)
    for bar, value in zip(bars, params):
        left.text(
            bar.get_x() + bar.get_width() / 2, value * 1.12, f"{value/1000:.1f} k",
            ha="center", va="bottom", fontsize=9, color="#2d3748",
        )
    left.tick_params(axis="x", labelsize=8.5)

    bars = right.bar(models, span, color=colors, width=0.6)
    right.set_ylim(0, 860)
    right.set_ylabel(t("cmp_y2"))
    right.set_title(t("cmp_t2"), pad=10)
    right.grid(axis="y", alpha=0.18, lw=0.6)
    right.set_axisbelow(True)
    right.tick_params(axis="x", labelsize=8.5)
    labels = ["24", "625 *", "625 *", "127", "625"]
    for index, (bar, label) in enumerate(zip(bars, labels)):
        if index in (1, 2):
            bar.set_hatch("//")
            bar.set_alpha(0.6)
        right.text(
            bar.get_x() + bar.get_width() / 2, span[index] + 18, label,
            ha="center", va="bottom", fontsize=9, color="#2d3748",
        )
    right.text(0.5, -0.26, t("cmp_note"), transform=right.transAxes, ha="center", fontsize=8.5, color=GREY)

    fig.tight_layout(w_pad=3.0 if LANG == "en" else 1.08)
    fig.savefig(output_dir() / "fig_compare.png")
    plt.close(fig)


def figure_fall_window():
    """A real fall window: pre-impact, impact, then lying still."""
    time, axes, magnitude = load_accelerometer()
    impact = float(time[np.argmax(magnitude)])

    fig, ax = plt.subplots(figsize=(10.0, 4.4))
    bottom, top = -60.0, 78.0
    ax.set_ylim(bottom, top)
    for values, label, color in zip(axes.T, t("axes3"), (BLUE, ORANGE, GREEN)):
        ax.plot(time, values, lw=1.4, color=color, label=label)
    ax.plot(time, magnitude, lw=1.8, color="#1a202c", ls="--", label=t("magnitude"))
    ax.axvline(impact, color=RED, lw=1.3, ls=":")

    phases = [(0.4, 2.7, t("fw_p1")), (3.2, 4.35, t("fw_p2")), (4.9, 9.8, t("fw_p3"))]
    for start, stop, text in phases:
        ax.axvspan(start, stop, color=LIGHT, alpha=0.6, lw=0)
        ax.text((start + stop) / 2, bottom + 4, text, ha="center", va="bottom", fontsize=9, color=GREY)

    if LANG == "en":
        ax.text(impact - 0.15, top - 6, t("fw_peak").format(magnitude.max()), color=RED, fontsize=9.5, va="top", ha="right")
    else:
        ax.text(impact + 0.15, top - 6, t("fw_peak").format(magnitude.max()), color=RED, fontsize=9.5, va="top")

    ax.set_xlabel(t("time"))
    ax.set_ylabel(t("acc"))
    ax.set_title(t("fw_title"), pad=8)
    ax.grid(alpha=0.18, lw=0.6)
    ax.legend(loc="upper right", ncol=4, frameon=False, fontsize=9)
    fig.tight_layout()
    fig.savefig(output_dir() / "fig_fall_window.png")
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", choices=["zh", "en"], default="zh")
    arguments = parser.parse_args()
    LANG = arguments.lang
    output_dir().mkdir(parents=True, exist_ok=True)
    figure_conv1d()
    figure_cnn_arch()
    figure_rnn_unroll()
    figure_lstm_cell()
    figure_compare()
    figure_fall_window()
    print("Figures written to", output_dir())
