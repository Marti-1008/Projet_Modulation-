import numpy as np
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import sounddevice as sd


dossier_racine = Path(__file__).resolve().parents[4]
sys.path.append(str(dossier_racine))


import modulation.algo.qam.QAM_mod as QAM_mod


f_ech = 48000 


def Modulation(f_ech : int, message_bin : str, F_porteuse : float, QAM_number : int, t_symbol : float, display : bool)-> list:
    """
    Modulation du signal avec la QAM retourne le signal Modulé
    f_ech = fréquence d'échantillonage
    message_bin : c'est le message bianire
    F_porteuse : c'est la fréquence de la porteuse
    QAM_numver : c'est le numéro de la QAM
    t_symbol : c'est la durée d'un symbole
    display : c'est un bool qui permet l'affichage des graphes 
    """

    divide_message, taille = QAM_mod.Divide_qam(message_bin, QAM_number)

    time_start = 0
    time_stop = (taille+1) * t_symbol

    print("------")
    print("La durée du message est de : ", time_stop)
    print("------")

    
    
    
    signal_IQ = []
    for i in divide_message:
        signal_IQ.append(QAM_mod.Transform(i, QAM_number))

    
    message_mod = []
    for i in range(taille):
        pas_time = 1000
        precision = np.linspace(0 + i*t_symbol, t_symbol * (i + 1), pas_time)
        message_mod.append(QAM_mod.Signal(signal_IQ[i][0],signal_IQ[i][1],F_porteuse, precision))

    message_mod = np.concatenate(message_mod)
    if display:
        plt.figure(1)
        plt.title("Message Modulé")
        time =  np.arange(len(message_mod)) * pas_time
        plt.plot(time, message_mod)
        plt.show()

    message_mod_ech = []
    for i in range(taille):
        precision = np.arange(i * t_symbol, t_symbol * (i + 1), 1 / f_ech)
        message_mod_ech.append(QAM_mod.Signal(signal_IQ[i][0],signal_IQ[i][1],F_porteuse, precision))


    message_mod_ech = np.concatenate(message_mod_ech)
    print(message_mod_ech)
    if display:
        plt.figure(2)
        plt.title("Message Modulé")
        time =  np.arange(len(message_mod_ech)) * 1/f_ech
        plt.plot(time, message_mod_ech)
        plt.show()

    return message_mod_ech, time_stop
        






    


    


