import numpy as np
from scipy import signal
import os
import sounddevice as sd
from scipy.io import wavfile
import sys
from pathlib import Path
import math as m
import csv

dossier_racine = Path(__file__).resolve().parents[3]
sys.path.append(str(dossier_racine))



from modulation.algo.qam import QAM_mod as Mod
from modulation.algo.qam.plot import Signal as Si

FREQ_PORTEUSE = 10000   # Fréquence de la porteuse (Hz)

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

    
    nb_niveaux = int(QAM_number**0.5) -1

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

    print("Valeur de I après multiplication avec cos", i[:20])
    print("Valeur de Q après multiplication avec -sin", q[:20])


    
    

    f_cut = (1 / t_symbol) * 5

    sos = signal.butter(5, f_cut, btype="low", fs=f_ech, output="sos")

    # --- Application du filtre stable (SOS) ---
    i_filtre = signal.sosfiltfilt(sos, i)
    q_filtre = signal.sosfiltfilt(sos, q)

    max_i = np.max(np.abs(i_filtre))
    max_q = np.max(np.abs(q_filtre))

    i_filtre = (i_filtre / max_i) * nb_niveaux if max_i > 0 else np.zeros_like(i_filtre)
    q_filtre = (q_filtre / max_q) * nb_niveaux if max_q > 0 else np.zeros_like(q_filtre)

    print("NaN dans i avant filtre :", np.isnan(i).sum(), "| NaN dans i_filtre après filtre :", np.isnan(i_filtre).sum())
    print("Max abs i_filtre :", np.max(np.abs(i_filtre)), "| Max abs q_filtre :", np.max(np.abs(q_filtre)))

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
        bits_str = format(incr, "0"+ str(int(m.log2(QAM_number))) + "b")
        i, q = Mod.Transform(bits_str, QAM_number)
        associate[i,q] = bits_str
    return associate

def Recuperation(i : list, q : list , QAM_number : int, f_ech : float, t_symbol : float, duree_message : float ) -> str:
    """A partir des valeurs en phase et en quadrature on récupère les valeurs binaire correspondates du signal contenant les données.
    Ce signal ne doit plus contenir la trame de début et de fin. 

    Args : 
        - I (int) : Composante d'amplitude en phase (axe X)
        - Q (int) : Composante d'amplitude en quadrature (axe Y)
        - QAM_number (int) : Nombre total d'états dans la constellation QAM
        - f_ech (float): fréquence d'échatillonage
        - t_symbol (float) : durée d'un symbole
        - duree_message (float) : durée du message
    
    Returns :
        - message (str) : messsage traduis
    """
    associate = Associate(QAM_number)
    
    print( "valeur de la QAM", associate)
    

    taille_message = duree_message/t_symbol

    i_mean = []
    q_mean = []

    ech_par_symbole = int(t_symbol * f_ech)
    marge = int(ech_par_symbole * 0.1)

    for incr in range(int(taille_message)):
        debut = incr * ech_par_symbole + marge
        fin = (incr + 1) * ech_par_symbole - marge
        print("Partie de message I : ", incr, i[debut:fin])
        print("Partie de message Q : ", incr, i[debut:fin])
        i_mean.append(mean(i[debut:fin]))
        q_mean.append(mean(q[debut:fin]))



    i_mean = delete_zero(i_mean)
    q_mean = delete_zero(q_mean)
    # for incr in range(len(i_mean)):
    #     print("I moyen: ", find_key(associate,i_mean[incr]))
    #     print("Q moyen: ", find_key(associate,q_mean[incr]))


    message = ""
    for incr in range(len(i_mean)):
        message= message + associate[find_key(associate,i_mean[incr]), find_key(associate,q_mean[incr])]

    return message


def find_key(associate, value: float) -> int:
# Extrait toutes les valeurs des tuples (I, Q) sans doublons et les trie 
    niveaux = sorted({val for cle in associate.keys() for val in cle})
    # On parcourt jusqu'à l'avant-dernier élément (len - 1)
    for i in range(len(niveaux) - 1):
        milieu = (niveaux[i+1] + niveaux[i]) / 2
        if value < milieu:
            return niveaux[i]
            
    # Si la valeur est au-dessus de tous les milieux, c'est forcément le dernier niveau (3)
    return niveaux[-1]



