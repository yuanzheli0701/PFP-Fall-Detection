# PFP — Détection de chutes (QUIDA)

Projet de fin de période : comparaison d'une **classification supervisée directe** et d'une
**classification par distances apprises** sur le jeu de données **QUIDA**, capteur par capteur
puis en fusion, avec une quantité d'entraînement limitée. Évaluation sur des **sujets non vus**.

> **État au 2026-11-04 :** le nettoyage des données et les baselines de validation sont terminés.
> La vérification indépendante passe **130/130 contrôles**. Le support de présentation en anglais
> est disponible dans `slides/QUIDA_Data_Cleaning_EN_WhiteBlue.pptx`.

## Organisation du dépôt

```
.
├── Planning_Projet_Detection_Chutes.docx    # consignes du projet (fourni)
├── QUIDA_Dataset_Overview.pptx (1).pptx     # presentation du jeu de donnees (fourni)
├── yjgdv-osfstorage-archive.zip             # archive OSF d'origine (fournie)
├── data_raw/                                # donnees extraites (non versionnees)
│   ├── falls.csv                            # horodatages des chutes (10 evenements x 10 sujets)
│   ├── accelerometer.csv, radar.csv, ...    # index de chaque chute dans le fichier du capteur
│   └── subject_1 ... subject_10/            # accelerometer / radar / LIDAR / ir_camera
├── data_processed/                           # artefacts reproductibles du nettoyage
│   ├── quida_clean.npz                       # 130 clips fixes de 10 s, 4 modalites
│   ├── quida_windows_4s.npz                  # 396 fenetres de 4 s pour les baselines
│   ├── splits_loso.npz                       # 10 folds leave-one-subject-out
│   └── qa_report.json, manifest.json         # controles QA et empreintes SHA-256
├── etat_de_lart/                            # tache 1 : etat de l'art
│   ├── plan_semaines_1_2.md                 # plan d'etude CNN + LSTM (2 semaines)
│   └── bibliographie.md                     # references verifiees et annotees
├── Synthese_CNN_LSTM.docx                   # synthese CNN / LSTM (chinois)
├── Synthese_CNN_LSTM_EN.docx                # synthese CNN / LSTM (anglais)
├── scripts/
│   ├── explorer_donnees.py                  # exploration + verification de la synchronisation
│   ├── figures_synthese.py                  # figures des syntheses (--lang zh|en)
│   ├── contenu_synthese.py                  # contenu de la synthese (zh)
│   ├── contenu_synthese_en.py               # contenu de la synthese (en)
│   ├── build_synthese_cnn_lstm.py           # construit le .docx (--lang zh|en)
│   ├── build_clean_dataset.py                # construit les donnees nettoyees
│   ├── verify_clean_dataset.py               # QA independante (130 assertions)
│   ├── train_preliminary_baselines.py        # CNN 1D + LSTM radar, validation LOSO
│   └── make_cleaning_figures.py              # figures du rapport / de la presentation
├── reports/                                  # resultats et rapports
├── slides/                                   # presentations du projet
└── figures/                                 # figures generees
```

## Environnement

Python **Anaconda** (tout est deja installe : numpy, pandas, matplotlib, scipy, scikit-learn,
**PyTorch 2.10 CPU**, seaborn, jupyter) :

```powershell
D:\Anaconda\python.exe scripts\explorer_donnees.py --plot
```

> Une GPU NVIDIA RTX 5060 (8 Go) est presente mais PyTorch installe est en version CPU.
> Largement suffisant pour ce projet (donnees legeres) ; on pourra passer en CUDA plus tard si besoin.

## Ce qu'il faut savoir sur les donnees (verifie le 2026-11-04)

| Modalite | Frequence mesuree | Remarque |
|---|---|---|
| Accelerometre | 62.5 Hz | 13 fenetres de 10 s (625 pts) par sujet, separees par des coupures |
| Radar | 8.3 Hz | lignes de longueur variable (7 valeurs par cible detectee) |
| LIDAR | **10 Hz** (le PPT annonce 8.3 Hz) | 512 valeurs par trame (panneau 8x8) |
| Camera IR | 2.6 Hz | 768 valeurs = 32x24 temperatures |

