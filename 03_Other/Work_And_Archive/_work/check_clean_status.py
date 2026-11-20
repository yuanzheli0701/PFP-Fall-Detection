# -*- coding: utf-8 -*-
import numpy as np, os, csv

R = "data_raw"

def read_matrix(p):
    with open(p, newline="") as f:
        return np.array([[float(v) for v in row] for row in csv.reader(f) if row])

falls = read_matrix(os.path.join(R, "falls.csv"))
idx = {m: read_matrix(os.path.join(R, m + ".csv")) for m in ["accelerometer", "radar", "LIDAR", "ir_camera"]}

print("=== Fixed 625-block analysis (accelerometer) ===")
total_f = total_n = total_blocks = 0
for s in range(1, 11):
    p = os.path.join(R, "subject_%d" % s, "accelerometer.csv")
    d = np.genfromtxt(p, delimiter=",", dtype=float)
    n = len(d)
    nb = n // 625
    rest = n % 625
    blocks = set()
    badpos = 0
    for e in range(10):
        pos = int(round(idx["accelerometer"][e, s-1]))
        if 0 <= pos < n:
            blocks.add(pos // 625)
        else:
            badpos += 1
    total_f += len(blocks); total_n += nb - len(blocks); total_blocks += nb
    ts = d[:, 0]
    dmin = float(np.min(np.diff(ts))) if n > 1 else 0.0
    print("s%d: N=%d blocks=%d (+%d rest) fall_blocks=%d  min_dt=%+.1fs  bad_pos=%d" % (s, n, nb, rest, len(blocks), dmin, badpos))
print("TOTAL blocks=%d  with_fall=%d  without=%d" % (total_blocks, total_f, total_n))

print()
print("=== NaN / inf checks (all subjects) ===")
for m in ["accelerometer", "LIDAR", "ir_camera"]:
    nan = 0; inf = 0; rows = 0
    for s in range(1, 11):
        p = os.path.join(R, "subject_%d" % s, m + ".csv")
        try:
            d = np.genfromtxt(p, delimiter=",", dtype=float)
        except Exception as ex:
            print(m, "s", s, "parse error", ex); continue
        nan += int(np.isnan(d).sum()); inf += int(np.isinf(d).sum()); rows += len(d)
    print("%-14s rows=%d nan=%d inf=%d" % (m, rows, nan, inf))

print()
print("=== radar frame sizes ===")
from collections import Counter
c = Counter()
for s in range(1, 11):
    p = os.path.join(R, "subject_%d" % s, "radar.csv")
    with open(p) as f:
        for line in f:
            t = line.strip()
            if t:
                c[(len(t.split(",")) - 1)] += 1
print(sorted(c.items())[:12])

print()
print("=== subject_8 accelerometer timestamp jump + subject_8 fall block check ===")
d = np.genfromtxt(os.path.join(R, "subject_8", "accelerometer.csv"), delimiter=",")
ts = d[:, 0]
dd = np.diff(ts)
rank = np.argsort(dd)[:3]
for r in rank:
    print("sample %d -> %d : dt=%+.1f s" % (r, r+1, dd[r]))
pos = [int(round(idx["accelerometer"][e, 7])) for e in range(10)]
print("subject_8 fall positions:", pos)
print("subject_8 fall blocks:", sorted(set(p // 625 for p in pos)))
