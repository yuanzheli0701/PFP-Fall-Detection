#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Verification de l'installation et test de bout en bout (smoke test).

A executer AVANT toute campagne d'experiences :
    D:\\Anaconda\\python.exe scripts\\verifier_installation.py

Le script verifie :
  1. l'environnement Python (versions, PyTorch, CPU/CUDA) ;
  2. l'integrite des donnees QUIDA (lisibilite, frequences, segments) ;
  3. la construction des tenseurs et des etiquettes ;
  4. un entrainement reel (CNN 1D puis LSTM) avec evaluation sur des sujets non vus,
     en mesurant le temps — ce qui donne une estimation pour le vrai projet.
"""

import os
import sys
import time
import platform
import csv

import numpy as np

RACINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data_raw")
MODALITES = ["accelerometer", "radar", "LIDAR", "ir_camera"]
FREQUENCE = {"accelerometer": 62.5, "radar": 8.31, "LIDAR": 10.0, "ir_camera": 2.6}

SEPARATEUR = "=" * 78


def titre(texte):
    print()
    print(SEPARATEUR)
    print(texte)
    print(SEPARATEUR)


# --------------------------------------------------------------- 1. environnement

def verifier_environnement():
    titre("1. ENVIRONNEMENT PYTHON")
    print("  python      :", sys.version.split()[0], "|", sys.executable)
    print("  plateforme  :", platform.platform())
    paquets = ["numpy", "pandas", "matplotlib", "scipy", "sklearn", "torch", "seaborn"]
    manquants = []
    for nom in paquets:
        try:
            module = __import__(nom)
            print("  %-11s : %s" % (nom, getattr(module, "__version__", "?")))
        except Exception:
            manquants.append(nom)
            print("  %-11s : MANQUANT" % nom)
    try:
        import torch
        print("  torch CPU   : threads =", torch.get_num_threads(),
              "| CUDA =", torch.cuda.is_available())
        if torch.cuda.is_available():
            print("  GPU         :", torch.cuda.get_device_name(0))
        else:
            print("  GPU         : non utilisee (build CPU) — suffisant pour ce projet")
    except Exception as erreur:
        manquants.append("torch")
        print("  torch       : ERREUR", erreur)
    return manquants


# --------------------------------------------------------------------- 2. donnees

def lire_horodatages(chemin):
    valeurs = []
    with open(chemin, newline="") as f:
        for ligne in f:
            premiere = ligne.split(",")[0].strip()
            if premiere:
                valeurs.append(float(premiere))
    return np.asarray(valeurs)


def lire_matrice(chemin):
    with open(chemin, newline="") as f:
        return np.array([[float(v) for v in ligne if v.strip()]
                         for ligne in csv.reader(f) if ligne])


def verifier_donnees():
    titre("2. INTEGRITE DES DONNEES")
    if not os.path.isdir(RACINE):
        print("  ERREUR : dossier introuvable ->", os.path.abspath(RACINE))
        return False, None, None

    chutes = lire_matrice(os.path.join(RACINE, "falls.csv"))
    index_acc = lire_matrice(os.path.join(RACINE, "accelerometer.csv"))
    print("  falls.csv            :", chutes.shape, "(10 chutes x 10 sujets)")
    print("  accelerometer.csv    :", index_acc.shape, "(indice de chaque chute)")

    problemes = []
    avertissements = []
    print()
    print("  %-10s %8s %10s %10s %10s %8s" % ("sujet", "accel.", "radar", "LIDAR", "IR", "couvre"))
    for sujet in range(1, 11):
        longueurs, couvre_tout = {}, True
        premiere_chute, derniere_chute = chutes[:, sujet - 1].min(), chutes[:, sujet - 1].max()
        for modalite in MODALITES:
            chemin = os.path.join(RACINE, "subject_%d" % sujet, modalite + ".csv")
            if not os.path.isfile(chemin):
                problemes.append("manquant: " + chemin)
                longueurs[modalite] = 0
                continue
            try:
                ts = lire_horodatages(chemin)
            except Exception as erreur:
                problemes.append("illisible: %s (%s)" % (chemin, erreur))
                longueurs[modalite] = 0
                continue
            longueurs[modalite] = len(ts)
            if len(ts) < 100:
                problemes.append("trop court: " + chemin)
                continue
            if not np.all(np.diff(ts) > 0):
                avertissements.append(chemin)
            frequence = 1.0 / float(np.median(np.diff(ts)))
            attendue = FREQUENCE[modalite]
            if abs(frequence - attendue) / attendue > 0.05:
                problemes.append("frequence %.2f Hz au lieu de %.2f Hz : %s"
                                 % (frequence, attendue, chemin))
            if ts[0] > premiere_chute or ts[-1] < derniere_chute:
                couvre_tout = False
        print("  %-10s %8d %10d %10d %10d %8s"
              % ("subject_%d" % sujet, longueurs["accelerometer"], longueurs["radar"],
                 longueurs["LIDAR"], longueurs["ir_camera"], "oui" if couvre_tout else "NON"))
        if not couvre_tout:
            problemes.append("enregistrement incomplet pour subject_%d" % sujet)

    print()
    print("  accelerometre        : 13 fenetres de 10 s par sujet (12 pour subject_8)")
    print("  frequences nominales : accel. 62,5 Hz | radar 8,3 Hz | LiDAR 10 Hz | IR 2,6 Hz")
    if avertissements:
        print()
        print("  AVERTISSEMENT (non bloquant) : horodatages non monotones dans")
        for chemin in avertissements:
            print("    -", os.path.relpath(chemin, RACINE))
        print("    Cause connue : pour subject_8, les clips des chutes 6 et 7 sont ranges")
        print("    dans le desordre (saut de -67 s), donc un decoupage par intervalles de")
        print("    temps fusionne deux clips. -> Toujours decouper en blocs FIXES de 625")
        print("    echantillons et localiser les chutes avec le fichier d'index officiel.")
    if problemes:
        print()
        print("  PROBLEMES DETECTES :")
        for probleme in problemes[:10]:
            print("    -", probleme)
    else:
        print()
        print("  -> aucun probleme bloquant (frequences conformes, toutes les chutes couvertes)")
    return (len(problemes) == 0), chutes, index_acc


# ------------------------------------------------------------------- 3. tenseurs

def construire_jeu(chutes, index_acc):
    """Fenetres (N, 3, 625) + etiquettes, par sujet."""
    par_sujet = {}
    for sujet in range(1, 11):
        chemin = os.path.join(RACINE, "subject_%d" % sujet, "accelerometer.csv")
        donnees = np.loadtxt(chemin, delimiter=",")
        signal = donnees[:, 1:4]
        nombre = len(signal) // 625
        fenetres = signal[:nombre * 625].reshape(nombre, 625, 3).transpose(0, 2, 1)
        etiquettes = np.zeros(nombre, dtype=np.int64)
        for evenement in range(index_acc.shape[0]):
            position = int(index_acc[evenement, sujet - 1])
            if 0 <= position < nombre * 625:
                etiquettes[position // 625] = 1
        # normalisation par fenetre et par axe
        moyennes = fenetres.mean(axis=2, keepdims=True)
        ecarts = fenetres.std(axis=2, keepdims=True) + 1e-6
        par_sujet[sujet] = ((fenetres - moyennes) / ecarts, etiquettes)
    return par_sujet


# --------------------------------------------------------------- 4. entrainement

def entrainer(modele, x_app, y_app, x_test, y_test, epochs=15, lot=16):
    import torch
    import torch.nn as nn

    torch.manual_seed(0)
    optimiseur = torch.optim.Adam(modele.parameters(), lr=1e-3)
    perte = nn.CrossEntropyLoss()
    xa = torch.tensor(x_app, dtype=torch.float32)
    ya = torch.tensor(y_app, dtype=torch.long)
    xt = torch.tensor(x_test, dtype=torch.float32)

    debut = time.perf_counter()
    modele.train()
    for _ in range(epochs):
        permutation = torch.randperm(len(xa))
        for i in range(0, len(xa), lot):
            indices = permutation[i:i + lot]
            optimiseur.zero_grad()
            sortie = modele(xa[indices])
            cout = perte(sortie, ya[indices])
            cout.backward()
            optimiseur.step()
    duree = time.perf_counter() - debut

    modele.eval()
    with torch.no_grad():
        predictions = modele(xt).argmax(dim=1).numpy()
    return predictions, duree


def evaluer(y_vrai, y_predit):
    vp = int(((y_vrai == 1) & (y_predit == 1)).sum())
    fp = int(((y_vrai == 0) & (y_predit == 1)).sum())
    fn = int(((y_vrai == 1) & (y_predit == 0)).sum())
    precision = vp / max(vp + fp, 1)
    rappel = vp / max(vp + fn, 1)
    f1 = 2 * precision * rappel / max(precision + rappel, 1e-9)
    exactitude = float((y_vrai == y_predit).mean())
    return exactitude, precision, rappel, f1


def tester_modeles(par_sujet):
    import torch.nn as nn

    titre("3. TEST DE BOUT EN BOUT (entrainement reel sur sujets non vus)")

    class CNN(nn.Module):
        def __init__(self):
            super().__init__()
            self.corps = nn.Sequential(
                nn.Conv1d(3, 16, 5, padding=2), nn.ReLU(), nn.MaxPool1d(2),
                nn.Conv1d(16, 32, 5, padding=2), nn.ReLU(),
                nn.AdaptiveAvgPool1d(1))
            self.tete = nn.Linear(32, 2)

        def forward(self, x):
            return self.tete(self.corps(x).squeeze(-1))

    class ReseauLSTM(nn.Module):
        def __init__(self):
            super().__init__()
            self.lstm = nn.LSTM(input_size=3, hidden_size=32, batch_first=True)
            self.tete = nn.Linear(32, 2)

        def forward(self, x):
            sortie, (etat, _) = self.lstm(x.transpose(1, 2))
            return self.tete(etat[-1])

    resultats = {}
    for nom, fabrique in [("CNN 1D", CNN), ("LSTM", ReseauLSTM)]:
        print()
        print("  --- %s ---" % nom)
        scores = []
        for sujet_test in (9, 10):
            x_app = np.concatenate([par_sujet[s][0] for s in par_sujet if s != sujet_test])
            y_app = np.concatenate([par_sujet[s][1] for s in par_sujet if s != sujet_test])
            x_test, y_test = par_sujet[sujet_test]
            predictions, duree = entrainer(fabrique(), x_app, y_app, x_test, y_test)
            exactitude, precision, rappel, f1 = evaluer(y_test, predictions)
            scores.append((exactitude, precision, rappel, f1, duree))
            print("     sujet %2d : exactitude %.2f | precision %.2f | rappel %.2f | F1 %.2f | %.1f s"
                  % (sujet_test, exactitude, precision, rappel, f1, duree))
        moyenne = np.mean(scores, axis=0)
        resultats[nom] = moyenne
        print("     moyenne  : exactitude %.2f | precision %.2f | rappel %.2f | F1 %.2f | %.1f s"
              % tuple(moyenne))
    return resultats


def main():
    print()
    print("Verification de l'installation — projet detection de chutes (QUIDA)")
    print("Dossier de donnees :", os.path.abspath(RACINE))

    manquants = verifier_environnement()
    donnees_ok, chutes, index_acc = verifier_donnees()

    if manquants:
        print()
        print("  /!\\ paquets manquants :", ", ".join(manquants))
        print("      -> installer avec :  python -m pip install " + " ".join(manquants))
    if not donnees_ok:
        print()
        print("  /!\\ donnees incompletes : corriger avant de lancer des experiences.")

    if donnees_ok and not manquants:
        par_sujet = construire_jeu(chutes, index_acc)
        total = sum(len(v[1]) for v in par_sujet.values())
        positifs = sum(int(v[1].sum()) for v in par_sujet.values())
        titre("   TENSEURS CONSTRUITS")
        print("  fenetres   :", total, "| dont chutes :", positifs,
              "| non-chutes :", total - positifs)
        print("  forme      :", par_sujet[1][0].shape, "(fenetres, axes, echantillons)")
        tester_modeles(par_sujet)
        titre("CONCLUSION")
        print("  Installation operationnelle : donnees lisibles, tenseurs construits,")
        print("  CNN et LSTM entrainables et evaluables sur des sujets non vus.")
        print("  Les scores ci-dessus ne sont PAS des resultats de projet (modeles")
        print("  minimaux, 15 epochs) : ils servent uniquement a valider la chaine.")
    print()


if __name__ == "__main__":
    main()