import math as m
import numpy as np

def Divide_qam(message : str, QAM_number : int) -> tuple[list[str], int]:
    """Divise une chaîne binaire en blocs en fonction de la taille de la constellation QAM.

    Args :
        message (str) : Chaîne binaire en entrée (par ex. « 011010 »).
        QAM_number (int) : Ordre de modulation (par ex. 16, 32, 64).

    Returns :
        tuple[list[str], int] : Une liste de blocs de symboles binaires et le nombre total de symboles.
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


def Transform(message : str, QAM_number : int) -> tuple[list, list]:
    """Associe une chaîne binaire à ses coordonnées [I, Q] en utilisant le codage de Gray

    Prend en charge nativement les constellations carrées, ainsi que les constellations
    en croix non carrées grâce à la technique de repliement géométrique (« geometric folding ») de Broadcom

    Args :
        message (str) : Bloc binaire représentant un symbole (par ex. « 01101 »)
        QAM_number (int) : Nombre total d'états dans la constellation QAM

    Returns :
        list[int] : Coordonnées spatiales sous la forme d'une liste à deux éléments [I, Q]
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
        seuil_i = largeur - 2  # Pour 32-QAM : 8 - 2 = 6

        if abs(rcti) > seuil_i:  # Cible uniquement abs(rcti) == 7
            sign_i = 1 if rcti > 0 else -1
            sign_q = 1 if rctq > 0 else -1

            # Nouvelle hauteur : pousse les points sur les extensions hautes/basses
            q_cross = sign_q * (longeur + 1)  # Pour 32-QAM : longeur 4 + 1 = ±5

            # Détermination de la position sur l'aile
            idx_aile = (abs(rcti) - (largeur - 1)) // 2
            nb_points_aile = longeur // 2  # Nombre de points par aile (ex: 2)

            # Inversion sélective de l'ordre pour respecter le Code de Gray
            if abs(rctq) == (longeur - 1):
                # Lignes extérieures (ex: ±3) -> vont à l'intérieur
                i_cross = sign_i * (1 + 2 * (nb_points_aile - 1 - idx_aile))
            else:
                # Lignes intérieures (ex: ±1) -> vont à l'extérieur
                i_cross = sign_i * (1 + 2 * idx_aile)
        else:
            # Zone centrale : les points restent à leur place
            i_cross = rcti
            q_cross = rctq

        return [i_cross, q_cross]  # Renvoie [Axe_X, Axe_Y]


def Determine_length(n : int) -> tuple[int, int]:
    """Trouve les deux diviseurs les plus proches de n pour former le rectangle le plus compact.

    Args :
        n (int) : Le nombre à factoriser (par ex., l'ordre de modulation QAM comme 32).

    Returns :
        tuple[int, int] : Un tuple contenant (largeur, hauteur) où largeur >= hauteur.
    """
    for i in range(m.isqrt(n), 0, -1):
        if n % i == 0:
            largeur = n // i
            hauteur = i
            return largeur, hauteur


def Phase(I : int, Q : int) -> float:
    """Calcule la phase (l'angle en radians) d'un point de la constellation.

    Args :
        I (int | float) : Composante en phase (axe X).
        Q (int | float) : Composante en quadrature (axe Y).

    Returns :
        float : L'angle de phase en radians (entre 0 et 2*pi ou -pi/2).
    """
    # Gestion du cas particulier où I vaut 0 pour éviter la division par zéro
    if I == 0:
        return m.pi / 2 if Q > 0 else -m.pi / 2

    # Calcul de base de l'angle
    angle = m.atan(Q / I)

    # Correction selon le quadrant (si I < 0, on est à gauche de l'axe)
    if I < 0:
        angle += m.pi
    elif I > 0 and Q < 0:
        angle += 2 * m.pi  # Optionnel : pour garder l'angle positif entre 0 et 2*pi

    return angle


def Amplitude(I : int, Q : int ) -> float:
    """Définit l'amplitude du signal à partir de ses coordonnées I et Q.

    Args :
        I (int) : Composante d'amplitude en phase (axe X).
        Q (int) : Composante d'amplitude en quadrature (axe Y).

    Returns :
        float : L'amplitude du point dans la constellation.
    """
    return(m.sqrt(I**2+Q**2))


def Signal(I : int, Q : int , freq : float, t : float) -> list:
    """Génère l'onde modulée en QAM dans le domaine temporel pour un seul symbole.

    Args :
        I (int) : Composante d'amplitude en phase (axe X).
        Q (int) : Composante d'amplitude en quadrature (axe Y).
        freq (float) : Fréquence de la porteuse en Hz.
        t (np.ndarray) : Tableau du vecteur temps généré avec NumPy.

    Returns :
        np.ndarray : Tableau représentant la forme d'onde du signal modulé combiné.
    """
    # CORRECTION : On utilise np.cos et np.sin à la place de m.cos et m.sin
    # pour pouvoir calculer tout le tableau d'un coup
    signal_I = I * np.cos(2 * np.pi * freq * t)
    signal_Q = Q * np.sin(2 * np.pi * freq * t)
    return signal_I - signal_Q


def Barker(Longeur : int) -> list:
    """Génère un code de Barker pour la détection du début d'une trame.

    Args :
        Longeur (int) : Nombre de symboles à mettre dans la trame.

    Returns :
        list[int] : La séquence du code de Barker composée de 1 et -1.
    """
    Code = []
    match Longeur:
        case 2:
            Code = [1, -1]
        case 3:
            Code = [+1, +1, -1]
        case 4:
            Code = [1, 1 -1, 1]
        case 5:
            Code = [1, 1, 1, -1, 1]
        case _:
            print("Trop Long passage en code barker = 5")
            Code = [1, 1, 1, -1, 1]
    return Code


def Barker_IQ(Code : list, QAM_number : int) -> list[list[int], list[int]]:
    """Génère les valeurs en phase (I) et en quadrature (Q) à partir d'un code de Barker.

    Args :
        Code (list) : Séquence binaire (composée de 1 et -1) à transformer.
        QAM_number (int) : Ordre ou taille de la modulation QAM (ex: 16, 64, 256).

    Returns :
        list[list[int], list[int]] : Une liste contenant `i` (coordonnées en phase) et `q` (coordonnées en quadrature).
    """
    i = []
    q = []
    reduce = 0
    if (QAM_number**0.5 ).is_integer():
        reduce = -1
    max_i, max_q = Determine_length(QAM_number)
    max_i = max_i - 1
    max_q = max_q - 1 - reduce
    for value in Code:
        if value == 1:
            i.append(max_i)
            q.append(max_q)
        else :
            i.append(-max_i)
            q.append(-max_q)
    return [i, q]
