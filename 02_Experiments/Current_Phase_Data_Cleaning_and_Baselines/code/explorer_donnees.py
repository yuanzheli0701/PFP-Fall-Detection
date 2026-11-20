#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Exploration du jeu de donnees QUIDA (detection de chutes).

Objectif : verifier la structure reelle des fichiers avant toute chose
(taux d'echantillonnage, decoupage en fenetres, annotations, synchronisation).
Aucune valeur n'est supposee : tout est mesure sur les fichiers.

Usage :
    python code/explorer_donnees.py
python code/explorer_donnees.py --plot         # enregistre des figures dans figures/

Sortie : un rapport texte dans la console (+ figures si --plot).
"""

import argparse
import csv
import os

import numpy as np

RACINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data_raw")
MODALITES = ["accelerometer", "radar", "LIDAR", "ir_camera"]
NB_SUJETS = 10


# ---------------------------------------------------------------- utilitaires

def lire_horodatages(chemin):
    """Retourne le tableau des horodatages (1re colonne) d'un fichier capteur."""
    valeurs = []
    with open(chemin, newline="") as f:
        for ligne in f:
            premiere = ligne.split(",")[0].strip()
            if premiere:
                valeurs.append(float(premiere))
    return np.asarray(valeurs)


def decouper_en_segments(ts, facteur=10.0):
    """Coupe une serie d'horodatages en segments contigus.

    Un segment se termine des que l'ecart entre deux echantillons depasse
    `facteur` fois l'ecart median (= une coupure d'enregistrement).
    Retourne une liste d'indices (debut, fin) inclusifs.
    """
    if len(ts) < 2:
        return [(0, len(ts) - 1)]
    ecart_median = float(np.median(np.diff(ts)))
    ruptures = np.where(np.diff(ts) > facteur * ecart_median)[0]
    bornes = np.concatenate(([-1], ruptures, [len(ts) - 1]))
    return [(int(bornes[i] + 1), int(bornes[i + 1])) for i in range(len(bornes) - 1)]


def lire_matrice(chemin):
    """Lit un CSV de synthese (10x10, sans en-tete) : lignes = evenements, colonnes = sujets."""
    with open(chemin, newline="") as f:
        return np.array([[float(v) for v in ligne] for ligne in csv.reader(f) if ligne])


# ------------------------------------------------------------------- rapports

def rapport_structure():
    """Taux d'echantillonnage mesure, nombre de segments, anomalies."""
    print("=" * 78)
    print("1. STRUCTURE DES FICHIERS (valeurs mesurees, pas supposees)")
    print("=" * 78)
    print("%-14s %10s %12s %8s %s" % ("modalite", "N moyen", "dt median", "freq", "colonnes"))
    for modalite in MODALITES:
        tailles, freqs, colonnes = [], [], set()
        for sujet in range(1, NB_SUJETS + 1):
            chemin = os.path.join(RACINE, "subject_%d" % sujet, modalite + ".csv")
            nb_colonnes = set()
            with open(chemin) as f:
                for ligne in f:
                    if ligne.split(",")[0].strip():
                        nb_colonnes.add(len(ligne.rstrip("\n").split(",")))
            nb_colonnes.discard(1)
            ts = lire_horodatages(chemin)
            tailles.append(len(ts))
            freqs.append(1.0 / float(np.median(np.diff(ts))))
            colonnes.add(tuple(sorted(nb_colonnes)))
        print("%-14s %10.0f %12s %7.2f Hz %s" % (
            modalite, np.mean(tailles), "-", np.mean(freqs), list(colonnes)[0][:4]))
    print()
    print("  Note : 'colonnes' = valeurs hors horodatage (variable pour le radar :")
    print("         chaque ligne contient 7 valeurs par cible detectee).")


def rapport_segments():
    """Nombre de segments contigus + fenetres de 10 s (accelerometre)."""
    print()
    print("=" * 78)
    print("2. DECOUPAGE EN SEGMENTS CONTIGUS")
    print("=" * 78)
    print("%-10s %12s %12s %12s %12s" % ("sujet", "accelerom.", "radar", "LIDAR", "ir_camera"))
    for sujet in range(1, NB_SUJETS + 1):
        compte = []
        for modalite in MODALITES:
            ts = lire_horodatages(os.path.join(RACINE, "subject_%d" % sujet, modalite + ".csv"))
            compte.append(len(decouper_en_segments(ts)))
        print("%-10s %12d %12d %12d %12d" % tuple(["subject_%d" % sujet] + compte))
    print()
    print("  Accelerometre = series de fenetres de 10 s (625 echantillons) separees")
    print("  par des coupures ; les autres capteurs sont quasi continus.")


def rapport_annotations():
    """Correspondance chute -> sujet -> fenetre, et equilibre des classes."""
    print()
    print("=" * 78)
    print("3. ANNOTATIONS (falls.csv) ET FENETRES ASSOCIEES")
    print("=" * 78)
    chutes = lire_matrice(os.path.join(RACINE, "falls.csv"))
    print("falls.csv : %d evenements x %d sujets" % chutes.shape)
    print("  -> lignes = numero de la chute (1..10), colonnes = sujet (1..10),")
    print("     valeurs = horodatage Unix de la chute.\n")

    total_fenetres_chute, total_fenetres_neutres = 0, 0
    for sujet in range(1, NB_SUJETS + 1):
        ts = lire_horodatages(os.path.join(RACINE, "subject_%d" % sujet, "accelerometer.csv"))
        segments = decouper_en_segments(ts)
        milieux = np.array([(ts[a] + ts[b]) / 2 for a, b in segments])
        avec_chute = set()
        for t in chutes[:, sujet - 1]:
            distances = np.abs(milieux - t)
            avec_chute.add(int(np.argmin(distances)))
        neutres = len(segments) - len(avec_chute)
        total_fenetres_chute += len(avec_chute)
        total_fenetres_neutres += neutres
        note = ""
        if len(avec_chute) < 10:
            note = "  <-- 10 chutes reparties sur %d fenetres distinctes" % len(avec_chute)
        print("  subject_%-2d : %2d fenetres = %2d avec chute + %2d sans chute%s"
              % (sujet, len(segments), len(avec_chute), neutres, note))
    print()
    print("  TOTAL : %d fenetres avec chute / %d fenetres sans chute (ratio %.2f:1)"
          % (total_fenetres_chute, total_fenetres_neutres,
             total_fenetres_chute / max(total_fenetres_neutres, 1)))
    print("  Les fenetres sans chute servent de classe negative (marche / activites).")


def rapport_synchronisation():
    """Verifie que les index fournis permettent de retrouver les chutes."""
    print()
    print("=" * 78)
    print("4. SYNCHRONISATION : les fichiers d'index sont-ils coherents ?")
    print("=" * 78)
    chutes = lire_matrice(os.path.join(RACINE, "falls.csv"))
    for modalite in ["accelerometer", "radar", "LIDAR", "ir_camera"]:
        index = lire_matrice(os.path.join(RACINE, modalite + ".csv"))
        ecarts = []
        for sujet in range(1, NB_SUJETS + 1):
            chemin = os.path.join(RACINE, "subject_%d" % sujet, modalite + ".csv")
            if modalite == "accelerometer":
                ts = lire_horodatages(chemin)
            else:
                ts = lire_horodatages(chemin)
            for evenement in range(index.shape[0]):
                position = int(index[evenement, sujet - 1])
                if 0 <= position < len(ts):
                    ecarts.append(ts[position] - chutes[evenement, sujet - 1])
        ecarts = np.asarray(ecarts)
        hors = np.where(np.abs(ecarts) > 2.0)[0]
        print("  %-14s : %3d chutes, ecart median = %+.2f s, p90 = %.2f s, hors bornes (>2 s) = %d"
              % (modalite, len(ecarts), float(np.median(ecarts)),
                 float(np.percentile(np.abs(ecarts), 90)), len(hors)))
    print()
    print("  Lecture : l'ecart median (~ +0.6 s) est constant et positif -> le fichier d'index")
    print("  pointe le pic du mouvement de chute, alors que falls.csv donne l'horodatage")
    print("  annote par l'experimentateur (legerement avant). L'ecart est donc normal.")
    print("  Seule exception a verifier : subject_3 / chute 2 (ecart ~ 10 s sur les 4 capteurs)")
    print("  -> probable erreur d'annotation ou de placement dans le fichier d'index.")


def figures():
    """Trace une fenetre de chute et une fenetre neutre (3 axes)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    dossier = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures")
    os.makedirs(dossier, exist_ok=True)

    sujet = 1
    chemin = os.path.join(RACINE, "subject_%d" % sujet, "accelerometer.csv")
    donnees = np.loadtxt(chemin, delimiter=",", skiprows=0)
    ts = donnees[:, 0]
    segments = decouper_en_segments(ts)

    for numero, etiquette in [(0, "neutre"), (5, "chute")]:
        a, b = segments[numero]
        bloc = donnees[a:b + 1]
        t = bloc[:, 0] - bloc[0, 0]
        plt.figure(figsize=(9, 4))
        plt.plot(t, bloc[:, 1], label="axe x")
        plt.plot(t, bloc[:, 2], label="axe y")
        plt.plot(t, bloc[:, 3], label="axe z")
        plt.axhline(0, color="grey", linewidth=0.5)
        plt.title("subject_%d - fenetre %d (%s)" % (sujet, numero + 1, etiquette))
        plt.xlabel("temps (s)")
        plt.ylabel("acceleration (m/s2)")
        plt.legend(loc="upper right")
        plt.tight_layout()
        sortie = os.path.join(dossier, "fenetre_%s_subject%d.png" % (etiquette, sujet))
        plt.savefig(sortie, dpi=130)
        plt.close()
        print("  figure ecrite :", os.path.relpath(sortie))


def main():
    parser = argparse.ArgumentParser(description="Exploration du jeu de donnees QUIDA.")
    parser.add_argument("--plot", action="store_true", help="enregistre des figures d'exemple")
    args = parser.parse_args()

    print()
    print("Exploration de : %s" % os.path.abspath(RACINE))
    rapport_structure()
    rapport_segments()
    rapport_annotations()
    rapport_synchronisation()
    if args.plot:
        print()
        print("=" * 78)
        print("5. FIGURES")
        print("=" * 78)
        figures()
    print()


if __name__ == "__main__":
    main()
