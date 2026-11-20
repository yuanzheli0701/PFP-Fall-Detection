#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Smoke-test 1D-CNN (accelerometer) and LSTM (radar) on the cleaned 4 s windows.

This is a pipeline validation baseline, not the final supervised comparison.
Every fold holds out one complete subject, and all normalisation statistics come
from the training subjects only.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import confusion_matrix, roc_auc_score


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data_processed"
RESULTS = ROOT / "results"


class CNN1D(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv1d(3, 16, 5, padding=2), nn.BatchNorm1d(16), nn.ReLU(), nn.MaxPool1d(2),
            nn.Conv1d(16, 32, 5, padding=2), nn.BatchNorm1d(32), nn.ReLU(), nn.MaxPool1d(2),
            nn.Conv1d(32, 64, 3, padding=1), nn.BatchNorm1d(64), nn.ReLU(),
            nn.AdaptiveAvgPool1d(1),
        )
        self.head = nn.Sequential(nn.Dropout(0.30), nn.Linear(64, 2))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.head(self.features(x.transpose(1, 2)).squeeze(-1))


class RadarLSTM(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.lstm = nn.LSTM(input_size=22, hidden_size=32, batch_first=True)
        self.head = nn.Sequential(nn.Dropout(0.30), nn.Linear(32, 2))

    def forward(self, x: torch.Tensor, lengths: torch.Tensor) -> torch.Tensor:
        packed = nn.utils.rnn.pack_padded_sequence(
            x, lengths.cpu(), batch_first=True, enforce_sorted=False
        )
        _, (hidden, _) = self.lstm(packed)
        return self.head(hidden[-1])


def set_seed(seed: int) -> None:
    np.random.seed(seed)
    torch.manual_seed(seed)


def metrics(y_true: np.ndarray, y_pred: np.ndarray, probability: np.ndarray) -> dict:
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    specificity = tn / max(tn + fp, 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-12)
    return {
        "n": int(len(y_true)),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
        "accuracy": float((tp + tn) / len(y_true)),
        "precision": float(precision),
        "recall": float(recall),
        "specificity": float(specificity),
        "f1": float(f1),
        "balanced_accuracy": float((recall + specificity) / 2.0),
        "auroc": float(roc_auc_score(y_true, probability)),
    }


def train_epochs(model, optimizer, loss_fn, x, y, lengths, epochs, batch_size, seed):
    generator = torch.Generator().manual_seed(seed)
    for _ in range(epochs):
        model.train()
        order = torch.randperm(len(y), generator=generator)
        for start in range(0, len(y), batch_size):
            batch = order[start:start + batch_size]
            optimizer.zero_grad()
            output = model(x[batch], lengths[batch]) if lengths is not None else model(x[batch])
            loss = loss_fn(output, y[batch])
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            optimizer.step()


def predict(model, x, lengths, batch_size=64):
    model.eval()
    probabilities = []
    with torch.no_grad():
        for start in range(0, len(x), batch_size):
            xb = x[start:start + batch_size]
            if lengths is None:
                logits = model(xb)
            else:
                logits = model(xb, lengths[start:start + batch_size])
            probabilities.append(torch.softmax(logits, dim=1)[:, 1].numpy())
    probability = np.concatenate(probabilities)
    return probability, (probability >= 0.5).astype(np.int64)


def run_fold(fold, train_idx, test_idx, windows, epochs, seed):
    labels = windows["label"].astype(np.int64)
    train_y = torch.tensor(labels[train_idx], dtype=torch.long)
    test_y = labels[test_idx]
    class_count = np.bincount(labels[train_idx], minlength=2)
    weights = len(train_idx) / (2.0 * np.maximum(class_count, 1))
    loss_fn = nn.CrossEntropyLoss(weight=torch.tensor(weights, dtype=torch.float32))

    train_acc = windows["acc"][train_idx]
    test_acc = windows["acc"][test_idx]
    acc_mean = train_acc.reshape(-1, 3).mean(axis=0)
    acc_std = train_acc.reshape(-1, 3).std(axis=0)
    acc_std = np.where(acc_std < 1e-7, 1.0, acc_std)
    x_train_acc = torch.tensor((train_acc - acc_mean) / acc_std, dtype=torch.float32)
    x_test_acc = torch.tensor((test_acc - acc_mean) / acc_std, dtype=torch.float32)

    train_radar = windows["radar"][train_idx]
    test_radar = windows["radar"][test_idx]
    train_mask = windows["radar_mask"][train_idx]
    test_mask = windows["radar_mask"][test_idx]
    real_values = train_radar[train_mask]
    radar_mean = real_values.mean(axis=0)
    radar_std = real_values.std(axis=0)
    radar_std = np.where(radar_std < 1e-7, 1.0, radar_std)
    x_train_radar = torch.tensor((train_radar - radar_mean) / radar_std, dtype=torch.float32)
    x_test_radar = torch.tensor((test_radar - radar_mean) / radar_std, dtype=torch.float32)
    x_train_radar[~torch.tensor(train_mask)] = 0.0
    x_test_radar[~torch.tensor(test_mask)] = 0.0
    lengths_train = torch.tensor(train_mask.sum(axis=1), dtype=torch.long)
    lengths_test = torch.tensor(test_mask.sum(axis=1), dtype=torch.long)

    fold_results = {}
    for name, model, xtr, xte, ltr, lte in (
        ("acc_cnn", CNN1D(), x_train_acc, x_test_acc, None, None),
        ("radar_lstm", RadarLSTM(), x_train_radar, x_test_radar, lengths_train, lengths_test),
    ):
        set_seed(seed + fold * 17 + (0 if name == "acc_cnn" else 101))
        optimizer = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)
        start = time.perf_counter()
        train_epochs(model, optimizer, loss_fn, xtr, train_y, ltr, epochs, 32, seed + fold)
        probability, prediction = predict(model, xte, lte)
        elapsed = time.perf_counter() - start
        fold_results[name] = {
            "fold": fold,
            "test_subject": fold,
            "train_windows": int(len(train_idx)),
            "test_windows": int(len(test_idx)),
            "train_seconds": float(elapsed),
            "probability": probability,
            "prediction": prediction,
            "metrics": metrics(test_y, prediction, probability),
        }
    return fold_results, test_y


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=45)
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()
    torch.set_num_threads(max(1, min(8, torch.get_num_threads())))
    RESULTS.mkdir(parents=True, exist_ok=True)
    windows = np.load(DATA / "quida_windows_4s.npz", allow_pickle=False)
    subjects = windows["subject"]
    all_results = {"acc_cnn": [], "radar_lstm": []}
    truth, indices = [], []

    for fold in range(1, 11):
        train_idx = np.flatnonzero(subjects != fold)
        test_idx = np.flatnonzero(subjects == fold)
        fold_results, test_y = run_fold(fold, train_idx, test_idx, windows, args.epochs, args.seed)
        truth.append(test_y)
        indices.append(test_idx)
        for name, result in fold_results.items():
            all_results[name].append(result)
            m = result["metrics"]
            print(
                f"{name:10s} fold {fold:2d}: F1={m['f1']:.3f} recall={m['recall']:.3f} "
                f"specificity={m['specificity']:.3f} AUROC={m['auroc']:.3f} "
                f"({result['train_seconds']:.2f}s)",
                flush=True,
            )

    y_true = np.concatenate(truth)
    summary = {"epochs": args.epochs, "seed": args.seed, "protocol": "leave-one-subject-out", "models": {}}
    predictions_rows = []
    for name, results in all_results.items():
        probability = np.concatenate([r["probability"] for r in results])
        prediction = np.concatenate([r["prediction"] for r in results])
        fold_metrics = [r["metrics"] for r in results]
        macro = {}
        for key in ("accuracy", "precision", "recall", "specificity", "f1", "balanced_accuracy", "auroc"):
            values = np.asarray([m[key] for m in fold_metrics])
            macro[key] = {"mean": float(values.mean()), "std": float(values.std())}
        summary["models"][name] = {
            "pooled": metrics(y_true, prediction, probability),
            "per_subject_macro": macro,
            "mean_train_seconds": float(np.mean([r["train_seconds"] for r in results])),
            "fold_metrics": [
                {"fold": r["fold"], "test_subject": r["test_subject"], **r["metrics"]}
                for r in results
            ],
        }
        for row_index, probability_i, prediction_i in zip(np.concatenate(indices), probability, prediction):
            predictions_rows.append({
                "model": name,
                "row": int(row_index),
                "subject": int(windows["subject"][row_index]),
                "clip": int(windows["clip"][row_index]),
                "event": int(windows["event"][row_index]),
                "y_true": int(windows["label"][row_index]),
                "y_pred": int(prediction_i),
                "probability": float(probability_i),
            })

    (RESULTS / "preliminary_baselines.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    with (RESULTS / "preliminary_baseline_predictions.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(predictions_rows[0]))
        writer.writeheader()
        writer.writerows(predictions_rows)

    print("\nPOOLED TEST RESULTS")
    for name in ("acc_cnn", "radar_lstm"):
        m = summary["models"][name]["pooled"]
        print(
            f"{name:10s}: F1={m['f1']:.3f} recall={m['recall']:.3f} "
            f"specificity={m['specificity']:.3f} AUROC={m['auroc']:.3f}"
        )


if __name__ == "__main__":
    main()
