# Current Phase - Data Cleaning and Preliminary Baselines

This folder contains the complete current experiment. Everything needed to rebuild, verify,
train and inspect the cleaned QUIDA dataset is self-contained here.

## Layout

The 2026-11-17 four-model comparison uses `code/compare_four_models.py`.
Its main protocol is shuffled stratified window-level five-fold evaluation, without
subject or source-clip grouping; supplementary LOSO evaluates all four models too.
See [FOUR_MODEL_PROTOCOL.md](FOUR_MODEL_PROTOCOL.md) for splits and training rules.
New outputs go to `results/four_model_comparison/`; historical baselines below remain separate.

| Path | Contents |
|---|---|
| `code/` | Data exploration, cleaning, QA, baseline training and figure scripts |
| `data_raw/` | Original QUIDA CSV files; read-only |
| `data_processed/` | Cleaned 10-second clips, 4-second windows, LOSO splits, QA receipt and indexes |
| `results/` | Preliminary baseline metrics and window-level predictions |
| `figures/cleaning_light/` | White-background evidence figures |

## Dataset snapshot

- 10 subjects and 45 source CSV files.
- 130 fixed 10-second clips: **99 fall / 31 no-fall**.
- 396 four-second windows: **99 fall / 297 no-fall**.
- 10 leave-one-subject-out folds, with normalisation statistics computed from training subjects only.
- Independent QA: **130 assertions passed, 0 failed**.

## Reproduce

Run these commands from this folder:

```powershell
D:\Anaconda\python.exe code\build_clean_dataset.py --overwrite
D:\Anaconda\python.exe code\verify_clean_dataset.py
D:\Anaconda\python.exe code\train_preliminary_baselines.py
D:\Anaconda\python.exe code\make_cleaning_figures.py --theme light
```

## Result history

The 2026-11-04 report and deck use the original preliminary run:

- 1D-CNN: F1 **0.952**, recall 1.000, specificity 0.966, AUROC 0.995.
- Radar LSTM: F1 **0.946**, recall 0.970, specificity 0.973, AUROC 0.988.

After the folder reorganization, the baseline script was rerun on 2026-11-05 to verify the new
paths. That run produced:

- 1D-CNN: F1 **0.957**, recall 1.000, specificity 0.970, AUROC 0.995.
- Radar LSTM: F1 **0.951**, recall 0.980, specificity 0.973, AUROC 0.988.

The small difference is consistent with non-bitwise-deterministic CPU training and remains within
the preliminary claim boundary. `results/` contains the 2026-11-05 rerun. The report, deck and
`figures/` retain the 2026-11-04 evidence set unless they are explicitly regenerated later.

## Method notes

- Clip labels come from the accelerometer index matrix, not from file order.
- Fixed 625-sample blocks avoid merging adjacent clips.
- Subject 3 / fall 2 is marked as an invalid event; subject 3 / clip 8 keeps an explicit review flag.
- Empty radar frames are valid observations (`empty_frame=1`), not missing values.
- Do not edit or replace files under `data_raw/`.

