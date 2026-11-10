import math as m
import numpy as np


def Divide_qam(message : str, QAM_number : int):
    """
Splits a binary string into blocks based on the QAM constellation size.

Args:
    message (str): Input binary string (e.g., "011010").
    QAM_number (int): Modulation order (e.g., 16, 32, 64).

Returns:
    tuple[list[str], int]: A list of binary symbol blocks and the total symbol count.

    """
    message_split = []
    nb_bits = int(m.log2(QAM_number))
    
    # --- AJOUT DU BOURRAGE (PADDING) ---
    reste = len(message) % nb_bits
    if reste != 0:
        nb_zeros_a_ajouter = nb_bits - reste
        message = message + ('0' * nb_zeros_a_ajouter)
    
    # Maintenant que la chaîne est propre, calcul du nombre réel de symboles
    nb_symboles = len(message) // nb_bits 
    
    for i in range(nb_symboles):
        début = i * nb_bits
        fin = début + nb_bits
        message_split.append(message[début:fin])
        
    return message_split, len(message_split)




def Transform(message, QAM_number):
    """
Maps a binary string to its [I, Q] coordinates using Gray coding.

Handles square constellations natively and non-square cross-shaped 
constellations via Broadcom geometric folding.

Args:
    message (str): Binary block representing one symbol (e.g., "01101").
    QAM_number (int): Total number of states in the QAM constellation.

Returns:
    list[int]: Spatial coordinates as a 2-element list [I, Q].
    """
    # =========================================================================
    # Square constellation
    if m.sqrt(QAM_number).is_integer():
        print("carré")
        nb_niveaux = int(QAM_number**0.5)
        nb_bits_axe = int(m.log2(nb_niveaux))
        
        # Découpe des bits
        bi = int(message[0:nb_bits_axe], 2)
        bq = int(message[nb_bits_axe:], 2)
        
        # Gray code
        gi = bi ^ (bi >> 1)
        gq = bq ^ (bq >> 1)

       
        i = 2 * gi - (nb_niveaux - 1)
        q = 2 * gq - (nb_niveaux - 1)
        
        return [i, q]  # Return [Axe_X, Axe_Y]

    # =========================================================================
    # Cross-shaped constellation
    else:
        # Récupération des dimensions optimales (largeur est toujours la plus grande)
        largeur, longeur = Determine_length(QAM_number)
        print("matrice de :", largeur, longeur)

        # Découpe des bits basée sur les dimensions logiques
        nb_bits_i = int(m.log2(largeur))
        bi = int(message[0:nb_bits_i], 2)
        bq = int(message[nb_bits_i:], 2)
        
        # Encodage de Gray
        gi = bi ^ (bi >> 1)
        gq = bq ^ (bq >> 1)

        # Coordonnées sur la grille rectangulaire initiale (ex: 8x4 pour la 32-QAM)
        rcti = 2 * gi - (largeur - 1)   # Axe horizontal (X)
        rctq = 2 * gq - (longeur - 1)   # Axe vertical (Y)

        # SEUIL STRICT : On ne cible QUE la dernière colonne extérieure qui dépasse
        seuil_i = largeur - 2           # Pour 32-QAM : 8 - 2 = 6
        
        if abs(rcti) > seuil_i:         # Cible uniquement abs(rcti) == 7
            sign_i = 1 if rcti > 0 else -1
            sign_q = 1 if rctq > 0 else -1
            
            # Nouvelle hauteur : pousse les points sur les extensions hautes/basses
            q_cross = sign_q * (longeur + 1)  # Pour 32-QAM : longeur 4 + 1 = ±5
            
            # Détermination de la position sur l'aile
            idx_aile = (abs(rcti) - (largeur - 1)) // 2  
            nb_points_aile = longeur // 2  # Nombre de points par aile (ex: 2)
            
            # Inversion sélective de l'ordre pour respecter le Code de Gray
            if abs(rctq) == (longeur - 1):  # Lignes extérieures (ex: ±3) -> vont à l'intérieur
                i_cross = sign_i * (1 + 2 * (nb_points_aile - 1 - idx_aile))
            else:                           # Lignes intérieures (ex: ±1) -> vont à l'extérieur
                i_cross = sign_i * (1 + 2 * idx_aile)
        else:
            # Zone centrale : les points restent à leur place
            i_cross = rcti
            q_cross = rctq
                
        return [i_cross, q_cross]  # Renvoie [Axe_X, Axe_Y]


def Determine_length(n : int) -> tuple[int, int]:
    """
Finds the two closest divisors of n to form the most compact rectangle.

Args:
    n (int): The number to factorize (e.g., QAM modulation order like 32).

Returns:
    tuple[int, int]: A tuple containing (largeur, hauteur) where largeur >= hauteur.
"""
    for i in range(m.isqrt(n), 0, -1):
        if n % i == 0:
            largeur = n // i
            hauteur = i
            return largeur, hauteur



def Phase(I, Q):
    # Gestion du cas particulier où I vaut 0 pour éviter la division par zéro
    if I == 0:
        return m.pi / 2 if Q > 0 else -m.pi / 2
        
    # Calcul de base de l'angle
    angle = m.atan(Q / I)
    
    # Correction selon le quadrant (si I < 0, on est à gauche de l'axe)
    if I < 0:
        angle += m.pi
    elif I > 0 and Q < 0:
        angle += 2 * m.pi # Optionnel : pour garder l'angle positif entre 0 et 2*pi
        
    return angle


def Amplitude(I, Q):
    return(m.sqrt(I**2+Q**2))

def Signal(I, Q, freq, t):
    """Generates the QAM modulated time-domain wave for a single symbol.

Args:
    I (float): In-phase amplitude component (X-axis).
    Q (float): Quadrature amplitude component (Y-axis).
    freq (float): Carrier frequency in Hz.
    t (np.ndarray): Time vector array generated with NumPy.

Returns:
    np.ndarray: Combined modulated signal waveform array.
    """
    # CORRECTION : On utilise np.cos et np.sin à la place de m.cos et m.sin 
    # pour pouvoir calculer tout le tableau d'un coup
    signal_I = I * np.cos(2 * np.pi * freq * t)
    signal_Q = Q * np.sin(2 * np.pi * freq * t)
    
    return signal_I - signal_Q

