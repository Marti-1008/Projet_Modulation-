import numpy as np
from scipy import signal


import sounddevice as sd
from scipy.io import wavfile

def enregistrer_audio(nom_fichier, duree=5.0, sample_rate=48000, canaux=2):
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
    sd.default.channels = canaux
    
    print(f"nregistrement démarré ({duree} secondes)...")
    
    # Lancement de l'enregistrement (retourne un tableau NumPy)
    donnees_audio = sd.rec(int(duree * sample_rate), dtype='float32')
    
    # Attente de la fin de l'enregistrement
    sd.wait()
    
    print("Enregistrement terminé.")
    
    # Sauvegarde dans le fichier WAV
    wavfile.write(nom_fichier, sample_rate, donnees_audio)
    print(f"Fichier sauvegardé : {nom_fichier}\n")




def Demodulatiob(message, freq_porteuse, t_symbol):

    #t_symbol normalement 0.5

    for incr in range(len(message)):

        # Le signal qu'on obtient est : I_recu * cos(wt) - Q_recu * sint(wt)
        # I = (I_recu * cos(wt) - Q_recu * sint(wt)) * cos(wt) = I_recu * cos²(wt) - Q_recu * sint(wt) * cos(wt) = I_recu * 0.5 * (1+cos(2wt)) -0.5 * Q_recu * sin(2wt)
        # Q = (I_recu * cos(wt) - Q_recu * sint(wt)) * -sin(wt) = I_recu * cos(wt) * -sin(wt) + Q_recu * sin²(wt) = 0.5 * I_recu * -sin(2x) + 0.5 * Q_recu * (1-cos(2wt))

        f_ech = 48000

        i = message[incr] * np.cos(2 * np.pi * freq_porteuse * t_symbol * incr)
        q = message[incr] * -np.sin(2 * np.pi * freq_porteuse * t_symbol * incr)

        f_cut = (1 / t_symbol) * 0.65 

        b, a = signal.butter(5, f_cut, btype='low', fs=f_ech)

        # --- Application du filtre ---
        i_filtre = signal.filtfilt(b, a, i)
        q_filtre = signal.filtfilt(b, a, q)