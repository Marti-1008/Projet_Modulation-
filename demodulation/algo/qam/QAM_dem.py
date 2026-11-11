import numpy as np
from scipy import signal
import os
import sounddevice as sd
from scipy.io import wavfile
import sys
from pathlib import Path
import math as m

dossier_racine = Path(__file__).resolve().parents[4]
sys.path.append(str(dossier_racine))


# 3. Importez votre fonction (adaptez le nom du fichier et de la fonction)
# Exemple si la fonction Modulation est dans modulation/algo/qam/plot/Signal.py :
from modulation.algo.qam import QAM_mod as Mod
from modulation.algo.qam.plot import Signal as Si

def enregistrer_audio(nom_fichier, duree=5.0, sample_rate=48000) -> tuple[list[int], list[int]]:
    """
    Enregistre le son du micro et le sauvegarde dans un fichier WAV.
    
    Paramètres:
    - nom_fichier (str) : Le nom ou chemin du fichier de sortie (ex: "audio.wav")
    - duree (float)     : La durée de l'enregistrement en secondes
    - sample_rate (int) : La fréquence d'échantillonnage (44100 par défaut)
    - canaux (int)      : 1 pour Mono, 2 pour Stéréo
    """
    # Configuration des paramètres par défaut de sounddevice
    sd.default.samplerate = sample_rate
    
    print(f"nregistrement démarré ({duree} secondes)...")
    
    # Lancement de l'enregistrement (retourne un tableau NumPy)
    donnees_audio = sd.rec(int(duree * sample_rate), dtype='float32')
    
    # Attente de la fin de l'enregistrement
    sd.wait()
    
    print("Enregistrement terminé.")
    
    # Sauvegarde dans le fichier WAV
    wavfile.write(nom_fichier, sample_rate, donnees_audio)
    print(f"Fichier sauvegardé : {nom_fichier}\n")




def Demodulation(message : str, freq_porteuse : float , t_symbol : float, QAM_number : int, f_ech : float = 48000):
    """
    Démodulation du signal (QAM)
    
    Args : 
        - message (str) : message récupéré depuis le micro
        - freq_porteuse (int) : fréquence de la porteuse du signal
        - t_symbol (float) : durée d'un symbol
        - QAM_number (int): Ordre de modulation QAM (par ex. 16, 32, 64).
        - f_ech (float) : fréquence d'échantillonage par défaut à 48 kHz

    Returns 
        - i_filtre (list[int]) : Composante d'amplitude en phase (axe X)
        - q_filtre (list[int]) : Composante d'amplitude en quadrature (axe Y)
    """

    #t_symbol normalement 0.5

    
    nb_niveaux = int(QAM_number**0.5)

    i = []
    q = []

    for incr in range(len(message)):

        # Le signal qu'on obtient est : I_recu * cos(wt) - Q_recu * sint(wt)
        # I = (I_recu * cos(wt) - Q_recu * sint(wt)) * cos(wt) = I_recu * cos²(wt) - Q_recu * sint(wt) * cos(wt) = I_recu * 0.5 * (1+cos(2wt)) -0.5 * Q_recu * sin(2wt)
        # Q = (I_recu * cos(wt) - Q_recu * sint(wt)) * -sin(wt) = I_recu * cos(wt) * -sin(wt) + Q_recu * sin²(wt) = 0.5 * I_recu * -sin(2x) + 0.5 * Q_recu * (1-cos(2wt))
        t = incr / f_ech

        i.append(message[incr] * np.cos(2 * np.pi * freq_porteuse * t))
        q.append(message[incr] * -np.sin(2 * np.pi * freq_porteuse * t))

    i = np.array(i)
    q = np.array(q)

    

    f_cut = (1 / t_symbol) * 1.5 

    b, a = signal.butter(5, f_cut, btype='low', fs=f_ech)

    # --- Application du filtre ---
    i_filtre = signal.filtfilt(b, a, i)
    q_filtre = signal.filtfilt(b, a, q)

    i_filtre = (i_filtre/abs(max(i_filtre)))*nb_niveaux
    q_filtre = (q_filtre/abs(max(q_filtre)))*nb_niveaux

    return i_filtre, q_filtre

def Associate(QAM_number : int) -> dict[tuple[int, int], str]:
    """Crée un dictionnaire associant chaque paire de coordonnées (I, Q) à son symbole binaire.

    Génère l'ensemble des combinaisons binaires possibles pour une constellation QAM donnée,
    calcule leurs coordonnées spatiales respectives via la fonction `Transform`, et les stocke
    pour permettre le décodage inverse (démapping)

    Args :
        QAM_number (int) : Ordre de modulation QAM (par ex. 16, 32, 64)

    Returns :
        dict[tuple[int, int], str] : Un dictionnaire où chaque clé est un tuple `(I, Q)`
            et chaque valeur est la chaîne binaire correspondante (par ex. « 0110 »)
    """

    associate = {}
    for incr in range(QAM_number):
        bits_str = format(incr, "0"+ m.log2(QAM_number) + "b")
        i, q = Mod.Transform(bits_str, QAM_number)
        associate[i,q] = bits_str
    return associate

def Recuperation(i : list, q : list , QAM_number : int) -> str:
    """A partir des valeurs en phase et en quadrature on récupère les valeurs binaire correspondates

    Args : 
        - I (int) : Composante d'amplitude en phase (axe X)
        - Q (int) : Composante d'amplitude en quadrature (axe Y)
        - QAM_number (int) : Nombre total d'états dans la constellation QAM.
    
    Returns :
        - message (str) : messsage traduis
    """
    associate = Associate(QAM_number)
    i_nom, q_nom = associate.keys()


    for incr in range(len(i)):
        pass
        # Utiliser start_find pour trouver le début et faire une moyenne pour détecter la valeur en phase et en quadrature

def Start_find(message : list, lenght_barker : int , f_ech : float, t_symbol : float , QAM_number : int ):
    """Permet de détecter le début du message de la modulation en utilisant l'alogorithme de Barker. 
    Pour détecter le début une corrélation est utilisée pour détecter l'index pour le quel
    il y a la plus grande ressemblance. Il est nécessaire de définir le nombre de symbole utilisé 
    pour l'algoryhtme de Barker.

    Args : 
        - message (list) : liste du message récupéré pour la modulation
        - lenght_barker (int): taille du code utilisé pour détecter le début de la trame
        - f_ech (float): fréquence d'échatillonage
        - t_symbol (float) : durée d'un symbole
        - QAM_number (int) : type de modulation QAM utilisé
    """

    code = Mod.Barker(lenght_barker)
    IQ = Mod.Barker_IQ(code)



    trame, time_stop = Si.Modulation(f_ech, "", 5000, QAM_number, t_symbol, False, IQ)

    res_corr = signal.correlate(message, trame, mode='valid')
    index = np.argmax(np.abs(res_corr))

    return message[index + len(trame): ]