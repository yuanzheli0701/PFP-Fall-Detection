#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Independent QA for data_processed/quida_clean.npz and related artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data_processed"
FAILURES = []


def check(condition: bool, message: str) -> None:
    if not condition:
        FAILURES.append(message)
    print(("PASS  " if condition else "FAIL  ") + message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    clean_path = DATA / "quida_clean.npz"
    windows_path = DATA / "quida_windows_4s.npz"
    splits_path = DATA / "splits_loso.npz"
    metadata = json.loads((DATA / "dataset_metadata.json").read_text(encoding="utf-8"))
    manifest = json.loads((DATA / "manifest.json").read_text(encoding="utf-8"))
    d = np.load(clean_path, allow_pickle=False)
    w = np.load(windows_path, allow_pickle=False)
    s = np.load(splits_path, allow_pickle=False)

    print("== Schema ==")
    check(d["acc"].shape == (130, 625, 3), "acc shape is (130, 625, 3)")
    check(d["radar"].shape == (130, 90, 22), "radar shape is (130, 90, 22)")
    check(d["lidar"].shape == (130, 105, 512), "LiDAR shape is (130, 105, 512)")
    check(d["ir"].shape == (130, 40, 768), "IR shape is (130, 40, 768)")
    check(w["acc"].shape == (396, 250, 3), "4 s window acc shape is (396, 250, 3)")
    check(w["radar"].shape == (396, 42, 22), "4 s window radar shape is (396, 42, 22)")

    print("== Labels and counts ==")
    check(len(np.unique(d["subject"])) == 10, "all 10 subjects are present")
    check(int(d["label"].sum()) == 99, "99 fall clips")
    check(int((d["label"] == 0).sum()) == 31, "31 no-fall clips")
    check(int(d["event_valid"].sum()) == 99, "99 valid fall events")
    check(not bool(d["event_valid"][2, 1]), "subject 3 / event 2 is marked invalid")
    check(bool(d["review_flag"][(3 - 1) * 13 + 7]), "subject 3 / clip 8 is review-flagged")
    check(int((d["label"] == 0).sum()) + int(d["label"].sum()) == 130, "clip labels cover all 130 rows")
    clips_per_subject = [int((d["subject"] == subject).sum()) for subject in range(1, 11)]
    check(clips_per_subject == [13] * 10, "13 fixed clips per subject")
    fall_clips = [int(d["label"][d["subject"] == subject].sum()) for subject in range(1, 11)]
    check(fall_clips == [10, 10, 9, 10, 10, 10, 10, 10, 10, 10], "per-subject fall clips match fixed-block mapping")

    print("== Values, masks, time axes ==")
    for key in ("acc", "radar", "lidar", "ir"):
        values = d[key]
        check(bool(np.isfinite(values).all()), f"{key} values are finite")
    for key in ("radar", "lidar", "ir"):
        mask = d[f"{key}_mask"]
        times = d[f"{key}_times"]
        check(int(mask.sum()) == int(np.isfinite(times).sum()), f"{key} mask and timestamp mask agree")
        bad_order = 0
        for row in range(130):
            valid_times = times[row][mask[row]]
            if valid_times.size > 1 and not bool(np.all(np.diff(valid_times) > 0)):
                bad_order += 1
        check(bad_order == 0, f"{key} timestamps increase inside every clip")
        padded_nonzero = int((~mask).sum() and np.abs(d[key][~mask]).sum())
        check(padded_nonzero == 0, f"{key} padded rows are zero")
    for key in ("radar_mask", "lidar_mask", "ir_mask"):
        check(bool(d[key].any(axis=1).all()), f"every clip has at least one {key.split('_')[0]} frame")

    print("== Radar structure ==")
    radar_frames = d["radar_mask"].sum(axis=1)
    check(int(radar_frames.min()) >= 83 and int(radar_frames.max()) <= 84, "radar clips contain 83-84 native frames")
    empty_frames = d["radar"][:, :, -1][d["radar_mask"]]
    check(int(empty_frames.sum()) > 0, "empty radar frames survive as explicit observations")
    check(int(empty_frames.sum()) < int(empty_frames.size), "radar is not entirely empty")

    print("== 4 s windows ==")
    wl = w["label"]
    check(len(wl) == 396, "396 windows")
    check(int(wl.sum()) == 99, "99 positive windows")
    check(int((wl == 0).sum()) == 297, "297 negative windows")
    check(bool(np.isfinite(w["acc"]).all()) and bool(np.isfinite(w["radar"]).all()), "window values are finite")
    window_radar_frames = w["radar_mask"].sum(axis=1)
    check(int(window_radar_frames.min()) >= 20, "every window has at least 20 radar frames (native gaps preserved)")
    per_subject_pos = [int(wl[w["subject"] == subject].sum()) for subject in range(1, 11)]
    per_subject_neg = [int((wl[w["subject"] == subject] == 0).sum()) for subject in range(1, 11)]
    check(per_subject_pos == [10, 10, 9, 10, 10, 10, 10, 10, 10, 10], "positive windows equal valid events per subject")
    check(per_subject_neg == [3 * n for n in per_subject_pos], "negative windows match 3:1 per subject")

    print("== LOSO and normalisation ==")
    check(np.array_equal(s["test_subject"], np.arange(1, 11)), "one test subject per fold")
    check(s["train_subject_matrix"].shape == (10, 9), "nine training subjects per fold")
    disjoint = all(fold + 1 not in s["train_subject_matrix"][fold] for fold in range(10))
    check(disjoint, "held-out subject never appears in its training fold")
    for fold in range(1, 11):
        check(s[f"acc_mean_{fold}"].shape == (3,), f"fold {fold}: acc mean shape")
        check(s[f"radar_mean_{fold}"].shape == (22,), f"fold {fold}: radar mean shape")
        check(s[f"lidar_mean_{fold}"].shape == (512,), f"fold {fold}: LiDAR mean shape")
        check(s[f"ir_mean_{fold}"].shape == (768,), f"fold {fold}: IR mean shape")
        check(bool(np.isfinite(s[f"acc_mean_{fold}"]).all()), f"fold {fold}: acc stats are finite")
        check(bool(np.isfinite(s[f"radar_mean_{fold}"]).all()), f"fold {fold}: radar stats are finite")

    print("== Manifest ==")
    for filename, record in manifest["files"].items():
        path = DATA / filename
        check(path.exists(), f"manifest file exists: {filename}")
        check(sha256(path) == record["sha256"], f"manifest sha256 matches: {filename}")

    qa = {
        "status": "PASS" if not FAILURES else "FAIL",
        "failures": FAILURES,
        "counts": metadata["counts"],
        "sampling_rates": metadata["sampling_rates"],
        "sync": metadata["sync"],
        "integrity": metadata["integrity"],
        "radar_frames_per_clip": {
            "min": int(radar_frames.min()),
            "median": float(np.median(radar_frames)),
            "max": int(radar_frames.max()),
        },
        "radar_frames_per_window": {
            "min": int(window_radar_frames.min()),
            "median": float(np.median(window_radar_frames)),
            "max": int(window_radar_frames.max()),
        },
        "empty_radar_frames_in_clips": int(empty_frames.sum()),
        "per_subject_fall_clips": dict(zip([f"subject_{i}" for i in range(1, 11)], fall_clips)),
        "per_subject_windows": {
            f"subject_{i}": {"fall": per_subject_pos[i - 1], "no_fall": per_subject_neg[i - 1]}
            for i in range(1, 11)
        },
    }
    (DATA / "qa_report.json").write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n{qa['status']}: {130 - len(FAILURES)} checks passed, {len(FAILURES)} failed")
    if FAILURES:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
