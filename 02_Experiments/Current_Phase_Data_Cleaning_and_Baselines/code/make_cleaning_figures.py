#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Create evidence figures for the QUIDA cleaning and smoke-test deck."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data_processed"
RESULTS = ROOT / "results"

THEME = sys.argv[sys.argv.index("--theme") + 1] if "--theme" in sys.argv else "dark"
if THEME not in {"dark", "light"}:
    raise SystemExit("--theme must be dark or light")
FIG = ROOT / "figures" / ("cleaning_light" if THEME == "light" else "cleaning")

if THEME == "light":
    NAVY = "#F7FBFF"
    PANEL = "#FFFFFF"
    CYAN = "#2563EB"
    MINT = "#0891B2"
    BLUE = "#0EA5E9"
    AMBER = "#D97706"
    ROSE = "#E11D48"
    TEXT = "#0B1F33"
    MUTED = "#60758A"
    GRID = "#D9E7F3"
    NORMAL_BAR = "#B9D5EA"
    CMAP_COLORS = ["#EFF7FF", "#A5D8F8", "#0EA5E9"]
    HEAT_STRONG_TEXT = "#FFFFFF"
else:
    NAVY = "#07121E"
    PANEL = "#0C1B2A"
    CYAN = "#38BDF8"
    MINT = "#2DD4BF"
    BLUE = "#60A5FA"
    AMBER = "#F59E0B"
    ROSE = "#FB7185"
    TEXT = "#E8F1F8"
    MUTED = "#8FA7BA"
    GRID = "#274056"
    NORMAL_BAR = "#36566E"
    CMAP_COLORS = ["#0C1B2A", "#164A63", CYAN]
    HEAT_STRONG_TEXT = NAVY


def style() -> None:
    plt.rcParams.update({
        "font.family": "Segoe UI",
        "font.size": 10,
        "text.color": TEXT,
        "axes.labelcolor": TEXT,
        "axes.edgecolor": GRID,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "axes.facecolor": PANEL,
        "figure.facecolor": NAVY,
        "savefig.facecolor": NAVY,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.alpha": 0.32,
        "grid.linewidth": 0.7,
        "axes.spines.top": False,
        "axes.spines.right": False,
    })


def save(fig, name: str) -> None:
    FIG.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIG / name, dpi=220, bbox_inches="tight", facecolor=NAVY)
    plt.close(fig)
    print("wrote", FIG / name)


