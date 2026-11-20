# QUIDA processed data card

Generated: 2026-11-20T08:18:03.211652+00:00

| File | Contents |
|---|---|
| `quida_clean.npz` | 130 fixed 10 s clips: four modalities, labels, masks and timestamps |
| `quida_windows_4s.npz` | 396 four-second windows: 99 fall / 297 no-fall |
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
