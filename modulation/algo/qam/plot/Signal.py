import numpy as np
import sys
from pathlib import Path
import matplotlib.pyplot as plt


dossier_racine = Path(__file__).resolve().parents[4]
sys.path.append(str(dossier_racine))


import modulation.algo.qam.QAM_mod as QAM_mod



def Modulation(f_ech : int, message_bin : str, F_porteuse : float, QAM_number : int, t_symbol : float, display : bool, trame_IQ : list = [])-> list:
    """Module un message binaire en un signal QAM et calcule sa durée totale.

    Découpe le message binaire en symboles, génère les composantes I et Q 
    associées (en ajoutant éventuellement une trame de synchronisation en tête), 
    puis synthétise le signal modulé sur une porteuse à la fréquence d'échantillonnage 
    donnée. Affiche optionnellement le signal continu simulé et le signal échantillonné.

    Args:
        - f_ech (int): Fréquence d'échantillonnage du signal en Hertz (Hz).
        - message_bin (str): Message binaire à moduler (chaîne de '0' et de '1').
        - F_porteuse (float): Fréquence de la porteuse en Hertz (Hz).
        - QAM_number (int): Ordre de la modulation QAM (ex: 4, 16, 64).
        t_symbol (float): Durée d'un symbole en secondes (s).
        display (bool): Si True, affiche les graphiques du signal modulé (continu et échantillonné).
        trame_IQ (list, optional): Coordonnées [I, Q] d'une trame d'en-tête ou de 
            synchronisation à insérer au début du signal. Par défaut à [].

    Returns:
        tuple[np.ndarray, float]: Un tuple contenant :
            - message_mod_ech (np.ndarray): Le signal modulé et échantillonné.
            - time_stop (float): La durée totale estimée du message en secondes (s).
    """

    divide_message, taille = QAM_mod.Divide_qam(message_bin, QAM_number)

    time_start = 0
    time_stop = (taille+1) * t_symbol

    print("------")
    print("La durée du message est de : ", time_stop)
    print("------")

    
    
    
    signal_IQ = []
    if len(trame_IQ[0]) != 0:
        signal_IQ.append(trame_IQ[0])
        signal_IQ.append(trame_IQ[1])


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
        






    


    


