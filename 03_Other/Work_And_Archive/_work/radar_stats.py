counts = {}
import os
tot = 0; notarget = 0; mx = 0
for s in range(1, 11):
    p = "data_raw/subject_%d/radar.csv" % s
    with open(p) as f:
        for line in f:
            t = line.strip()
            if not t: continue
            n = len(t.split(",")) - 1
            tot += 1
            k = n // 7
            if k == 0: notarget += 1
            mx = max(mx, k)
            counts[k] = counts.get(k, 0) + 1
print("radar frames total:", tot, " no-target frames:", notarget, " max targets:", mx)
print("targets histogram:", dict(sorted(counts.items())))
print("radar frames per subject ~", tot//10)
