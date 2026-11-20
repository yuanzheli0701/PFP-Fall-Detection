#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Verification pass over the QUIDA raw data (numbers used in the data cleaning report).

Re-measures, directly from the files: sampling rates, fixed 625-sample clip
segmentation, fall-to-clip mapping, index/timestamp synchronization, NaN/inf
integrity, radar frame structure. Read-only: no file in data_raw is modified.

Usage:
    python scripts/verifier_donnees_quida.py
"""
import os, csv, json
import numpy as np

RACINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data_raw")
MODS = ["accelerometer", "radar", "LIDAR", "ir_camera"]
NB = 10
out = {}
def p(*a):
    print(*a, flush=True)

def ts_col(path):
    vals = []
    with open(path) as f:
        for line in f:
            first = line.split(",")[0].strip()
            if first:
                vals.append(float(first))
    return np.asarray(vals)

def mat(path):
    with open(path, newline="") as f:
        return np.array([[float(v) for v in row] for row in csv.reader(f) if row])

chutes = mat(os.path.join(RACINE, "falls.csv"))
acc_idx = mat(os.path.join(RACINE, "accelerometer.csv"))
p("falls.csv", chutes.shape, "acc index", acc_idx.shape)

p("\n== 1. Accelerometer: samples, fixed 625 blocks, fall blocks ==")
acc_ts = {}
subj_info = {}
tot_fall_blocks = 0
for s in range(1, NB + 1):
    ts = ts_col(os.path.join(RACINE, "subject_%d" % s, "accelerometer.csv"))
    acc_ts[s] = ts
    n = len(ts)
    fb = sorted(set(int(acc_idx[e, s - 1]) // 625 for e in range(10)))
    subj_info[s] = dict(samples=n, blocks=n // 625, fall_blocks=fb)
    tot_fall_blocks += len(fb)
    p("subject_%d: samples=%d blocks=%d fall_blocks=%d %s" % (s, n, n // 625, len(fb), fb))
p("TOTAL fall blocks=%d  no-fall=%d" % (tot_fall_blocks, 130 - tot_fall_blocks))

p("\n== 2. Time-gap segmentation (naive) ==")
def segments(ts, factor=10.0):
    d = np.diff(ts); med = float(np.median(d))
    cuts = np.where(d > factor * med)[0]
    b = np.concatenate(([-1], cuts, [len(ts) - 1]))
    return [(int(b[i] + 1), int(b[i + 1])) for i in range(len(b) - 1)]

tot_seg = tot_seg_fall = 0
seg_counts = {}
for s in range(1, NB + 1):
    ts = acc_ts[s]
    segs = segments(ts)
    mids = np.array([(ts[a] + ts[b]) / 2 for a, b in segs])
    used = set()
    for t in chutes[:, s - 1]:
        used.add(int(np.argmin(np.abs(mids - t))))
    seg_counts[s] = len(segs)
    tot_seg += len(segs); tot_seg_fall += len(used)
    p("subject_%d: %d segments, %d mapped fall windows" % (s, len(segs), len(used)))
p("TOTAL segments=%d with fall=%d without=%d" % (tot_seg, tot_seg_fall, tot_seg - tot_seg_fall))

p("\n== 3. subject_8 timestamp anomalies ==")
ts8 = acc_ts[8]
d8 = np.diff(ts8)
mn = int(np.argmin(d8))
p("most negative jump at sample index %d: %.1f s (dt=%.3fs)" % (mn, d8[mn], d8[mn]))
p("median dt=%.5f -> %.2f Hz" % (np.median(d8), 1 / np.median(d8)))
idx8 = acc_idx[:, 7]
p("subject_8 index positions per event:", [int(v) for v in idx8])
p("blocks:", [int(v) // 625 for v in idx8])
p("falls.csv ts per event:", ["%.1f" % v for v in chutes[:, 7]])
p("acc ts at positions:", ["%.1f" % ts8[int(v)] if 0 <= int(v) < len(ts8) else "OOR" for v in idx8])

p("\n== 4. Sync offsets ==")
sync = {}
for m in MODS:
    idx = mat(os.path.join(RACINE, m + ".csv"))
    offs = []
    detail = []
    for s in range(1, NB + 1):
        ts = ts_col(os.path.join(RACINE, "subject_%d" % s, m + ".csv"))
        for e in range(10):
            pos = int(idx[e, s - 1])
            if 0 <= pos < len(ts):
                o = ts[pos] - chutes[e, s - 1]
                offs.append(o); detail.append((s, e + 1, pos, o))
    offs = np.asarray(offs)
    outl = [(s, e, pos, "%.2f" % o) for s, e, pos, o in detail if abs(o) > 2.0]
    sync[m] = dict(median=float(np.median(offs)), p90=float(np.percentile(np.abs(offs), 90)),
                   n=len(offs), outliers=outl)
    p("%-14s n=%d median=%+.2f s p90=%.2f s max|dev|=%.2f outliers>2s=%s"
      % (m, len(offs), np.median(offs), np.percentile(np.abs(offs), 90), np.max(np.abs(offs)), outl))

p("\n== 5. Integrity (NaN / inf) ==")
integ = {}
# accelerometer via numpy
nan = inf = rows = 0
for s in range(1, NB + 1):
    a = np.loadtxt(os.path.join(RACINE, "subject_%d" % s, "accelerometer.csv"), delimiter=",")
    rows += a.shape[0]
    nan += int(np.isnan(a).sum()); inf += int(np.isinf(a).sum())
integ["accelerometer"] = dict(rows=rows, nan=nan, inf=inf)
p("accelerometer rows=%d nan=%d inf=%d" % (rows, nan, inf))
from pandas import read_csv
for m in ["LIDAR", "ir_camera"]:
    nan = inf = rows = 0
    for s in range(1, NB + 1):
        df = read_csv(os.path.join(RACINE, "subject_%d" % s, m + ".csv"), header=None)
        a = df.values.astype(float)
        rows += a.shape[0]
        nan += int(np.isnan(a).sum()); inf += int(np.isinf(a).sum())
    integ[m] = dict(rows=rows, nan=nan, inf=inf)
    p("%s rows=%d nan=%d inf=%d" % (m, rows, nan, inf))

p("\n== 6. Radar structure ==")
tot_frames = tot_empty = 0
maxt = 0
for s in range(1, NB + 1):
    path = os.path.join(RACINE, "subject_%d" % s, "radar.csv")
    frames = empty = 0; mxt = 0
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            ncol = line.count(",") + 1
            frames += 1
            tgt = (ncol - 1) // 7
            if tgt == 0:
                empty += 1
            if tgt > mxt:
                mxt = tgt
    ts = ts_col(path)
    segs = len(segments(ts))
    tot_frames += frames; tot_empty += empty; maxt = max(maxt, mxt)
    p("subject_%d: frames=%d empty=%d max_targets=%d segments=%d freq=%.2f Hz"
      % (s, frames, empty, mxt, segs, 1 / np.median(np.diff(ts))))
p("TOTAL radar frames=%d empty=%d max_targets=%d" % (tot_frames, tot_empty, maxt))

p("\n== 7. Sampling rates per modality (median over subjects) ==")
rates = {}
for m in MODS:
    fr = []
    for s in range(1, NB + 1):
        ts = ts_col(os.path.join(RACINE, "subject_%d" % s, m + ".csv"))
        fr.append(1.0 / float(np.median(np.diff(ts))))
    rates[m] = (float(np.mean(fr)), float(np.min(fr)), float(np.max(fr)))
    p("%-14s mean=%.2f Hz  min=%.2f  max=%.2f" % (m, np.mean(fr), np.min(fr), np.max(fr)))

p("\n== 8. File sizes (MB per subject) ==")
sizes = {}
for m in MODS:
    vals = []
    for s in range(1, NB + 1):
        vals.append(os.path.getsize(os.path.join(RACINE, "subject_%d" % s, m + ".csv")) / 1e6)
    sizes[m] = (min(vals), max(vals))
    p("%-14s %.1f - %.1f MB" % (m, min(vals), max(vals)))

p("\n== 9. subject_3 / fall 2 detail ==")
idx3 = mat(os.path.join(RACINE, "accelerometer.csv"))[:, 2]
for e in range(10):
    pos = int(idx3[e]); ts = acc_ts[3]
    p("event %d pos %d ts=%.2f falls=%.2f off=%+.2f s block=%d" % (e + 1, pos, ts[pos], chutes[e, 2], ts[pos] - chutes[e, 2], pos // 625))

p("\n== 10. Per-subject acc segments gap check (first gap sizes) ==")
ts1 = acc_ts[1]
d1 = np.diff(ts1)
gaps = d1[d1 > 10 * np.median(d1)]
p("subject_1 gaps (s):", ["%.1f" % g for g in gaps], "n=%d" % len(gaps))

out = dict(subj_info={str(k): v for k, v in subj_info.items()}, sync=sync, integ=integ,
           tot_fall_blocks=tot_fall_blocks, tot_seg=tot_seg, tot_seg_fall=tot_seg_fall,
           radar=dict(frames=tot_frames, empty=tot_empty, max_targets=maxt),
           rates=rates, sizes={k: list(v) for k, v in sizes.items()})
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_work", "report_numbers.json"), "w") as f:
    json.dump(out, f, indent=1)
p("\nDONE")

