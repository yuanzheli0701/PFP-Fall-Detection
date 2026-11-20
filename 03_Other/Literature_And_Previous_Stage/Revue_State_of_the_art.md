# Revue du rapport « State of the art » — lecture « avant expérimentation »

- **Document relu :** `State of the art - shared.docx` (version 1.0, 15 pages, 3 996 mots, 3 tableaux, 3 équations, 20 références).
- **Sources utilisées pour la vérification :** texte intégral de Taramasco et al. (2025), PeerJ 13:e19004 (PMC11970414) ; planning du projet (`Planning_Projet_Detection_Chutes.docx`).
- **Aucun résultat d'expérience n'est utilisé ni proposé** : le rapport est relu comme un état de l'art + choix de méthodes, avant toute campagne. Les remarques portent donc uniquement sur (1) l'exactitude par rapport aux sources citées, (2) le contenu de la revue, (3) le protocole écrit au futur, (4) la forme.

---

## 0. Cadre de la relecture

Le rapport est cohérent avec le livrable demandé par le planning : étudier CNN/LSTM, siamois, pertes contrastive et triplet, classification par voisins ou prototypes, puis justifier les méthodes retenues. La structure tient, les équations sont présentes et correctes, les références sont complètes.

Les points ci-dessous sont classés par priorité : **P0** = à corriger avant diffusion, **P1** = renforce nettement le rapport, **P2** = finition.

---

## 1. Exactitude par rapport aux sources (P0/P1)

### 1.1 Ce qui est déjà correct (ne pas y toucher)

