import csv
import datetime as dt
import os
from pathlib import Path
import sys
import matplotlib.pyplot as plt
import numpy as np
import sounddevice as sd
import Signal as Si

dossier_racine = Path(__file__).resolve().parents[4]
sys.path.append(str(dossier_racine))

import modulation.algo.qam.QAM_mod as QAM_mod

# ==============================================================================
# PARAMÈTRES GLOBAUX DE TRANSMISSION (à modifier ici en une seule fois)
# ==============================================================================
F_ECH = 48000                 # Fréquence d'échantillonnage (Hz)
FREQ_PORTEUSE = 10000         # Fréquence de la porteuse (Hz)
QAM_NUMBER = 16               # Ordre QAM (ex. 4, 16, 64)
T_SYMBOL = 0.1                # Durée d'un symbole en secondes (ex. 0.5 ou 0.001)
BARKER_LEN = 5                # Longueur du code de Barker
TRAME_DETECTION = True        # Activation de la trame de détection dans Si.Modulation
NB_SYMBOLES_SILENCE_FIN = 3   # Nombre de périodes symbole de zéros ajoutés à la fin
CANAUX_ENTREE = 1             # Nombre de canaux d'enregistrement
AFFICHER_GRAPHIQUE = True     # Afficher ou non la figure matplotlib
DOSSIER_SORTIE = "datasets"   # Sous-dossier pour les fichiers CSV
# ==============================================================================

# Saisie du texte à moduler
message = input("Donnez le texte à moduler : ")
binaire = "".join(format(ord(c), "08b") for c in message)
print("Message binaire : ", binaire)

# Préambule de Barker
code = QAM_mod.Barker(BARKER_LEN)
IQ = QAM_mod.Barker_IQ(code, QAM_NUMBER)

# Modulation du message avec trame de détection
message_mod, time_stop = Si.Modulation(
    F_ECH,
    binaire,
    FREQ_PORTEUSE,
    QAM_NUMBER,
    T_SYMBOL,
    TRAME_DETECTION,
    IQ,
)

# Ajout de zéros en fin de trame calculés à partir de F_ECH et T_SYMBOL
ech_par_symbole = int(round(T_SYMBOL * F_ECH))
zeros_fin = np.zeros(int(NB_SYMBOLES_SILENCE_FIN * ech_par_symbole), dtype=message_mod.dtype)
message_mod = np.concatenate((message_mod, zeros_fin))

print("Envoi du signal dans la carte son (lecture + enregistrement)...")

# Joue et enregistre le résultat
message_mod_recu = sd.playrec(message_mod, F_ECH, channels=CANAUX_ENTREE)
sd.wait()
print("Enregistrement terminé.")

# Préparation des signaux pour affichage et sauvegarde
message_mod_zoom = message_mod[:]
message_mod_recu_zoom = message_mod_recu[:].flatten()

if AFFICHER_GRAPHIQUE:
    max_emis = np.max(np.abs(message_mod_zoom))
    max_recu = np.max(np.abs(message_mod_recu_zoom))

    plt.figure(2, figsize=(12, 6))
    plt.title(f"Comparaison du Message Modulé (QAM-{QAM_NUMBER}) : Émis vs Reçu")
    plt.plot(
        message_mod_zoom / max_emis if max_emis > 0 else message_mod_zoom,
        label="Signal Émis (Propre)",
        color="blue",
        alpha=0.8,
        linewidth=1.5,
    )
    plt.plot(
        message_mod_recu_zoom / max_recu if max_recu > 0 else message_mod_recu_zoom,
        label="Signal Reçu (Micro/Ligne)",
        color="orange",
        alpha=0.7,
        linewidth=1.5,
    )
    plt.xlabel("Échantillons")
    plt.ylabel("Amplitude")
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.show()

# Sauvegarde des CSV
dossier_actuel = os.path.dirname(os.path.abspath(__file__))
dossier_datasets = os.path.join(dossier_actuel, DOSSIER_SORTIE)
os.makedirs(dossier_datasets, exist_ok=True)

nom_fichier = f"{QAM_NUMBER}_{dt.datetime.now().strftime('%d_%H%M')}"
chemin_base = os.path.join(dossier_datasets, nom_fichier)

with open(chemin_base + "_recu.csv", "w", newline="", encoding="utf-8") as fichier:
    writer = csv.writer(fichier)
    writer.writerows(message_mod_recu.reshape(-1, 1))

with open(chemin_base + "_emis.csv", "w", newline="", encoding="utf-8") as fichier:
    writer = csv.writer(fichier)
    writer.writerows(message_mod.reshape(-1, 1))

print(f"Fichiers enregistrés sous : {chemin_base}_emis.csv et _recu.csv")