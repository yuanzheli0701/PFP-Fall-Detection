# PFP - Fall Detection with QUIDA

Four-modality fall detection (accelerometer, radar, LiDAR and thermal infrared) on the
QUIDA dataset, with leave-one-subject-out (LOSO) evaluation.

**Status:** data cleaning complete; independent QA passed; preliminary baselines complete.

## Folder map

| Folder | Purpose |
|---|---|
| `01_Reports_and_Presentation/` | Current report, English slide deck, speech script and previous versions |
| `02_Experiments/Current_Phase_Data_Cleaning_and_Baselines/` | Current experiment: code, raw data, processed arrays, results and figures |
| `03_Other/` | Project inputs, literature, previous-stage material, legacy scripts and build archives |

## Current status

- **2026-11-17 experiment:** paired ACC/RADAR × CNN/LSTM comparison, with mixed-subject
  shuffled stratified window-level five-fold evaluation (no subject/clip grouping) as the main
  experiment and LOSO as supplementary evaluation.
  See `02_Experiments/Current_Phase_Data_Cleaning_and_Baselines/FOUR_MODEL_PROTOCOL.md`.

- **130 fixed 10-second clips**: 99 fall / 31 no-fall.
- **396 four-second windows**: 99 fall / 297 no-fall.
- Independent QA: **130 / 130 checks passed** after the folder reorganization.
- The 2026-11-04 report and deck record the preliminary LOSO baselines:
  **1D-CNN F1 0.952** and **radar LSTM F1 0.946**.
- A post-move verification rerun on 2026-11-05 produced slightly different preliminary
  scores because the CPU training is not bitwise deterministic. See the experiment README.

## Main deliverables

- `01_Reports_and_Presentation/Current/QUIDA_Data_Cleaning_EN_WhiteBlue.pptx`
- `01_Reports_and_Presentation/Current/Data_Cleaning_Report_QUIDA_EN_2026-11-04.md`
- `01_Reports_and_Presentation/Current/QUIDA_Progress_Speech_Script_EN_CN_2026-11-05.pdf`

## Reproduce the current experiment

Run from the experiment directory:

```powershell
cd 02_Experiments\Current_Phase_Data_Cleaning_and_Baselines
D:\Anaconda\python.exe code\build_clean_dataset.py --overwrite
D:\Anaconda\python.exe code\verify_clean_dataset.py
D:\Anaconda\python.exe code\train_preliminary_baselines.py
D:\Anaconda\python.exe code\make_cleaning_figures.py --theme light
```

`data_raw/` is treated as read-only. Generated files go to `data_processed/`,
`results/` and `figures/` inside the current experiment folder.