Vérifié mot à mot dans le papier : les chiffres épidémiologiques (28–35 % après 65 ans, 32–42 % après 70, cités par Taramasco d'après l'OMS/Kalache), l'accéléromètre à 62,5 Hz porté entre T5 et T10, le radar TI IWR6843AOP 60–64 GHz à 8,3 Hz au plafond, la fenêtre de ±2 s autour de l'annotation, la synchronisation par un mouvement de bras, les 10 sujets (8 hommes, 2 femmes, ~24,5 et 25,5 ans), les 10 types de chute, le fait que les auteurs ne font que caractériser les signaux (norme instantanée plus discriminante pour le radar et l'accéléromètre, différence entre trames pour la caméra thermique et le LiDAR). Rien à corriger sur ces points.

### 1.2 Le ratio 1:3 : préciser « après segmentation »

Texte actuel (§2.3) :

> « The authors segment recordings into windows of ±2 s around each annotated fall, with a fall to non-fall ratio of 1:3. »

Le papier écrit : « segments of equal width were defined using measurements outside the segments labeled as falls, maintaining a balance between fall and no-fall samples at a ratio of 1:N, in this case N = 3 ». Deux précisions à ajouter, purement au niveau de la source :

1. le 1:3 est le ratio du **jeu segmenté**, pas des enregistrements bruts ;
2. le papier décrit l'archive comme des enregistrements par sujet (4 CSV) plus le fichier `Falls.csv` à la racine — **pas** comme un jeu de fenêtres déjà découpées. Le rapport laisse entendre que la segmentation est fournie ; il vaut mieux écrire que les fenêtres sont à reconstruire, et décrire la procédure prévue (fichier d'annotations, repère temporel, nombre d'échantillons par capteur).

Formulation proposée :

> After segmentation, the authors balance the fall and no-fall windows at a ratio of 1:N with N = 3. The distributed archive contains the raw recordings and the fall annotations; the windows are not shipped as such, and must be rebuilt from the annotation file and the sensor time stamps. We therefore state the reconstruction rule explicitly in Section 6.

### 1.3 « A walking sequence provides non-fall data » : à préciser

Le papier prévoit une phase de marche, mais les non-chutes sont définies comme des segments de 4 s pris **en dehors** des segments de chute (pas seulement dans la marche). La phrase du rapport est donc plus restrictive que la source ; à reformuler (« no-fall windows are sampled outside the annotated fall segments, including the walking phase »).

### 1.4 Épidémiologie : citer l'OMS ou Kalache et al. (2007) directement

La tournure « figures reported by the WHO and cited by Taramasco et al. (2025) » est acceptable, mais une référence directe (OMS, ou Kalache et al. 2007, cité par le papier) est plus propre pour un rapport de revue.

### 1.5 Nom du jeu de données

Le nom « QUIDA » n'apparaît ni dans le titre du papier ni dans la description de l'archive (qui est déposée sur OSF). Soit ajouter une note de bas de page qui justifie le nom employé, soit demander confirmation à l'encadrante. Ajouter aussi le DOI OSF (10.17605/OSF.IO/YJGDV) à la référence du jeu de données, en plus du DOI PeerJ.

### 1.6 Références à ajouter

- **Wang, Yan & Oates (2016), *Time Series Classification from Scratch with Deep Neural Networks: A Strong Baseline* (arXiv:1611.06455)** : justifie directement le choix d'un petit 1D-CNN comme baseline, c'est la référence naturelle du §4.1. Elle est déjà dans votre bibliographie de travail mais absente du rapport.
- Une **référence pour la taxonomie early / intermediate / late fusion** (§5) : la classification est énoncée sans source ; une revue de fusion de capteurs (ou une revue de détection de chutes multimodale) suffit.

---

## 2. Contenu à renforcer (P1)

### 2.1 Définir les métriques d'évaluation

Le §6.2 cite rappel/sensibilité, précision, F1, spécificité sans les définir. Ajouter un court paragraphe (ou un tableau) : formule, ce que chaque métrique mesure, et pourquoi l'exactitude est trompeuse en cas de déséquilibre. Ajouter aussi l'asymétrie décisionnelle : une chute manquée et une fausse alarme n'ont pas le même coût (argument utile pour la suite du projet).

### 2.2 CNN vs LSTM : rendre le choix explicite

Le rapport présente les deux familles puis retient un CNN pour l'accéléromètre et un LSTM pour le radar. Ajouter les critères de décision (quantité de données disponible, latence d'inférence, coût d'entraînement, facilité de déploiement) et une phrase de décision unique et assumée. Deux références utiles sont déjà dans la bibliographie : Wang et al. (2016) pour le CNN, Musci et al. (2021) pour le compromis précision/latence du LSTM.

### 2.3 Apprentissage métrique : compléter le choix de conception

- Préciser la **distance** utilisée (euclidienne) et la **normalisation L2** des embeddings (le rapport dit « usually normalized », il faut trancher).
- Indiquer la **dimension d'embedding** prévue et le fait qu'elle sera un hyperparamètre.
- Ajouter un petit tableau comparatif des pertes (contrastive / triplet) : contrainte (absolue vs relative), sensibilité à l'échantillonnage, difficulté de mise en œuvre.

### 2.4 Voisins vs prototypes

L'argument « le vote des k plus proches voisins est biaisé vers la classe majoritaire » est juste ; ajouter le pendant côté prototypes (un seul prototype peut mal représenter une classe multimodale, d'où l'extension à plusieurs prototypes par classe, déjà mentionnée). Citer Snell et al. (2017) et Koch et al. (2015) au moment de l'argument, pas seulement en fin de section.

### 2.5 Fusion

- Sourcer la taxonomie (§1.6).
- Ajouter une phrase sur la **robustesse à une modalité manquante** : c'est un des arguments pratiques en faveur de la fusion tardive, et cela prépare la discussion.
- Conserver la contrainte de synchronisation déjà bien décrite, et préciser la **stratégie de fenêtrage commune** retenue (voir §3 ci-dessous).

### 2.6 Positionnement

La phrase « To our knowledge, metric learning has not yet been applied to the QUIDA dataset, nor to the fusion of wearable and radar data » est forte. La nuancer (« to the best of our knowledge, based on the literature reviewed in [mois/année] ») et dater la recherche bibliographique : c'est ce qui rend l'affirmation défendable.

### 2.7 Ajouter « Limites et menaces sur la validité » (une demi-page)

Chutes simulées et répétitives, sujets jeunes et en bonne santé, 10 sujets seulement, durée d'enregistrement limitée, scène unique, absence de benchmark publié sur ce corpus. Cette section est attendue dans un état de l'art et prépare la discussion finale du projet.

### 2.8 Figures (le rapport n'en contient aucune)

Trois figures possibles, toutes descriptives (aucun résultat) :
1. le pipeline prévu : fenêtrage → encodeur par capteur → espace d'embedding → classification par prototypes / k-NN ;
2. les trois niveaux de fusion (early / intermediate / late) ;
3. une illustration d'une fenêtre de chute et d'une fenêtre de marche (données publiques du jeu, clairement légendées comme illustration).

---

## 3. Protocole : ce qui doit être écrit noir sur blanc dès maintenant (P0)

Ces points ne sont pas des résultats : ce sont des règles de méthode qui doivent figurer dans le rapport pour qu'il soit évaluable et reproductible.

1. **Règle de fenêtrage complète.** 4 s (2 s avant / 2 s après l'annotation), et pour chaque capteur le nombre d'échantillons attendu (accéléromètre 250 × 3 ; radar ~33 trames, à × le nombre de variables retenues par trame). Le rapport donne déjà ces ordres de grandeur, il manque la règle générale.
2. **Construction des négatifs.** Écrire comment les fenêtres sans chute sont échantillonnées : pas de recouvrement avec une fenêtre de chute, et **une garde minimale** entre une fenêtre négative et toute chute. Sans cette garde, l'immobilité qui suit une chute peut se retrouver étiquetée « non-chute » — c'est le point qu'un jury relèvera en premier.
3. **Ratio des classes.** Annoncer le ratio visé (1:3 comme dans le papier, ou autre) et préciser s'il est appliqué par sujet ou globalement.
4. **Repère temporel.** Dire explicitement si les fenêtres sont centrées sur l'horodatage annoté ou sur un index fourni par le fichier d'annotations. Ce choix déplace l'alignement entre capteurs et doit être écrit.
5. **Normalisation.** Statistiques ajustées sur les seuls sujets d'entraînement (pas de fuite), et variante par sujet ou globale.
6. **Protocole de données réduites.** Le planning demande des sous-ensembles d'entraînement de tailles décroissantes. Deux options à choisir et à écrire : (a) k-shot — k fenêtres étiquetées par classe sur le sujet testé, k ∈ {1, 2, 4, 8} ; (b) pourcentages fixes des fenêtres d'entraînement (100/50/25/10 %). L'option (a) correspond mieux à l'argument « peu d'exemples » et à la littérature few-shot déjà citée.
7. **Baseline sans apprentissage.** Prévoir, dans le même protocole, une baseline simple (statistiques + plus proche prototype) sur les mêmes épisodes : sans elle, on ne peut pas attribuer un gain à la métrique apprise plutôt qu'au classifieur. À annoncer dès le §6.
8. **Incertitude.** Avec 10 sujets, annoncer que les résultats seront donnés par fold (moyenne ± écart-type) et comparés par test apparié, pas seulement en agrégeant toutes les fenêtres.
9. **Augmentation.** La phrase actuelle sur l'absence de fuite est bien vue ; préciser qu'elle ne s'applique qu'aux fenêtres d'entraînement.
10. **Reproductibilité.** Graines aléatoires, versions des bibliothèques, matériel.

---

## 4. Forme et présentation (P2)

1. **Numérotation des tableaux :** le tableau k-NN/prototypes n'a pas de légende ; le tableau de synthèse est numéroté « Table 2 » alors que c'est le troisième. Ajouter une légende (Table 2) au premier, renuméroter le second en Table 3, et corriger l'appel du §6 (« Table 2 summarises the reviewed approaches »).
2. **Coquille :** titre « Comparision » → « Comparison ».
3. **Langue :** mélange britannique/américain — « popularised », « summarised », « recognise », « synchronised » vs « characterize », « normalized », « synchronized ». Choisir une variante (US conseillé) et harmoniser.
4. **Figures :** voir §2.8 ; en l'état, 15 pages sans aucune figure.
5. **Table des matières et numérotation des sections :** le document est assez long pour une table des matières ; vérifier que les sections sont numérotées de façon homogène.
6. **Volume :** 15 pages / 3 996 mots, correct pour le livrable.

---

## 5. Priorités

| Priorité | Action |
|---|---|
| P0 | §2.3 : préciser « après segmentation », le fait que les fenêtres sont à reconstruire, et la règle de reconstruction |
| P0 | §6 : écrire la règle de fenêtrage, la construction des négatifs (avec garde), le ratio, le repère temporel |
| P0 | §6.2 : ajouter la baseline sans apprentissage et le mode de comparaison (par fold, test apparié) |
| P1 | §4.1 : ajouter Wang, Yan & Oates (2016) ; §5 : sourcer la taxonomie de fusion |
| P1 | Ajouter la section « Limites et menaces sur la validité » |
| P1 | Trancher et écrire les choix (distance/normalisation/dimension d'embedding ; CNN vs LSTM par capteur ; k-NN et/ou prototypes) |
| P2 | Tableaux, coquille, langue, figures, table des matières, DOI OSF |

---

## Annexe — À vérifier le jour où vous ferez la préparation des données (à ne pas écrire dans le rapport maintenant)

Liste de contrôle, sans chiffres : ces questions se posent au moment de l'exploration, et leurs réponses pourront alors être ajoutées au rapport (ou à un rapport de préparation séparé).

- Le papier annonce des blocs d'enregistrement de l'accéléromètre de 12 s : vérifier la durée réelle des blocs dans l'archive et le nombre d'échantillons par bloc.
- Vérifier ce que contiennent réellement les fichiers en matière de chutes et de non-chutes (nombre de blocs avec / sans chute) avant de reprendre le ratio 1:3 dans le rapport.
- Vérifier si l'archive contient des fenêtres déjà segmentées ou seulement les enregistrements bruts et le fichier d'annotations ; si les fenêtres doivent être reconstruites, identifier le fichier d'index et mesurer l'écart entre l'index et l'horodatage annoté.
- Mesurer la durée réellement couverte par chaque capteur et par sujet, et surtout la durée de recouvrement entre capteurs : c'est ce qui détermine combien de fenêtres sont exploitables en fusion.
- Documenter les anomalies éventuelles (horodatages incohérents, deux chutes dans une même fenêtre, chute sans fenêtre complète) et la règle de nettoyage appliquée.
