import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd
import Signal as Si
import csv
import datetime as dt
import os
from pathlib import Path
import sys

dossier_racine = Path(__file__).resolve().parents[4]
sys.path.append(str(dossier_racine))

import modulation.algo.qam.QAM_mod as QAM_mod

# freq échantillonage de l'ordinateur
f_ech = 48000  

# texte à moduler et type de modulation
message = input("Donnez le texte à moduler : ")
binaire = ''.join(format(ord(c), '08b') for c in message)
print("Message binaire : ", binaire)

QAM_number = int(input("Donnez la modulation : (chiffre ex : 32)"))


# Ajout du code barker permettant à détecter le début du message
code = QAM_mod.Barker(5)
IQ = QAM_mod.Barker_IQ(code, QAM_number)


# modulation du message avec trame de détection
message_mod, time_stop = Si.Modulation(f_ech, binaire, 5000, QAM_number, 0.5, True, IQ)




nombre_symbol = 0.5 * 48000


zeros_fin = np.zeros(int(3 * nombre_symbol), dtype=message_mod.dtype) # corriger le décalgage de sd.playrec avec un signal d'amplitude nul
message_mod = np.concatenate((message_mod, zeros_fin))


print("Envoi du signal dans la carte son (lecture + enregistrement)...")


# Joue et enregistre le résultat
message_mod_recu = sd.playrec(message_mod, f_ech, channels=1)
sd.wait()
print("Enregistrement terminé.")


# Affichage et enregistrement du signal émis et reçu
limite = len(message_mod) // 100
message_mod_zoom = message_mod[:]


message_mod_recu_zoom = message_mod_recu[:].flatten()


plt.figure(2, figsize=(12, 6))
plt.title(f"Comparaison du Message Modulé (QAM-{QAM_number}) : Émis vs Reçu")


plt.plot(message_mod_zoom/max(message_mod_zoom), label="Signal Émis (Propre)", color="blue", alpha=0.8, linewidth=1.5)


plt.plot(message_mod_recu_zoom/max(message_mod_recu_zoom), label="Signal Reçu (Micro/Ligne)", color="orange", alpha=0.7, linewidth=1.5)
plt.xlabel("Échantillons")
plt.ylabel("Amplitude")


plt.legend(loc="upper right") 

plt.tight_layout()
plt.show()

dossier_actuel = os.path.dirname(os.path.abspath(__file__))


dossier_datasets = os.path.join(dossier_actuel, "datasets")
os.makedirs(dossier_datasets, exist_ok=True)


nom_fichier = str(QAM_number) + "_" + dt.datetime.now().strftime("%d_%H%M")
chemin_base = os.path.join(dossier_datasets, nom_fichier)


with open(
    chemin_base + "_recu.csv", "w", newline="", encoding="utf-8"
) as fichier:
  writer = csv.writer(fichier)
  writer.writerows(message_mod_recu.reshape(-1, 1))

with open(
    chemin_base + "_emis.csv", "w", newline="", encoding="utf-8"
) as fichier:
  writer = csv.writer(fichier)
  writer.writerows(message_mod.reshape(-1, 1))
