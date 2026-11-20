for s in [1, 2, 3, 8]:
    with open("data_raw/subject_%d/accelerometer.csv" % s) as f:
        ls = [f.readline().strip() for _ in range(3)]
    print("s%d:" % s, " | ".join(ls))
