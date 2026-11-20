# QUIDA Data Cleaning and Preliminary Testing Report

**Project:** PFP - four-modality fall detection with QUIDA  
**Date:** 4 November 2026  
**Status:** data cleaning complete; independent QA passed; preliminary baselines complete  
**Presentation:** `QUIDA_Data_Cleaning_EN_WhiteBlue.pptx` (same folder)

> This report supersedes the earlier `Data_Cleaning_Report_QUIDA_EN.docx` and PDF drafts,
> retained in `../Previous_Versions/`.

## 1. Executive summary

The raw QUIDA corpus has been converted into a reproducible, tested dataset for fall-detection
experiments:

- **130 fixed 10-second clips** from 10 subjects: **99 fall / 31 no-fall**.
- **396 four-second windows**: **99 fall / 297 no-fall**, with a 1:3 ratio per subject.
- **10 leave-one-subject-out (LOSO) folds**, with normalisation statistics computed only on each
  training partition.
- Independent QA: **130/130 checks passed**, no failures, no non-finite values, and all SHA-256
  checksums matched.
- Preliminary pooled results: 1D-CNN **F1 0.952**, radar LSTM **F1 0.946**.

The scores demonstrate that the complete path (cleaning, windowing, training, prediction and
reporting) works. They are deliberately presented as **preliminary pipeline-validation baselines**,
not as evidence of final clinical or cross-dataset generalisation.

## 2. Input data and sampling

The cleaned dataset covers 10 subjects and 45 raw CSV files.

| Modality | Sensor | Native rhythm | Stored representation |
|---|---|---:|---|
| Accelerometer | 3-axis inertial signal | 62.5 Hz | 625 x 3 samples per 10 s clip |
| Radar | Millimetre-wave radar | 8.33 Hz | Up to 90 frames x 22 aggregated features + mask |
| LiDAR | SPAD depth array | 10.0 Hz | Up to 105 frames x 512 values + mask |
| Thermal | Infrared camera | 2.60 Hz | Up to 40 frames x 768 values + mask |

Because the sampling rates differ by up to 24x, all modalities are aligned on absolute time.
The median index-to-annotation offset is 0.34-0.72 s depending on modality; the P90 absolute
offset remains at or below 1.10 s.

## 3. Cleaning protocol

The pipeline applies six explicit transformations:

1. **Read source files without modification.** Raw CSV, index and annotation files remain immutable.
2. **Slice fixed 625-sample blocks.** Each block is one 10-second accelerometer clip. Time-gap
   segmentation is intentionally avoided because a temporal gap can merge two adjacent files.
3. **Assign labels from the accelerometer index matrix.** A clip is positive when at least one
   valid accelerometer index falls inside its fixed block.
4. **Align clocks on absolute timestamps.** Timestamps retain float64 precision before windowing.
5. **Preserve native structure.** Variable-length radar/LiDAR/thermal rows use explicit masks;
   padded rows are not treated as missing observations.
6. **Build model inputs.** Four-second windows, LOSO folds and training-only normalisation are
   generated from the cleaned arrays.

### Edge cases retained explicitly

- **Subject 3 / fall event 2:** approximately 10 s offset across modalities. The event is invalid
  and excluded from event-level windows. Clip 4 stays positive because it contains valid event 1;
  no silent relabelling is performed.
- **Subject 3 / clip 8:** retained as no-fall with an explicit `review_flag`.
- **Subject 8 / clips 9-11:** file order and timestamps disagree. Fixed 625-sample blocks preserve
  each clip; labels come from the index matrix rather than file order.
- **Empty radar frames:** 1,377 of 36,838 raw frames (3.74%) contain no target. They remain valid
  observations with `target_count=0` and `empty_frame=1`.

## 4. Windowing and evaluation protocol

- Window length: **4 s**, corresponding to 250 accelerometer samples.
- Positive windows are centred on each valid fall event and clipped to the source clip bounds.
- Negative candidates are scanned on a fixed **0.5 s** start grid.
- A **2-second guard on each side** prevents negative windows from intersecting the fall buffer.
- Negative sampling: **three negatives per positive window, per subject**, selected without replacement.
- Evaluation: **10-fold LOSO**; no subject appears in both training and test partitions.
- Normalisation: per-channel statistics from training subjects only.

The resulting dataset contains 396 windows. Subject 3 contributes 9 positive and 27 negative
windows; every other subject contributes 10 positive and 30 negative windows.

## 5. Quality assurance

