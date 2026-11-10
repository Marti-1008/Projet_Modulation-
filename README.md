# Communication acoustique numérique

Projet de Master en ingénierie électronique : transmission de messages binaires par le son entre un haut-parleur et un micro (deux appareils, ou un seul en boucle).

On compare **deux résolutions** sur les **mêmes données** et avec les **mêmes critères chiffrés** :

1. **Algorithmique (`algo`)** : chaîne de traitement du signal.
2. **Réseaux de neurones (`nn`)** : trame, modulation, démodulation et vérification réalisées par des réseaux entraînés (autoencodeur de communication). Si un bloc ne s'y prête pas, on le justifie dans le rapport.

**Modulations testées** : BPSK, QPSK, QAM (16-QAM) et OFDM, ce dernier existant en trois variantes (OFDM-BPSK, OFDM-QPSK, OFDM-QAM). AM et FM sont exclues.

---

## 1. Objectifs et critères

| Niveau | Contenu |
|---|---|
| **Socle** | Message texte court, faible distance, pièce calme |
| **Extension** | Petite image, plusieurs distances |
| **Ambitieux** | Débit élevé malgré bruit et réverbération |

Critères mesurés, identiques pour les deux résolutions :

- **Débit utile** (bit/s) : bits du message / durée totale du signal (préambule, en-tête, CRC inclus).
- **Taux d'erreur binaire (BER)** selon la distance, le bruit, la pièce et le matériel.
- **Fiabilité de la détection du début** du message.
- **Compromis débit / fiabilité**.
- **Qualité de la vérification** : taux de messages corrompus correctement détectés / faux rejets.

---

## 2. Format d'une trame

```
| Préambule (sync) | En-tête (longueur) | Message | CRC |
```

- **Préambule** : séquence connue, détectée pour retrouver le début du message.
- **En-tête** : longueur du message en bits.
- **CRC** (CRC-16 ou CRC-32) : si le CRC reçu ne correspond pas, le message est marqué **invalide**.

