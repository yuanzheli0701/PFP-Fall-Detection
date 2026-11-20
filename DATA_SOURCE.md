# Data availability

This repository contains the code, processed arrays, results, figures and reports
for the QUIDA fall-detection project.

The raw QUIDA CSV files (`02_Experiments/Current_Phase_Data_Cleaning_and_Baselines/data_raw/`)
are **not** included, because of their size and the dataset's redistribution terms.
They are available from the QUIDA/OSF source archive used for this project.

The contents of `data_processed/` are sufficient to run:

```powershell
D:\Anaconda\python.exe code\verify_clean_dataset.py
D:\Anaconda\python.exe code\compare_four_models.py --protocol both
D:\Anaconda\python.exe code\report_four_models.py
D:\Anaconda\python.exe code\make_cleaning_figures.py --theme light
```

Rebuilding the processed arrays from scratch additionally requires the raw CSVs
and `code/build_clean_dataset.py --overwrite`.