The independent verifier checks array shapes, labels, masks, time axes, LOSO isolation,
normalisation statistics, file manifests and SHA-256 hashes.

| Check group | Result |
|---|---|
| QA status | **PASS** |
| Assertions passed | **130 / 130** |
| Failures | **0** |
| Non-finite sensor values | **0** |
| Raw files modified | **No** |
| Manifest integrity | **All SHA-256 checks passed** |

Machine-readable evidence is stored in
`02_Experiments/Current_Phase_Data_Cleaning_and_Baselines/data_processed/qa_report.json`,
`.../manifest.json` and `.../dataset_metadata.json`.

## 6. Preliminary baselines

Two intentionally small models test the complete learning path:

- **ACC 1D-CNN:** three convolutional blocks, global average pooling and a two-logit head.
- **RADAR LSTM:** packed sequence encoder with 32 hidden units, dropout and a two-logit head.

Training used Adam (learning rate 1e-3, weight decay 1e-4), batch size 32, 45 epochs and seed 2026.
Class weights were computed from the training partition only.

| Model | TN | FP | FN | TP | Accuracy | Precision | Recall | Specificity | F1 | AUROC |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ACC 1D-CNN | 287 | 10 | 0 | 99 | 0.975 | 0.908 | **1.000** | 0.966 | **0.952** | **0.995** |
| RADAR LSTM | 289 | 8 | 3 | 96 | 0.972 | 0.923 | 0.970 | 0.973 | **0.946** | 0.988 |

### Error analysis

- Six of ten held-out folds reach F1 = 1.000.
- **Subject 3** is the main difficulty: 5 false positives for both models; F1 = 0.783.
- **Subject 8** adds 3 false positives for both models; F1 = 0.870.
- The radar model additionally misses 3 falls: 1 on subject 1 and 2 on subject 2.

The saturated folds indicate that the current negative class is still relatively easy. The main
next step is therefore not a larger model, but a harder evaluation set and a stronger protocol.

## 7. Interpretation and next steps

What is supported by this phase:

- The cleaned dataset is reproducible and internally consistent.
- Labels, validity flags, padding masks and review cases are traceable.
- LOSO isolation, time axes and file integrity pass independent checks.
- The full modelling path executes end to end.

What remains open:

- Only 100 annotated fall events from 10 subjects are available.
- Negative windows are dominated by limited walking activity.
- Six saturated folds make the current pooled metrics optimistic.
- The baselines are not yet the final supervised-versus-metric-learning comparison.

Recommended next experiments:

1. Add hard negatives: sitting, bending, lying down and abrupt non-fall motion.
2. Compare direct supervised learning with metric-learning objectives.
3. Fuse accelerometer and radar first, then add LiDAR and thermal.
4. Freeze folds, metrics and preprocessing before the final benchmark.

## 8. Reproduction and deliverables

Run from `02_Experiments/Current_Phase_Data_Cleaning_and_Baselines`:

```powershell
D:\Anaconda\python.exe code\build_clean_dataset.py --overwrite
D:\Anaconda\python.exe code\verify_clean_dataset.py
D:\Anaconda\python.exe code\train_preliminary_baselines.py
D:\Anaconda\python.exe code\make_cleaning_figures.py --theme light
```

Key deliverables:

- `02_Experiments/Current_Phase_Data_Cleaning_and_Baselines/data_processed/quida_clean.npz`:
  130 cleaned 10-second clips.
- `02_Experiments/Current_Phase_Data_Cleaning_and_Baselines/data_processed/quida_windows_4s.npz`:
  396 four-second model windows.
- `02_Experiments/Current_Phase_Data_Cleaning_and_Baselines/data_processed/splits_loso.npz`:
  10 LOSO folds and training-only statistics.
- `02_Experiments/Current_Phase_Data_Cleaning_and_Baselines/data_processed/qa_report.json`:
  full QA receipt.
- `02_Experiments/Current_Phase_Data_Cleaning_and_Baselines/results/preliminary_baselines.json`:
  metrics and per-fold results.
- `02_Experiments/Current_Phase_Data_Cleaning_and_Baselines/results/preliminary_baseline_predictions.csv`:
  window-level predictions.
- `02_Experiments/Current_Phase_Data_Cleaning_and_Baselines/figures/cleaning_light/`:
  white-background evidence figures.
- `QUIDA_Data_Cleaning_EN_WhiteBlue.pptx`: 13-slide English presentation with speaker notes.

**Claim boundary:** the reported scores validate the data and modelling pipeline on this QUIDA
subset. They should not be interpreted as final generalisation performance.
