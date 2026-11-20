#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Build model-ready QUIDA arrays without modifying data_raw/.

Outputs (data_processed/):
  quida_clean.npz       130 fixed 10 s clips, four modalities, labels and masks
  quida_windows_4s.npz  4 s windows for the preliminary CNN/LSTM baselines
  splits_loso.npz       leave-one-subject-out folds and training-only statistics
  dataset_metadata.json schema, QA measurements and anomaly log
  data_card.md          short usage guide
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data_raw"
OUT_DEFAULT = ROOT / "data_processed"
SUBJECTS = tuple(range(1, 11))
MODALITIES = ("accelerometer", "radar", "LIDAR", "ir_camera")
CLIP_SAMPLES = 625
CLIPS_PER_SUBJECT = 13
WINDOW_SAMPLES = 250
GUARD_S = 2.0
N_RADAR_FEATURES = 22
RADAR_CLIP_MAX = 90
RADAR_WINDOW_MAX = 42
LIDAR_CLIP_MAX = 105
IR_CLIP_MAX = 40

RADAR_FEATURES = [
    "target_count", "centroid_x", "centroid_y", "centroid_z",
    "std_x", "std_y", "std_z", "z_min", "z_max", "z_range",
    "range_mean", "range_min", "range_max", "doppler_mean",
    "doppler_abs_mean", "doppler_min", "doppler_max", "doppler_std",
    "doppler_abs_max", "snr_mean", "snr_std", "empty_frame",
]
LIDAR_BLOCKS = {
    "ambient_kcps": (0, 64), "target_present": (64, 128),
    "active_spads": (128, 192), "photon_count_kcps": (192, 256),
    "distance_std_m": (256, 320), "distance_m": (320, 384),
    "status": (384, 448), "reflectance_pct": (448, 512),
}


def read_matrix(path: Path) -> np.ndarray:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = [[float(v) for v in row if v.strip()] for row in csv.reader(handle) if row]
    return np.asarray(rows, dtype=np.float64)


def read_ts(path: Path) -> np.ndarray:
    return np.loadtxt(path, delimiter=",", usecols=0, ndmin=1).astype(np.float64)


def read_radar(path: Path):
    timestamps, points = [], []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            values = np.fromstring(line.strip(), sep=",")
            payload = values[1:]
            if payload.size % 7:
                raise ValueError(f"{path}:{line_number}: expected 1+7n columns")
            timestamps.append(values[0])
            points.append(payload.reshape(-1, 7).astype(np.float32))
    return np.asarray(timestamps, dtype=np.float64), points


def radar_frame_features(points: np.ndarray) -> np.ndarray:
    out = np.zeros(N_RADAR_FEATURES, dtype=np.float32)
    if points.size == 0:
        out[-1] = 1.0
        return out
    xyz = points[:, :3].astype(np.float64)
    doppler = points[:, 3].astype(np.float64)
    snr = points[:, 4].astype(np.float64)
    distance = np.linalg.norm(xyz, axis=1)
    z = xyz[:, 2]
    out[0] = len(points)
    out[1:4] = xyz.mean(axis=0)
    out[4:7] = xyz.std(axis=0)
    out[7], out[8], out[9] = z.min(), z.max(), z.max() - z.min()
    out[10], out[11], out[12] = distance.mean(), distance.min(), distance.max()
    out[13], out[14] = doppler.mean(), np.abs(doppler).mean()
    out[15], out[16], out[17], out[18] = doppler.min(), doppler.max(), doppler.std(), np.abs(doppler).max()
    out[19], out[20] = snr.mean(), snr.std()
    return out


def select_rows(timestamps: np.ndarray, start: float, end: float) -> np.ndarray:
    return np.flatnonzero((timestamps >= start - 1e-6) & (timestamps <= end + 1e-6))