def sensor_alignment() -> None:
    d = np.load(DATA / "quida_clean.npz")
    subject, event = 1, 0
    block = int(d["event_blocks"][subject - 1, event]) - 1
    center = int(d["event_offsets"][subject - 1, event])
    row = (subject - 1) * 13 + block
    start = float(d["clip_start"][row])
    target = start + float(d["acc_times"][row, center])

    fig, axes = plt.subplots(2, 2, figsize=(11.2, 5.6), sharex=True)
    fig.patch.set_facecolor(NAVY)
    for ax in axes.ravel():
        ax.set_facecolor(PANEL)
        ax.axvline(0, color=AMBER, lw=1.1, ls=(0, (3, 3)), alpha=0.9)
        ax.set_xlim(-2.2, 2.2)
        ax.tick_params(labelsize=9)

    t = start + d["acc_times"][row].astype(np.float64) - target
    mag = np.linalg.norm(d["acc"][row], axis=1)
    axes[0, 0].plot(t, mag, color=CYAN, lw=1.25)
    axes[0, 0].fill_between(t, mag, color=CYAN, alpha=0.12)
    axes[0, 0].set_title("ACCELEROMETER · 62.5 Hz", loc="left", color=CYAN, fontsize=10, fontweight="bold")
    axes[0, 0].set_ylabel("|a| (m/s²)")

    rm = d["radar_mask"][row]
    rt = start + d["radar_times"][row][rm].astype(np.float64) - target
    count = d["radar"][row][rm, 0]
    doppler = d["radar"][row][rm, 18]
    axes[0, 1].plot(rt, count, color=MINT, lw=1.6, label="points")
    axes[0, 1].plot(rt, doppler * 20, color=ROSE, lw=1.1, alpha=0.9, label="|Doppler|max × 20")
    axes[0, 1].set_title("RADAR · 8.33 Hz", loc="left", color=MINT, fontsize=10, fontweight="bold")
    axes[0, 1].set_ylabel("points / scaled m·s⁻¹")
    axes[0, 1].legend(frameon=False, fontsize=8, loc="upper left", labelcolor=TEXT)

    lm = d["lidar_mask"][row]
    lt = start + d["lidar_times"][row][lm].astype(np.float64) - target
    values = d["lidar"][row][lm]
    present = values[:, 64:128].reshape(-1, 8, 8).astype(bool)
    distance = values[:, 320:384].reshape(-1, 8, 8)
    median_distance = []
    for frame_present, frame_distance in zip(present, distance):
        valid = frame_present & (frame_distance > 0) & np.isfinite(frame_distance)
        median_distance.append(np.median(frame_distance[valid]) / 1000.0 if valid.any() else np.nan)
    axes[1, 0].plot(lt, median_distance, color=BLUE, lw=1.5, marker="o", ms=2.5)
    axes[1, 0].set_title("LiDAR · 10 Hz", loc="left", color=BLUE, fontsize=10, fontweight="bold")
    axes[1, 0].set_ylabel("median depth (m, raw/1000)")
    axes[1, 0].set_xlabel("time from annotated fall (s)")

    im = d["ir_mask"][row]
    it = start + d["ir_times"][row][im].astype(np.float64) - target
    temp = d["ir"][row][im]
    thermal_mean = temp.mean(axis=1)
    axes[1, 1].plot(it, thermal_mean, color=AMBER, lw=1.5, marker="o", ms=3)
    axes[1, 1].fill_between(it, thermal_mean, thermal_mean.min() - 0.2, color=AMBER, alpha=0.10)
    axes[1, 1].set_title("THERMAL CAMERA · 2.60 Hz", loc="left", color=AMBER, fontsize=10, fontweight="bold")
    axes[1, 1].set_ylabel("mean temperature (°C)")
    axes[1, 1].set_ylim(float(thermal_mean.min()) - 0.25, float(thermal_mean.max()) + 0.25)
    axes[1, 1].set_xlabel("time from annotated fall (s)")

    fig.suptitle("One event, four rhythms · subject 1 / fall 1", x=0.02, ha="left", fontsize=14, fontweight="bold", color=TEXT)
    fig.text(0.02, 0.925, "Fast impact spike, slower radar trajectory, sparse LiDAR and thermal frames remain aligned on one clock.",
             color=MUTED, fontsize=9)
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    save(fig, "sensor_alignment.png")


def model_metrics() -> None:
    report = json.loads((RESULTS / "preliminary_baselines.json").read_text(encoding="utf-8"))
    labels = ["F1", "Recall", "Specificity", "AUROC", "Balanced acc."]
    keys = ["f1", "recall", "specificity", "auroc", "balanced_accuracy"]
    acc = [report["models"]["acc_cnn"]["pooled"][k] for k in keys]
    radar = [report["models"]["radar_lstm"]["pooled"][k] for k in keys]
    y = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(9.4, 4.6))
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(PANEL)
    height = 0.30
    ax.barh(y - height / 2, acc, height, color=CYAN, label="ACC · 1D-CNN", alpha=0.94)
    ax.barh(y + height / 2, radar, height, color=MINT, label="RADAR · LSTM", alpha=0.94)
    for offset, values, color in ((-height / 2, acc, CYAN), (height / 2, radar, MINT)):
        for yi, value in zip(y, values):
            ax.text(value + 0.012, yi + offset, f"{value:.3f}", va="center", color=color, fontsize=9, fontweight="bold")
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlim(0, 1.14)
    ax.set_xlabel("pooled score across 396 held-out windows")
    ax.grid(axis="y", visible=False)
    ax.axvline(1.0, color=MUTED, lw=0.8, alpha=0.5)
    ax.legend(frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.18), labelcolor=TEXT)
    ax.set_title("Preliminary LOSO baseline · 10 held-out subjects", loc="left", fontsize=14, fontweight="bold", color=TEXT)
    fig.tight_layout()
    save(fig, "model_metrics.png")