- **130 clips fixes de 10 s : 99 avec chute / 31 sans chute** ; apres fenetrage 4 s :
  **396 fenetres = 99 positives / 297 negatives**, soit un ratio 1:3 par sujet.
- Le decoupage se fait en **blocs fixes de 625 echantillons**, jamais par ecart temporel.
- `subject_8`, clips 9-11 : ordre chronologique incoherent. Les blocs fixes preservent chaque clip ;
  les labels viennent de la matrice d'index d'accelerometre.
- `subject_3`, chute 2 : environ **10 s d'ecart** avec `falls.csv`. L'evenement est invalide et exclu
  du niveau evenement, sans relabeler le clip 4 qui contient une autre chute valide.
- `subject_3`, clip 8 : conserve comme no-fall avec `review_flag`, jamais relabelle silencieusement.
- Les **1 377 trames radar vides** (3.74 % des 36 838 trames brutes) restent dans les donnees avec
  `target_count=0`, `empty_frame=1`; ce sont des observations valides, pas des valeurs manquantes.
- Synchronisation sur temps absolu : ecart median **0.34-0.72 s** selon la modalite,
  P90 absolu **<= 1.10 s**; 99/100 evenements sont valides.

## Verification de l'installation (a relancer apres tout changement)

```powershell
D:\Anaconda\python.exe scripts\verifier_installation.py
```

Resultat verifie le 2026-09-28 : Python 3.13.9 (Anaconda), numpy/pandas/matplotlib/scipy/
scikit-learn/seaborn presents, **PyTorch 2.10 CPU**, donnees lisibles, **130 clips** construits,
CNN et LSTM entrainables et evaluables sur sujets non vus (environ 5 s pour le CNN et 9 s pour le
LSTM par fold, en moyenne, sur CPU).

Piege a connaitre : `subject_8\accelerometer.csv` contient les clips des chutes 6 et 7
**dans le desordre** (saut de -67 s). Un decoupage par intervalles de temps fusionne deux clips ;
il faut decouper en **blocs fixes de 625 echantillons** et localiser les chutes avec le
fichier d'index `data_raw/accelerometer.csv` (position // 625).

## Nettoyage et test preliminaire (2026-11-04)

Commandes de reproduction, depuis la racine du depot :

```powershell
D:\Anaconda\python.exe scripts\build_clean_dataset.py --overwrite
D:\Anaconda\python.exe scripts\verify_clean_dataset.py
D:\Anaconda\python.exe scripts\train_preliminary_baselines.py
D:\Anaconda\python.exe scripts\make_cleaning_figures.py --theme light
```

Controle qualite : **PASS, 130 assertions, 0 echec**, aucune valeur non finie, fichiers bruts non
modifies, empreintes SHA-256 conformes. Les artefacts et le journal complet sont dans
`data_processed/` et `reports/preliminary_baselines.json`.

Baselines preliminaires, validation **leave-one-subject-out** sur 396 fenetres :

| Modele | Entree | TN / FP / FN / TP | F1 | Recall | Specificity | AUROC |
|---|---|---:|---:|---:|---:|---:|
| 1D-CNN | accelerometre brut | 287 / 10 / 0 / 99 | **0.952** | 1.000 | 0.966 | 0.995 |
| LSTM | 22 features radar + masque | 289 / 8 / 3 / 96 | **0.946** | 0.970 | 0.973 | 0.988 |

Ces scores servent a valider de bout en bout le pipeline et le protocole LOSO. Ils ne constituent
pas encore une revendication de generalisation : six folds sur dix saturent a F1 = 1.000 et les
negatifs viennent surtout de sequences de marche. Le rapport courant est
`reports/Data_Cleaning_Report_QUIDA_EN_2026-11-04.md`.

## Suite

1. Semaines 1-2 : etudier CNN et LSTM -> `etat_de_lart/plan_semaines_1_2.md` et les deux syntheses
   (`Synthese_CNN_LSTM.docx`, `Synthese_CNN_LSTM_EN.docx`)
2. Renforcer les negatifs difficiles : s'asseoir, se pencher, s'allonger, mouvements brusques non-chute
3. Comparer les baselines supervisees a l'apprentissage metrique (siamese, contrastif / triplet)
4. Fusion accelerometre + radar, puis LIDAR / thermique, avec etude de la degradation en peu de donnees
5. Figer les folds, les metriques et le protocole avant la comparaison finale
