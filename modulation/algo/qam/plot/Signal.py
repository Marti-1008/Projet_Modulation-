import numpy as np
import sys
from pathlib import Path
import matplotlib.pyplot as plt

dossier_racine = Path(__file__).resolve().parents[4]
sys.path.append(str(dossier_racine))

import modulation.algo.qam.QAM_mod as QAM_mod


def Modulation(
    f_ech: int,
    message_bin: str,
    F_porteuse: float,
    QAM_number: int,
    t_symbol: float,
    display: bool,
    trame_IQ: list[list[int]] | list = [],
) -> tuple[np.ndarray, float]:
    """Module un message binaire en un signal QAM et calcule sa durée totale.

    Découpe le message binaire en symboles, génère les composantes I et Q
    associées (en ajoutant éventuellement une trame de synchronisation en tête),
    puis synthétise le signal modulé sur une porteuse à la fréquence d'échantillonnage
    donnée. Affiche optionnellement le signal continu simulé et le signal échantillonné.

    Args:
        f_ech (int): Fréquence d'échantillonnage du signal en Hertz (Hz).
        message_bin (str): Message binaire à moduler (chaîne de '0' et de '1').
        F_porteuse (float): Fréquence de la porteuse en Hertz (Hz).
        QAM_number (int): Ordre de la modulation QAM (ex: 4, 16, 64).
        t_symbol (float): Durée d'un symbole en secondes (s).
        display (bool): Si True, affiche les graphiques du signal modulé (continu et échantillonné).
        trame_IQ (list, optional): Coordonnées [I, Q] d'une trame d'en-tête ou de
            synchronisation à insérer au début du signal. Par défaut à [].

    Returns:
        tuple[np.ndarray, float]: Un tuple contenant :
            - message_mod_ech (np.ndarray): Le signal modulé et échantillonné.
            - time_stop (float): La durée totale estimée du message en secondes (s).
    """
    # 1. Découpage du message binaire en symboles
    divide_message, _ = QAM_mod.Divide_qam(message_bin, QAM_number)

    # 2. Construction de la liste des symboles [I, Q] : préambule Barker puis message
    signal_IQ: list[list[int]] = []
    if trame_IQ and len(trame_IQ) == 2 and len(trame_IQ[0]) > 0:
        for i_val, q_val in zip(trame_IQ[0], trame_IQ[1]):
            signal_IQ.append([i_val, q_val])

    for i in divide_message:
        signal_IQ.append(QAM_mod.Transform(i, QAM_number))

    nb_symboles = len(signal_IQ)
    time_stop = nb_symboles * t_symbol

    print("------")
    print("Nombre total de symboles (Barker + message) :", nb_symboles)
    print("La durée du message est de : ", time_stop)
    print("------")

    # 3. Signal continu simulé
    pas_time = 1000
    message_mod = []
    for i in range(nb_symboles):
        precision = np.linspace(i * t_symbol, (i + 1) * t_symbol, pas_time)
        message_mod.append(
            QAM_mod.Signal(signal_IQ[i][0], signal_IQ[i][1], F_porteuse, precision)
        )

    message_mod = np.concatenate(message_mod) if message_mod else np.array([])

    if display and len(message_mod) > 0:
        plt.figure(1)
        plt.title("Message Modulé (continu simulé)")
        time = np.linspace(0, time_stop, len(message_mod))
        plt.plot(time, message_mod)
        plt.xlabel("Temps (s)")
        plt.show()

    # 4. Signal échantillonné à f_ech
    message_mod_ech = []
    for i in range(nb_symboles):
        precision = np.arange(i * t_symbol, (i + 1) * t_symbol, 1 / f_ech)
        message_mod_ech.append(
            QAM_mod.Signal(signal_IQ[i][0], signal_IQ[i][1], F_porteuse, precision)
        )

    message_mod_ech = np.concatenate(message_mod_ech) if message_mod_ech else np.array([])
    print(message_mod_ech)

    if display and len(message_mod_ech) > 0:
        plt.figure(2)
        plt.title("Message Modulé (échantillonné)")
        time = np.arange(len(message_mod_ech)) / f_ech
        plt.plot(time, message_mod_ech)
        plt.xlabel("Temps (s)")
        plt.show()

    return message_mod_ech, time_stop