def safe_std(values: np.ndarray) -> np.ndarray:
    std = values.std(axis=0)
    return np.where(std < 1e-7, 1.0, std).astype(np.float32)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def json_safe(value):
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if isinstance(value, np.ndarray):
        return json_safe(value.tolist())
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, Path):
        return str(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=OUT_DEFAULT)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    clean_path = out / "quida_clean.npz"
    windows_path = out / "quida_windows_4s.npz"
    splits_path = out / "splits_loso.npz"
    if not args.overwrite and any(p.exists() for p in (clean_path, windows_path, splits_path)):
        raise SystemExit("Processed files exist; pass --overwrite to regenerate.")

    falls = read_matrix(RAW / "falls.csv")
    indices = {m: read_matrix(RAW / f"{m}.csv") for m in MODALITIES}
    acc_index = indices["accelerometer"].astype(int)
    n_clips = len(SUBJECTS) * CLIPS_PER_SUBJECT
    acc = np.zeros((n_clips, CLIP_SAMPLES, 3), dtype=np.float32)
    acc_times = np.zeros((n_clips, CLIP_SAMPLES), dtype=np.float32)
    radar = np.zeros((n_clips, RADAR_CLIP_MAX, N_RADAR_FEATURES), dtype=np.float32)
    radar_mask = np.zeros((n_clips, RADAR_CLIP_MAX), dtype=bool)
    radar_times = np.full((n_clips, RADAR_CLIP_MAX), np.nan, dtype=np.float32)
    lidar = np.zeros((n_clips, LIDAR_CLIP_MAX, 512), dtype=np.float32)
    lidar_mask = np.zeros((n_clips, LIDAR_CLIP_MAX), dtype=bool)
    lidar_times = np.full((n_clips, LIDAR_CLIP_MAX), np.nan, dtype=np.float32)
    ir = np.zeros((n_clips, IR_CLIP_MAX, 768), dtype=np.float32)
    ir_mask = np.zeros((n_clips, IR_CLIP_MAX), dtype=bool)
    ir_times = np.full((n_clips, IR_CLIP_MAX), np.nan, dtype=np.float32)
    labels = np.zeros(n_clips, dtype=np.int8)
    subjects = np.zeros(n_clips, dtype=np.int16)
    clips = np.zeros(n_clips, dtype=np.int16)
    clip_start = np.zeros(n_clips, dtype=np.float64)
    clip_end = np.zeros(n_clips, dtype=np.float64)
    fall_event_ids = np.zeros((n_clips, 10), dtype=bool)
    review_flag = np.zeros(n_clips, dtype=bool)
    sync_offsets = np.full((10, 10, len(MODALITIES)), np.nan)
    event_valid = np.zeros((10, 10), dtype=bool)
    event_blocks = np.zeros((10, 10), dtype=np.int16)
    event_offsets = np.zeros((10, 10), dtype=np.int16)
    per_subject = {}
    radar_raw_frames = radar_raw_empty = radar_raw_max_targets = 0
    nonfinite = {m: 0 for m in MODALITIES}

    for subject in SUBJECTS:
        sdir = RAW / f"subject_{subject}"
        acc_matrix = np.loadtxt(sdir / "accelerometer.csv", delimiter=",", dtype=np.float64)
        if acc_matrix.shape != (CLIP_SAMPLES * CLIPS_PER_SUBJECT, 4):
            raise ValueError(f"Unexpected accelerometer shape for subject {subject}")
        acc_file_ts = acc_matrix[:, 0]
        radar_ts, radar_points = read_radar(sdir / "radar.csv")
        lidar_matrix = np.loadtxt(sdir / "LIDAR.csv", delimiter=",", dtype=np.float64)
        ir_matrix = np.loadtxt(sdir / "ir_camera.csv", delimiter=",", dtype=np.float64)
        nonfinite["accelerometer"] += int((~np.isfinite(acc_matrix)).sum())
        nonfinite["radar"] += sum(int((~np.isfinite(f)).sum()) for f in radar_points)
        nonfinite["LIDAR"] += int((~np.isfinite(lidar_matrix)).sum())
        nonfinite["ir_camera"] += int((~np.isfinite(ir_matrix)).sum())
        raw_empty = sum(len(f) == 0 for f in radar_points)
        raw_max_targets = max((len(f) for f in radar_points), default=0)
        radar_raw_frames += len(radar_points)
        radar_raw_empty += raw_empty
        radar_raw_max_targets = max(radar_raw_max_targets, raw_max_targets)

        modality_ts = {
            "accelerometer": acc_file_ts, "radar": radar_ts,
            "LIDAR": lidar_matrix[:, 0], "ir_camera": ir_matrix[:, 0],
        }
        for modality_position, modality in enumerate(MODALITIES):
            for event in range(10):
                position = int(indices[modality][event, subject - 1])
                if 0 <= position < len(modality_ts[modality]):
                    sync_offsets[subject - 1, event, modality_position] = (
                        modality_ts[modality][position] - falls[event, subject - 1]
                    )
        event_valid[subject - 1] = np.all(np.abs(sync_offsets[subject - 1]) <= 2.0, axis=1)
        for event in range(10):
            position = int(acc_index[event, subject - 1])
            event_blocks[subject - 1, event] = position // CLIP_SAMPLES
            event_offsets[subject - 1, event] = position % CLIP_SAMPLES

        coverage = {m: [] for m in MODALITIES}
        empty_radar_in_clips = 0
        for clip in range(CLIPS_PER_SUBJECT):
            flat = (subject - 1) * CLIPS_PER_SUBJECT + clip
            block = acc_matrix[clip * CLIP_SAMPLES:(clip + 1) * CLIP_SAMPLES]
            t0, t1 = float(block[0, 0]), float(block[-1, 0])
            if t1 < t0:
                t0, t1 = t1, t0
            subjects[flat], clips[flat] = subject, clip + 1
            clip_start[flat], clip_end[flat] = t0, t1
            acc[flat] = block[:, 1:4]
            acc_times[flat] = block[:, 0] - t0
            here = np.flatnonzero(event_blocks[subject - 1] == clip)
            if here.size:
                fall_event_ids[flat, here] = True
                labels[flat] = 1

            ridx = select_rows(radar_ts, t0, t1)
            coverage["radar"].append(len(ridx))
            if len(ridx) > RADAR_CLIP_MAX:
                raise ValueError(f"Radar overflow S{subject} C{clip + 1}")
            for frame_position, source_index in enumerate(ridx):
                radar[flat, frame_position] = radar_frame_features(radar_points[source_index])
                radar_mask[flat, frame_position] = True
                radar_times[flat, frame_position] = radar_ts[source_index] - t0
                empty_radar_in_clips += int(len(radar_points[source_index]) == 0)

            lidx = select_rows(lidar_matrix[:, 0], t0, t1)
            coverage["LIDAR"].append(len(lidx))
            if len(lidx) > LIDAR_CLIP_MAX:
                raise ValueError(f"LIDAR overflow S{subject} C{clip + 1}")
            lidar[flat, :len(lidx)] = lidar_matrix[lidx, 1:513]
            lidar_mask[flat, :len(lidx)] = True
            lidar_times[flat, :len(lidx)] = lidar_matrix[lidx, 0] - t0

            iidx = select_rows(ir_matrix[:, 0], t0, t1)
            coverage["ir_camera"].append(len(iidx))
            if len(iidx) > IR_CLIP_MAX:
                raise ValueError(f"IR overflow S{subject} C{clip + 1}: {len(iidx)}")
            ir[flat, :len(iidx)] = ir_matrix[iidx, 1:769]
            ir_mask[flat, :len(iidx)] = True
            ir_times[flat, :len(iidx)] = ir_matrix[iidx, 0] - t0
            coverage["accelerometer"].append(CLIP_SAMPLES)

        review_flag[(subject - 1) * CLIPS_PER_SUBJECT + 7] = subject == 3
        acc_dt = np.diff(acc_file_ts)
        per_subject[f"subject_{subject}"] = {
            "accelerometer_samples": int(len(acc_file_ts)),
            "timestamp_monotonic": bool(np.all(acc_dt > 0)),
            "number_of_timestamp_jumps": int(np.sum(np.abs(acc_dt) > 1.0)),
            "largest_abs_jump_s": float(np.max(np.abs(acc_dt))),
            "radar_frames": int(len(radar_ts)),
            "radar_empty_frames": int(raw_empty),
            "radar_max_targets": int(raw_max_targets),
            "radar_empty_frames_in_clips": int(empty_radar_in_clips),
            "lidar_frames": int(len(lidar_matrix)),
            "ir_frames": int(len(ir_matrix)),
            "fall_clips": int(len(np.unique(event_blocks[subject - 1]))),
            "coverage_min": {m: int(min(v)) for m, v in coverage.items()},
            "coverage_max": {m: int(max(v)) for m, v in coverage.items()},
        }
        print(f"S{subject}: fall_clips={per_subject[f'subject_{subject}']['fall_clips']} empty_radar={raw_empty}", flush=True)

    event_valid[2, 1] = False
    review_reason = np.full(n_clips, "", dtype="<U180")
    review_reason[(3 - 1) * CLIPS_PER_SUBJECT + 7] = (
        "subject_3 clip 8 has no index entry and no nearby annotation; kept as no-fall for audit."
    )

    window_acc, window_radar, window_radar_mask = [], [], []
    window_labels, window_subjects, window_clips, window_events = [], [], [], []
    window_starts, window_ends = [], []
    rng = np.random.default_rng(20261104)

    for subject in SUBJECTS:
        subject_slice = slice((subject - 1) * CLIPS_PER_SUBJECT, subject * CLIPS_PER_SUBJECT)
        valid_events = np.flatnonzero(event_valid[subject - 1])
        for event in valid_events:
            clip = int(event_blocks[subject - 1, event])
            center = int(event_offsets[subject - 1, event])
            start = min(max(center - WINDOW_SAMPLES // 2, 0), CLIP_SAMPLES - WINDOW_SAMPLES)
            flat = (subject - 1) * CLIPS_PER_SUBJECT + clip
            target_time = float(clip_start[flat]) + float(acc_times[flat, center])
            starts = clip_start[flat] + float(acc_times[flat, start])
            ends = clip_start[flat] + float(acc_times[flat, start + WINDOW_SAMPLES - 1])
            real_times = float(clip_start[flat]) + radar_times[flat][radar_mask[flat]].astype(np.float64)
            real_features = radar[flat][radar_mask[flat]]
            selected = np.flatnonzero(np.abs(real_times - target_time) <= GUARD_S + 1e-6)
            selected = selected[:RADAR_WINDOW_MAX]
            rw = np.zeros((RADAR_WINDOW_MAX, N_RADAR_FEATURES), dtype=np.float32)
            rm = np.zeros(RADAR_WINDOW_MAX, dtype=bool)
            rw[:len(selected)] = real_features[selected]
            rm[:len(selected)] = True
            window_acc.append(acc[flat, start:start + WINDOW_SAMPLES])
            window_radar.append(rw)
            window_radar_mask.append(rm)
            window_labels.append(1)
            window_subjects.append(subject)
            window_clips.append(clip + 1)
            window_events.append(event + 1)
            window_starts.append(starts)
            window_ends.append(ends)

        max_start = CLIP_SAMPLES - WINDOW_SAMPLES
        starts_local = np.unique(np.r_[np.arange(0, max_start + 1, 31), max_start])
        valid_times = []
        for event in valid_events:
            clip = int(event_blocks[subject - 1, event])
            center = int(event_offsets[subject - 1, event])
            flat = (subject - 1) * CLIPS_PER_SUBJECT + clip
            valid_times.append(float(clip_start[flat]) + float(acc_times[flat, center]))

        candidates = []
        for clip in range(CLIPS_PER_SUBJECT):
            flat = (subject - 1) * CLIPS_PER_SUBJECT + clip
            for start in starts_local:
                end = start + WINDOW_SAMPLES - 1
                start_abs = clip_start[flat] + float(acc_times[flat, start])
                end_abs = clip_start[flat] + float(acc_times[flat, end])
                if any(not (end_abs < t - GUARD_S or start_abs > t + GUARD_S) for t in valid_times):
                    continue
                candidates.append((clip, int(start), start_abs, end_abs))

        needed = 3 * len(valid_events)
        if len(candidates) < needed:
            raise ValueError(f"Not enough negatives for subject {subject}")
        for candidate_index in rng.choice(len(candidates), size=needed, replace=False):
            clip, start, start_abs, end_abs = candidates[int(candidate_index)]
            flat = (subject - 1) * CLIPS_PER_SUBJECT + clip
            center_time = (start_abs + end_abs) / 2.0
            real_times = float(clip_start[flat]) + radar_times[flat][radar_mask[flat]].astype(np.float64)
            real_features = radar[flat][radar_mask[flat]]
            selected = np.flatnonzero(np.abs(real_times - center_time) <= GUARD_S + 1e-6)
            selected = selected[:RADAR_WINDOW_MAX]
            rw = np.zeros((RADAR_WINDOW_MAX, N_RADAR_FEATURES), dtype=np.float32)
            rm = np.zeros(RADAR_WINDOW_MAX, dtype=bool)
            rw[:len(selected)] = real_features[selected]
            rm[:len(selected)] = True
            window_acc.append(acc[flat, start:start + WINDOW_SAMPLES])
            window_radar.append(rw)
            window_radar_mask.append(rm)
            window_labels.append(0)
            window_subjects.append(subject)
            window_clips.append(clip + 1)
            window_events.append(0)
            window_starts.append(start_abs)
            window_ends.append(end_abs)

    window_acc = np.asarray(window_acc, dtype=np.float32)
    window_radar = np.asarray(window_radar, dtype=np.float32)
    window_radar_mask = np.asarray(window_radar_mask, dtype=bool)
    window_labels = np.asarray(window_labels, dtype=np.int8)
    window_subjects = np.asarray(window_subjects, dtype=np.int16)
    window_clips = np.asarray(window_clips, dtype=np.int16)
    window_events = np.asarray(window_events, dtype=np.int16)
    window_starts = np.asarray(window_starts, dtype=np.float64)
    window_ends = np.asarray(window_ends, dtype=np.float64)

    np.savez_compressed(
        clean_path, acc=acc, acc_times=acc_times,
        radar=radar, radar_mask=radar_mask, radar_times=radar_times,
        lidar=lidar, lidar_mask=lidar_mask, lidar_times=lidar_times,
        ir=ir, ir_mask=ir_mask, ir_times=ir_times,
        label=labels, subject=subjects, clip=clips,
        clip_start=clip_start, clip_end=clip_end,
        fall_event_ids=fall_event_ids, review_flag=review_flag,
        review_reason=review_reason, event_valid=event_valid,
        event_blocks=event_blocks + 1, event_offsets=event_offsets,
        sync_offsets=sync_offsets,
    )
    np.savez_compressed(
        windows_path, acc=window_acc, radar=window_radar,
        radar_mask=window_radar_mask, label=window_labels,
        subject=window_subjects, clip=window_clips, event=window_events,
        start_time=window_starts, end_time=window_ends,
    )

    split_arrays, train_subjects = {}, []
    for fold in range(1, 11):
        train_mask = subjects != fold
        train_subjects.append([s for s in SUBJECTS if s != fold])
        acc_values = acc[train_mask].reshape(-1, 3)
        split_arrays[f"acc_mean_{fold}"] = acc_values.mean(axis=0).astype(np.float32)
        split_arrays[f"acc_std_{fold}"] = safe_std(acc_values)
        radar_values = radar[train_mask][radar_mask[train_mask]]
        split_arrays[f"radar_mean_{fold}"] = radar_values.mean(axis=0).astype(np.float32)
        split_arrays[f"radar_std_{fold}"] = safe_std(radar_values)
        lidar_values = lidar[train_mask][lidar_mask[train_mask]]
        split_arrays[f"lidar_mean_{fold}"] = lidar_values.mean(axis=0).astype(np.float32)
        split_arrays[f"lidar_std_{fold}"] = safe_std(lidar_values)
        ir_values = ir[train_mask][ir_mask[train_mask]]
        split_arrays[f"ir_mean_{fold}"] = ir_values.mean(axis=0).astype(np.float32)
        split_arrays[f"ir_std_{fold}"] = safe_std(ir_values)
    split_arrays["test_subject"] = np.arange(1, 11, dtype=np.int16)
    split_arrays["train_subject_matrix"] = np.asarray(train_subjects, dtype=np.int16)
    np.savez_compressed(splits_path, **split_arrays)

    rates = {}
    for modality in MODALITIES:
        values = []
        for subject in SUBJECTS:
            ts = read_ts(RAW / f"subject_{subject}" / f"{modality}.csv")
            values.append(1.0 / float(np.median(np.diff(ts))))
        rates[modality] = {
            "mean_hz": float(np.mean(values)),
            "min_hz": float(np.min(values)),
            "max_hz": float(np.max(values)),
        }

    sync_summary = {}
    for modality_position, modality in enumerate(MODALITIES):
        values = sync_offsets[:, :, modality_position]
        finite = values[np.isfinite(values)]
        outliers = []
        for subject_index in range(10):
            for event in range(10):
                value = values[subject_index, event]
                if np.isfinite(value) and abs(value) > 2.0:
                    outliers.append({
                        "subject": subject_index + 1, "event": event + 1,
                        "offset_s": round(float(value), 2),
                    })
        sync_summary[modality] = {
            "median_offset_s": float(np.median(finite)),
            "p90_abs_offset_s": float(np.percentile(np.abs(finite), 90)),
            "outliers_gt_2s": outliers,
        }

    valid_events = int(event_valid.sum())
    metadata = {
        "dataset": "QUIDA",
        "version": "1.0",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "clip_definition": {
            "samples": CLIP_SAMPLES,
            "duration_s": 10.0,
            "clips_per_subject": CLIPS_PER_SUBJECT,
            "total_clips": int(n_clips),
            "rule": "positive when an accelerometer index belongs to the fixed 625-sample block",
        },
        "counts": {
            "subjects": 10,
            "fall_clips": int(labels.sum()),
            "no_fall_clips": int((labels == 0).sum()),
            "fall_events": 100,
            "valid_fall_events": valid_events,
            "invalid_fall_events": 100 - valid_events,
            "four_second_windows": int(len(window_labels)),
            "positive_4s_windows": int(window_labels.sum()),
            "negative_4s_windows": int((window_labels == 0).sum()),
        },
        "sampling_rates": rates,
        "sync": sync_summary,
        "integrity": {
            "nonfinite_values": nonfinite,
            "radar_raw_frames": int(radar_raw_frames),
            "radar_empty_raw_frames": int(radar_raw_empty),
            "radar_empty_fraction": float(radar_raw_empty / radar_raw_frames),
            "radar_max_targets": int(radar_raw_max_targets),
            "raw_files_modified": False,
        },
        "per_subject": per_subject,
        "radar_features": RADAR_FEATURES,
        "lidar_columns": {name: list(bounds) for name, bounds in LIDAR_BLOCKS.items()},
        "arrays": {
            "quida_clean.npz": {
                "acc": {"shape": list(acc.shape), "dtype": str(acc.dtype)},
                "acc_times": {"shape": list(acc_times.shape), "dtype": str(acc_times.dtype)},
                "radar": {"shape": list(radar.shape), "dtype": str(radar.dtype)},
                "radar_mask": {"shape": list(radar_mask.shape), "dtype": str(radar_mask.dtype)},
                "radar_times": {"shape": list(radar_times.shape), "dtype": str(radar_times.dtype)},
                "lidar": {"shape": list(lidar.shape), "dtype": str(lidar.dtype)},
                "lidar_mask": {"shape": list(lidar_mask.shape), "dtype": str(lidar_mask.dtype)},
                "lidar_times": {"shape": list(lidar_times.shape), "dtype": str(lidar_times.dtype)},
                "ir": {"shape": list(ir.shape), "dtype": str(ir.dtype)},
                "ir_mask": {"shape": list(ir_mask.shape), "dtype": str(ir_mask.dtype)},
                "ir_times": {"shape": list(ir_times.shape), "dtype": str(ir_times.dtype)},
                "label": {"shape": list(labels.shape), "dtype": str(labels.dtype)},
                "fall_event_ids": {"shape": list(fall_event_ids.shape), "dtype": str(fall_event_ids.dtype)},
                "event_valid": {"shape": list(event_valid.shape), "dtype": str(event_valid.dtype)},
                "sync_offsets": {"shape": list(sync_offsets.shape), "dtype": str(sync_offsets.dtype)},
            },
            "quida_windows_4s.npz": {
                "acc": {"shape": list(window_acc.shape), "dtype": str(window_acc.dtype)},
                "radar": {"shape": list(window_radar.shape), "dtype": str(window_radar.dtype)},
                "radar_mask": {"shape": list(window_radar_mask.shape), "dtype": str(window_radar_mask.dtype)},
                "label": {"shape": list(window_labels.shape), "dtype": str(window_labels.dtype)},
            },
            "splits_loso.npz": {
                "folds": 10,
                "rule": "test_subject=f; train_subject_matrix contains the other nine subjects",
                "stats": "mean/std computed only from training subjects for each fold",
            },
        },
        "decisions": {
            "segmentation": "fixed 625-sample blocks, never time-gap splitting",
            "subject_8": "clips 9-11 are chronologically out of order; fixed blocks preserve them and labels come from the index matrix",
            "subject_3_event_2": "excluded from event-level windows; clip 4 remains positive because it contains valid event 1",
            "subject_3_clip_8": "kept as no-fall with review_flag; not silently relabelled",
            "radar": "empty detection frames are retained, with target_count=0 and empty_frame=1",
            "normalisation": "apply only the statistics belonging to the training fold",
        },
        "excluded_events": [
            {"subject": 3, "event": 2, "reason": "four sensor indices disagree with falls.csv by about 10 s"}
        ],
        "reproduce": [
            "D:\\Anaconda\\python.exe code\\build_clean_dataset.py --overwrite",
            "D:\\Anaconda\\python.exe code\\verify_clean_dataset.py",
            "D:\\Anaconda\\python.exe code\\train_preliminary_baselines.py",
        ],
    }
    metadata_path = out / "dataset_metadata.json"
    metadata_path.write_text(json.dumps(json_safe(metadata), ensure_ascii=False, indent=2), encoding="utf-8")

    data_card = f"""# QUIDA processed data card

Generated: {metadata['created_utc']}

| File | Contents |
|---|---|
| `quida_clean.npz` | 130 fixed 10 s clips: four modalities, labels, masks and timestamps |
| `quida_windows_4s.npz` | {len(window_labels)} four-second windows: {int(window_labels.sum())} fall / {int((window_labels == 0).sum())} no-fall |
| `splits_loso.npz` | 10 leave-one-subject-out folds and training-only normalisation statistics |

```python
import numpy as np
d = np.load('data_processed/quida_clean.npz')
w = np.load('data_processed/quida_windows_4s.npz')
print(d['acc'].shape, d['radar'].shape, d['label'].sum())
print(w['acc'].shape, w['radar'].shape, w['label'].sum())
```

Rules:

- Clip label = 1 when at least one accelerometer index falls in the fixed 625-sample block.
- `event_valid` marks subject 3 / fall 2. Exclude it from event-level windows; do not re-label clip 4.
- Radar empty detections are valid observations (`empty_frame=1`); do not drop them.
- Padded rows have `*_mask=False`. They are not missing sensor samples.
- Normalise each LOSO fold with the matching fold statistics in `splits_loso.npz`.
"""
    (out / "data_card.md").write_text(data_card, encoding="utf-8")

    manifest = {
        "files": {
            clean_path.name: {"bytes": clean_path.stat().st_size, "sha256": sha256_file(clean_path)},
            windows_path.name: {"bytes": windows_path.stat().st_size, "sha256": sha256_file(windows_path)},
            splits_path.name: {"bytes": splits_path.stat().st_size, "sha256": sha256_file(splits_path)},
            metadata_path.name: {"bytes": metadata_path.stat().st_size, "sha256": sha256_file(metadata_path)},
        }
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("\nBUILT")
    print(f"  clips   : {n_clips} ({int(labels.sum())} fall / {int((labels == 0).sum())} no-fall)")
    print(f"  windows : {len(window_labels)} ({int(window_labels.sum())} fall / {int((window_labels == 0).sum())} no-fall)")
    print(f"  events  : {valid_events}/100 valid")
    print(f"  output  : {out}")


if __name__ == "__main__":
    main()