def subject_f1() -> None:
    report = json.loads((RESULTS / "preliminary_baselines.json").read_text(encoding="utf-8"))
    subjects = np.arange(1, 11)
    fig, ax = plt.subplots(figsize=(9.4, 3.7))
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(PANEL)
    for name, color, label, style in (
        ("acc_cnn", CYAN, "ACC · 1D-CNN", "-"),
        ("radar_lstm", MINT, "RADAR · LSTM", "--"),
    ):
        values = [row["f1"] for row in report["models"][name]["fold_metrics"]]
        ax.plot(subjects, values, color=color, lw=2.0, linestyle=style, marker="o",
                markerfacecolor=color if name == "acc_cnn" else PANEL,
                markeredgecolor=color, markeredgewidth=1.5, ms=6, label=label, zorder=3)
        ax.fill_between(subjects, values, 0.65, color=color, alpha=0.06)
    for subject in (3, 8):
        ax.axvspan(subject - 0.38, subject + 0.38, color=ROSE, alpha=0.10, zorder=0)
    ax.set_xticks(subjects, [f"S{s}" for s in subjects])
    ax.set_ylim(0.65, 1.03)
    ax.set_ylabel("F1 on held-out subject")
    ax.set_xlabel("held-out subject")
    ax.grid(axis="x", visible=False)
    ax.legend(frameon=False, ncol=2, loc="lower left", labelcolor=TEXT)
    ax.set_title("Most folds are saturated; S3 and S8 expose the remaining false positives",
                 loc="left", fontsize=13, fontweight="bold", color=TEXT, pad=18)
    fig.tight_layout()
    save(fig, "subject_f1.png")


def confusion() -> None:
    report = json.loads((RESULTS / "preliminary_baselines.json").read_text(encoding="utf-8"))
    cmap = LinearSegmentedColormap.from_list("quida", CMAP_COLORS)
    fig, axes = plt.subplots(1, 2, figsize=(8.8, 3.8))
    fig.patch.set_facecolor(NAVY)
    for ax, name, title, color in (
        (axes[0], "acc_cnn", "ACC · 1D-CNN", CYAN),
        (axes[1], "radar_lstm", "RADAR · LSTM", MINT),
    ):
        m = report["models"][name]["pooled"]
        matrix = np.array([[m["tn"], m["fp"]], [m["fn"], m["tp"]]])
        ax.imshow(matrix, cmap=cmap, vmin=0, vmax=297)
        ax.set_facecolor(PANEL)
        ax.set_xticks([0, 1], ["no-fall", "fall"])
        ax.set_yticks([0, 1], ["no-fall", "fall"])
        ax.set_xlabel("predicted")
        ax.set_ylabel("actual")
        ax.set_title(title, loc="left", color=color, fontsize=12, fontweight="bold")
        ax.grid(False)
        for i in range(2):
            for j in range(2):
                ax.text(j, i, str(matrix[i, j]), ha="center", va="center",
                        color=HEAT_STRONG_TEXT if matrix[i, j] > 160 else TEXT,
                        fontsize=18, fontweight="bold")
    fig.tight_layout()
    save(fig, "confusion_matrices.png")


def anomaly_order() -> None:
    raw = ROOT / "data_raw"
    acc = np.loadtxt(raw / "subject_8" / "accelerometer.csv", delimiter=",", usecols=0)
    starts = np.array([acc[i * 625] for i in range(13)])
    order = np.argsort(starts) + 1
    fig, ax = plt.subplots(figsize=(9.2, 3.1))
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(PANEL)
    y = np.arange(13)
    colors = [ROSE if block in (9, 10, 11) else NORMAL_BAR for block in y + 1]
    ax.barh(y, starts - starts.min(), color=colors, height=0.65)
    for yi, block in zip(y, y + 1):
        offset = starts[yi] - starts.min()
        ax.text(offset + 1.5, yi, f"clip {block}", va="center", color=TEXT, fontsize=8)
    ax.set_yticks(y, [f"{i + 1}" for i in y])
    ax.invert_yaxis()
    ax.set_xlabel("file timestamp relative to first clip (s)")
    ax.set_ylabel("file order")
    ax.grid(axis="y", visible=False)
    ax.set_title("subject 8 · three clips sit outside chronological order", loc="left", fontsize=13, fontweight="bold", color=TEXT)
    fig.tight_layout()
    save(fig, "anomaly_order.png")


def main() -> None:
    style()
    sensor_alignment()
    model_metrics()
    subject_f1()
    confusion()
    anomaly_order()
    print("theme:", THEME)


if __name__ == "__main__":
    main()
