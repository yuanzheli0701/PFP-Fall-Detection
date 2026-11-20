# Data availability

This repository contains the raw QUIDA CSVs, the processed arrays, the results,
figures and reports for the fall-detection project.

## Raw data

- Location: `02_Experiments/Current_Phase_Data_Cleaning_and_Baselines/data_raw/`
- 10 subjects, 45 CSV files (accelerometer, radar, LiDAR, thermal infrared).
- Source: the QUIDA dataset, publicly available on the Open Science Framework:
  <https://osf.io/yjgdv/>
- Please check the OSF project for the dataset's terms of use and cite the
  QUIDA dataset paper when reusing it.

The OSF archive `03_Other/Project_Inputs/yjgdv-osfstorage-archive.zip` is not
committed: it is the compressed duplicate of `data_raw/` and its single file is
larger than GitHub's 100 MB limit.

## Third-party literature

PDFs under `03_Other/Literature_And_Previous_Stage/Bibliographie_PDF/` are
publisher/arXiv copies of third-party papers and are not redistributed here.
The citation lists (`LISTE_ARTICLES.md`, `LISTE_COMPLEMENTS.md`,
`bibliographie.md`) are included.

## Running from this repository

The processed arrays in `data_processed/` are sufficient for:

```powershell
D:\Anaconda\python.exe code\verify_clean_dataset.py
D:\Anaconda\python.exe code\compare_four_models.py --protocol both
D:\Anaconda\python.exe code\report_four_models.py
D:\Anaconda\python.exe code\make_cleaning_figures.py --theme light
```

Rebuilding the processed arrays from scratch additionally uses
`code/build_clean_dataset.py --overwrite` on the included raw CSVs.