def delete_zero(message: list, seuil: float = 0.1):
    """
    Supprime les valeurs dont la valeur absolue
    est inférieure au seuil.
    """
    return [val for val in message if abs(val) > seuil]


def mean(value : list) -> float :
    result = 0
    print(value)
    print("data : ", len(value))
    for i in range(len(value)):
        result = result + value[i]

    return result/len(value)
       

def Start_find(message : list, lenght_barker : int , f_ech : float, t_symbol : float , QAM_number : int, freq_porteuse : float = FREQ_PORTEUSE ):
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
        - freq_porteuse (float) : fréquence de la porteuse du signal
    """

    code = Mod.Barker(lenght_barker)
    IQ = Mod.Barker_IQ(code, QAM_number)

    

    trame, time_stop = Si.Modulation(f_ech, "", freq_porteuse, QAM_number, t_symbol, False, IQ)

    res_corr = signal.correlate(message, trame, mode='valid')
    index = np.argmax(np.abs(res_corr))

    return message[index + len(trame): ]



def read_csv(): 
    data = []
    with open("demodulation/algo/qam/16_24_2021_emis.csv", mode="r", encoding="utf-8", newline="") as f:
        lecteur = csv.reader(f, delimiter=",")
        for ligne in lecteur:
            data.append(ligne)
        return data
    return 0
            

data = read_csv()


# 1. Conversion des données lues depuis le CSV (chaînes de caractères -> nombres flottants)
# Si chaque ligne contient une seule valeur d'amplitude :
signal_recu = np.array([float(ligne[0]) for ligne in data if ligne])

# (Alternative si toutes les valeurs sont sur une seule ligne dans le CSV) :
# signal_recu = np.array([float(val) for val in data[0] if val])

# 2. Définition des paramètres de la transmission (à ajuster selon votre émission)
F_ECH = 48000          # Fréquence d'échantillonnage (Hz)
T_SYMBOL = 0.1         # Durée d'un symbole (secondes)
QAM_NUMBER = 16        # Ordre de modulation QAM (ex: 16, 32, 64)
LENGTH_BARKER = 5     # Longueur du code de Barker utilisé à l'émission
DUREE_MESSAGE = len(data)*1/F_ECH # Durée du message
print(DUREE_MESSAGE)
# 3. Détection du début de la trame (suppression de l'en-tête Barker)
signal_utile = Start_find(
    message=signal_recu,
    lenght_barker=LENGTH_BARKER,
    f_ech=F_ECH,
    t_symbol=T_SYMBOL,
    QAM_number=QAM_NUMBER,
    freq_porteuse=FREQ_PORTEUSE
)

print("Nombre d'échantillons :", len(signal_utile))
print("Début du signal utile :", signal_utile[:20])


# 4. Démodulation QAM (extraction et filtrage des composantes I et Q)
i_filtre, q_filtre = Demodulation(
    message=signal_utile,
    freq_porteuse=FREQ_PORTEUSE,
    t_symbol=T_SYMBOL,
    QAM_number=QAM_NUMBER,
    f_ech=F_ECH
)


print("Nombre d'échantillons :", len(i_filtre))
print("Début du signal I :", i_filtre[:20])


print("Nombre d'échantillons :", len(q_filtre))
print("Début du signal Q :", q_filtre[:20])

# 5. Récupération de la séquence binaire
message_binaire = Recuperation(
    i=i_filtre,
    q=q_filtre,
    QAM_number=QAM_NUMBER,
    f_ech=F_ECH,
    t_symbol=T_SYMBOL,
    duree_message=len(signal_utile)* 1/F_ECH
)

print("Message binaire démodulé :", message_binaire)

blocs = [message_binaire[i : i + 8] for i in range(0, len(message_binaire), 8)]
texte = "".join(chr(int(bloc, 2)) for bloc in blocs if len(bloc) == 8)

print("Message binaire démodulé :", texte)
print("Nombre de bits :", len(message_binaire))

print("durée : ", DUREE_MESSAGE)
print("débit : ",len(message_binaire)/DUREE_MESSAGE)