La trame existe en deux versions, `algo` (chirp + corrélation) et `nn` (préambule et en-tête appris, détection par réseau). Les constantes communes (longueur du préambule, taille de l'en-tête) sont dans `config.py`.

---

## 3. Structure du dépôt

Le dépôt est organisé par **fonction** : `mod`, `demod`, `verif`, `common`. Dans `mod`, `demod` et `verif`, on retrouve `algo` et `nn`. Chaque modulation (et la trame) a **son dossier**. **Chaque dossier `nn` contient son `dataset/`, son `train.py`, son `model.py` et ses `weights/`.**

```
acoustic-comm/
├── README.md
├── requirements.txt
├── .gitignore
│
├── modulation/                                 # MODULATION (émetteur)
│   ├── algo/
│   │   ├── frame/ (mod_frame.py)
│   │   ├── bpsk/ (mod_bpsk.py)
│   │   ├── qpsk/ (mod_qpsk.py)
│   │   ├── qam/ (mod_qam.py)
│   │   └── ofdm/
│   │       ├── ofdm_core.py             # Code IFFT / CP algorithmique standard
│   │       ├── bpsk/ (mod_ofdm_bpsk.py)
│   │       ├── qpsk/ (mod_ofdm_qpsk.py)
│   │       └── qam/ (mod_ofdm_qam.py)
│   └── nn/                              # Encodeurs neuronaux
│       ├── frame/ (model.py, train.py, dataset/, weights/)
│       ├── bpsk/ (model.py, train.py, dataset/, weights/)
│       ├── qpsk/ (model.py, train.py, dataset/, weights/)
│       ├── qam/ (model.py, train.py, dataset/, weights/)
│       └── ofdm/ 
|           |── bpsk/ (mod_ofdm_bpsk.py, train.py, dataset/, weights/)
│           ├── qpsk/ (mod_ofdm_qpsk.py, train.py, dataset/, weights/)
│           └── qam/ (mod_ofdm_qam.py, train.py, dataset/, weights/)
│
├── demodulation/                               # DÉMODULATION (récepteur)
│   ├── algo/
│   │   ├── frame/ (demod_frame.py, sync.py)
│   │   ├── bpsk/ (demod_bpsk.py)
│   │   ├── qpsk/ (demod_qpsk.py)
│   │   ├── qam/ (demod_qam.py)
│   │   └── ofdm/
│   │       ├── ofdm_core.py             # Code FFT / Égalisation algorithmique standard
│   │       ├── bpsk/ (demod_ofdm_bpsk.py)
│   │       ├── qpsk/ (demod_ofdm_qpsk.py)
│   │       └── qam/ (demod_ofdm_qam.py)
│   └── nn/                              # Décodeurs neuronaux
│       ├── frame/ (model.py, train.py, dataset/, weights/)
│       ├── bpsk/ (model.py, train.py, dataset/, weights/)
│       ├── qpsk/ (model.py, train.py, dataset/, weights/)
│       ├── qam/ (model.py, train.py, dataset/, weights/)
│       └── ofdm/ (model.py, train.py, dataset/, weights/) 
|           |── bpsk/ (mod_ofdm_bpsk.py, train.py, dataset/, weights/)
│           ├── qpsk/ (mod_ofdm_qpsk.py, train.py, dataset/, weights/)
│           └── qam/ (mod_ofdm_qam.py, train.py, dataset/, weights/)
│
├── verification/                               # VÉRIFICATION de l'intégrité du message
│   ├── algo/
│   │   ├── crc.py
│   │   └── hamming.py
│   └── nn/
│       ├── model.py
│       ├── train.py
│       ├── dataset/
│       └── weights/
│
├── common/                              # Tous les outils, configurations et points d'entrée
│   ├── config.py                        # Paramètres globaux (Fe, bande passante, chemins)
│   ├── channel.py                       # Simulation de canal acoustique (Numpy et PyTorch)
│   ├── audio_io.py                      # Accès micro / haut-parleur du PC
│   ├── record_session.py                # Enregistrement des données
│   ├── emitter.py                       # Point d'entrée Émetteur (Message -> .wav)
│   ├── receiver.py                      # Point d'entrée Récepteur (.wav -> Message)
│   └── evaluate.py                      # Outil de benchmark (Compare algo vs NN)
│
├── results/                             # Figures et logs
└── report/                              # Rapport final
```

Il n'y a **pas de dossier `data/` à la racine** : les données vivent dans les dossiers `dataset/` (voir section 4).

### Principe

- **`algo`** : un dossier par modulation (et pour la trame). L'OFDM est un dossier avec un `ofdm_core.py` commun, puis un dossier par modulation (bpsk, qpsk, qam) qui réutilise les mappings correspondants.
- **`nn`** : même découpage. Chaque dossier a son `model.py`, son `train.py`, son `dataset/` et ses `weights/`.
- **Trame** : `modulation/algo/frame` et `demodulation/algo/frame` gèrent préambule chirp, détection par corrélation (`sync.py`), en-tête et CRC. `modulation/nn/frame` et `demodulation/nn/frame` les remplacent par un préambule et un en-tête appris et une détection du début par réseau.
- **Entraînement en deux étapes** (équivalent d'un autoencodeur de communication) :
  1. `modulation/nn/<modulation>/train.py` entraîne l'encodeur avec le décodeur dans la boucle, à travers le canal simulé de `channel.py`. Les poids sont sauvegardés dans `modulation/nn/.../weights/` et `demodulation/nn/.../weights/`.
  2. `demodulation/nn/<modulation>/train.py` ajuste le décodeur (encodeur figé) sur les enregistrements réels de la partie `train`.
- **Équivalence des modulations côté NN** : le nom de la modulation fixe le nombre de bits par symbole (BPSK = 1, QPSK = 2, 16-QAM = 4). Pour l'OFDM, ce même nombre s'applique à chaque sous-porteuse.
- **Vérification** :
  - `verification/algo/crc.py` est la référence : un CRC faux = message invalide.
  - `verification/nn` est un classifieur complémentaire qui estime si un message reçu est fiable. Il est comparé au CRC sur les mêmes données ; si le CRC suffit, on le justifie dans le rapport.
- **`common/`** ne contient que l'accès au matériel et l'enregistrement. À la racine, on garde seulement `config.py`, `channel.py` et les trois points d'entrée.

---

## 4. Données (dossiers `dataset/`)

Chaque dossier `dataset/` contient les données nécessaires à l'entraînement et à l'évaluation des réseaux de neurones. La manière de construire ces datasets dépend de la fonction étudiée.

### 4.1. Construction des datasets

Les datasets sont construits de deux manières distinctes :

- **Modulation (`modulation/nn/`)** : les datasets sont générés à partir des sorties des algorithmes de modulation. Ils permettent de disposer de données de référence pour entraîner les encodeurs neuronaux et comparer leurs résultats aux modulations classiques.

- **Démodulation (`demodulation/nn/`)** : les datasets sont constitués des signaux reçus par le PC (entrées du réseau) et des bits originaux ayant servi à générer les signaux (sorties attendues). Les signaux reçus peuvent provenir de simulations réalisées avec `channel.py` ou d'enregistrements réels effectués avec le haut-parleur et le microphone.

Exemple de structure :

```text
modulation/nn/qpsk/dataset/
├── input.csv
└── output.csv

demodulation/nn/qpsk/dataset/
├── make_dataset.py
├── train/
│   └── 20261110_salleA_1.5m_calme/
│       ├── signal.wav
│       ├── message.bits
│       └── info.yaml
├── val/
└── test/
```


### 4.2. Séparation des données

Les données sont réparties en trois ensembles :

- **Train** : données utilisées pour entraîner les réseaux.
- **Validation** : données utilisées pour ajuster les hyperparamètres et suivre les performances pendant l'entraînement.
- **Test** : données réservées à l'évaluation finale. Elles ne doivent jamais être utilisées pendant l'entraînement ou le réglage des modèles.

La séparation doit être effectuée par session d'enregistrement et non par trame. Cela évite qu'un même enregistrement se retrouve à la fois dans le train et dans le test.

Les deux méthodes (`algo` et `nn`) doivent être évaluées sur les mêmes sessions de test afin de garantir une comparaison équitable.

### 4.3. Gestion des données avec Git

Les datasets pouvant rapidement occuper beaucoup d'espace, il faut distinguer les fichiers à versionner dans Git des fichiers à stocker séparément.

* **Git classique** : scripts de génération et d'entraînement (`train.py`, `model.py`), fichiers de configuration, métadonnées (`info.yaml`) et petits fichiers texte nécessaires au fonctionnement du projet.
* **Git LFS (Large File Storage)** : poids des modèles entraînés (`.pt`, `.pth`) et fichiers audio légers de référence si nécessaire, sous réserve du quota disponible sur votre plateforme.
* **Stockage externe partagé** : pour les datasets volumineux générés localement (fichiers `.npy`, enregistrements bruts). Ces fichiers restent confinés localement dans les dossiers `dataset/` de chaque sous-module NN et sont ignorés par Git.

Les scripts permettant de générer les données ou de charger les datasets doivent être conservés au sein de chaque dossier de modèle afin que chaque membre puisse reconstruire ou recharger les données localement.

Il faut également conserver (via un petit fichier `info.yaml` dans chaque dossier `dataset/`) les métadonnées permettant de retrouver la provenance des données : modulation, distance, pièce, bruit de fond, matériel utilisé et partition (train/val/test).

**Règles importantes :**
* Ne pas committer plusieurs copies inutiles d'un même dataset.
* Ne jamais modifier ou corrompre les données de test pour améliorer artificiellement les résultats de vos réseaux de neurones.
* Ne pas vider ou remplacer un dataset partagé sans prévenir les autres membres.
* Documenter précisément la structure des tenseurs/matrices stockées localement.
* Ne pas committer de fichiers audio ou de poids volumineux directement dans Git classique (utiliser rigoureusement le `.gitignore`).

L'objectif est que chaque membre puisse récupérer le code, réexécuter les scripts de génération et reproduire les expériences à l'identique, sans alourdir le dépôt.

---

## 5. Travail à trois avec Git

### Branches

Le développement est cloisonné par dossier. Nous utilisons une branche dédiée pour chaque **couple complet émetteur/récepteur** (méthode, modulation et sous-type) afin de garantir qu'une chaîne de modulation complète soit fonctionnelle avant d'être intégrée. Les outils partagés résident dans le dossier `common/`.

```text
main                          <- version stable et fonctionnelle (démo, rendu)
 │
 ├── feature/common           (tous les fichiers de common/ : config.py, channel.py, etc.)
 ├── feature/verif            (verification/algo et verification/nn)
 │
 ├── feature/algo-frame       (modulation/algo/frame + demodulation/algo/frame)
 ├── feature/algo-bpsk        (modulation/algo/bpsk + demodulation/algo/bpsk)
 ├── feature/algo-qpsk        ...
 ├── feature/algo-qam
 │
 ├── feature/algo-ofdm-bpsk   (modulation/algo/ofdm/bpsk + demodulation/algo/ofdm/bpsk)
 ├── feature/algo-ofdm-qpsk   ...
 ├── feature/algo-ofdm-qam
 │
 ├── feature/nn-frame         (modulation/nn/frame + demodulation/nn/frame)
 ├── feature/nn-bpsk          (modulation/nn/bpsk + demodulation/nn/bpsk)
 ├── feature/nn-qpsk          ...
 ├── feature/nn-qam
 │
 ├── feature/nn-ofdm-bpsk     (modulation/nn/ofdm/bpsk + demodulation/nn/ofdm/bpsk)
 ├── feature/nn-ofdm-qpsk     ...
 └── feature/nn-ofdm-qam
```

Pas de branche `develop` : on part de `main` et on y revient par Pull Request. Une même personne peut gérer plusieurs branches ; l'important est qu'**un dossier ait un seul propriétaire** à un instant T pour éviter tout conflit de fusion.

### Répartition proposée (à adapter)

| Personne | Branches assignées |
| :--- | :--- |
| **Membre 1** | `common`, `verif`, `algo-frame`, `algo-bpsk`, `algo-qpsk` |
| **Membre 2** | `algo-qam`, `algo-ofdm-bpsk`, `algo-ofdm-qpsk`, `algo-ofdm-qam`, `nn-frame` |
| **Membre 3** | `nn-bpsk`, `nn-qpsk`, `nn-qam`, `nn-ofdm-bpsk`, `nn-ofdm-qpsk`, `nn-ofdm-qam` |

Tout le monde dépend du code transverse dans `common/` (`config.py`, `channel.py`, etc.) : le membre 1 doit donc stabiliser et pousser ce socle en priorité.

### Règles d'or du projet

1. **Pas de push direct sur `main`** : passage obligatoire par une Pull Request relue et validée par au moins un autre membre de l'équipe.
2. **Cloisonnement strict** : chacun travaille exclusivement dans ses dossiers assignés pour éliminer à 100 % les conflits Git.
3. **Fichiers partagés** : les fichiers de `common/` ne sont modifiés qu'après accord unanime. On ne change jamais une signature de fonction existante sans avertir l'équipe.
4. **Synchronisation** : avant de coder, effectuer un `git checkout main && git pull origin main`, puis retourner sur sa branche pour y fusionner les nouveautés via `git merge main`.
5. **Exclusions Git** : interdiction stricte de committer les répertoires `__pycache__/`, `.venv/`, ainsi que les fichiers lourds `.npy` ou `.wav` (configurer correctement le fichier `.gitignore`).
6. **Critère d'acceptation de PR** : valider localement qu'un aller-retour complet émetteur \(\rightarrow\) canal (sans bruit) \(\rightarrow\) récepteur donne un BER (Bit Error Rate) de 0 et un CRC valide.

### Format des Commits

Nous suivons le format standardisé : `type(portée): description` (types autorisés : `feat`, `fix`, `data`, `docs`).

```text
feat(algo-qpsk): implémentation de la décision par distance minimale
feat(nn-qam): architecture de l'émetteur et du récepteur 16-QAM sous PyTorch
fix(algo-frame): ajustement du seuil de corrélation pour la synchronisation
data(nn-bpsk): génération du dataset local sous canal AWGN
```

### Cycle de développement type au terminal

```bash
# 1. Récupérer les dernières mises à jour stables
git checkout main
git pull origin main

# 2. Créer ou rejoindre sa branche dédiée au couple de modulation
git checkout -b feature/algo-ofdm-bpsk

# ... codage dans modulation/algo/ofdm/bpsk/ et demodulation/algo/ofdm/bpsk/ ...

# 3. Committer proprement son avancement
git add modulation/algo/ofdm/bpsk/ demodulation/algo/ofdm/bpsk/
git commit -m "feat(algo-ofdm-bpsk): écriture de la chaîne IFFT et FFT"

# 4. Réintégrer le travail récent des autres avant de soumettre
git fetch origin
git merge origin/main

# 5. Pousser sur le dépôt distant et ouvrir la Pull Request
git push -u origin feature/algo-ofdm-bpsk
```

## 🛠️ Méthodologie de développement d'un couple modulation/Demod

Développer par "couple" signifie qu'une seule branche prend en charge à la fois la génération du signal (`modulation/`) et son décodage (`demodulation/`). Cette approche évite les désynchronisations de formats de données entre l'émetteur et le récepteur.

Chaque module doit valider le cycle d'analyse suivant localement avant toute proposition de fusion :
1. **Génération de la Source** : Création d'un vecteur de bits aléatoires (0 et 1).
2. **Modulateur (`modulation/`)** : Conversion des bits en symboles, puis modulation sur porteuse (fréquences définies dans `common/config.py`).
3. **Canal Acoustique (`common/channel.py`)** : Passage du signal dans le simulateur. Pour les premiers tests de validation, le canal est configuré en mode idéal (sans bruit, sans écho).
4. **Démodulateur (`demodulation/`)** : Réception du signal, démodulation (multiplication porteuse, filtrage passe-bas) et prise de décision pour restituer les bits estimés.
5. **Calcul de performance** : Comparaison stricte des bits de sortie avec les bits d'entrée. Le code est considéré comme prêt pour la Pull Request lorsque le BER atteint strictement **0** sur un canal idéal.

---

### Jalons de livraison

1. **Socle & Outils Communs** : Fichiers du dossier `common/` opérationnels (entrées/sorties audio, simulateur de canal) + chaîne `algo-frame` (préambule chirp + CRC).
2. **Modulations de base (Algorithmique)** : Chaînes complètes BPSK, QPSK et QAM. Calculs et comparaisons du BER et du débit.
3. **OFDM (Algorithmique)** : Implémentation des variantes OFDM-BPSK, QPSK et QAM avec insertion de pilotes et traitement multi-trajet.
4. **Modèles Neuronaux (NN)** : Entraînement et validation des modèles pour la trame apprise, les modulations simples et les variantes OFDM.
5. **Rendu Final** : Exécution globale via `evaluate.py` sur un jeu de test acoustique commun congelé, rapport final et démonstration live.
---

## 6. Expériences

Pour chaque modulation (mono-porteuse et OFDM), on fait varier la **distance**, le **bruit ambiant**, la **pièce**, le **matériel** et le **débit symbole**, avec plusieurs répétitions. On mesure BER, débit utile, taux de détection du début, taux de CRC valides et qualité de la vérification, pour la version `algo` **et** la version `nn`.

---
## 7. Format des données (CSV)

Le fichier CSV généré contient deux parties distinctes : un **en-tête de métadonnées** (lignes commentées avec `#`) suivi des **données temporelles du signal**.

### Structure du fichier

```csv
# Type de modulation: QAM32
# Date de generation: 2026-11-07 14:15:13
# Message original: Bonjour
# Frequence echantillonnage (fe): 1000 Hz
# Frequence porteuse (freq): 10 Hz
# ----------------------------------------
Temps(s),Amplitude_s(t)
0.0,-1.0
0.001,-0.809655
```

### Description des champs

| Élément | Description |
| :--- | :--- |
| **Type de modulation** | Type de modulation d'amplitude en quadrature utilisé (ex: QAM32). |
| **Date de generation** | Horodatage précis de la création du fichier (AAAA-MM-JJ HH:MM:SS). |
| **Message original** | Le texte source qui a été encodé et modulé. |
| **Fréquence échantillonnage (fe)** | Fréquence à laquelle le signal a été numérisé (en Hz). |
| **Fréquence porteuse (freq)** | Fréquence de l'onde porteuse utilisée pour la modulation (en Hz). |
| **Temps(s)** | Première colonne de données : l'axe du temps en secondes. |
| **Amplitude_s(t)** | Deuxième colonne de données : la valeur de l'amplitude du signal modulé à l'instant *t*. |

---

## 8. Équipe

| Nom | Rôle |
|---|---|
| Martin Mineur | _à compléter_ |
| Noé Antoine | _à compléter_ |
| théo Demarche | _à compléter_ |
