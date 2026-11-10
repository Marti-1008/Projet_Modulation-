import sys
from pathlib import Path
import matplotlib.pyplot as plt

# Détermination exacte du dossier racine 'Projet_modulation' d'après ton arborescence
dossier_racine = Path(__file__).resolve().parents[4]
sys.path.append(str(dossier_racine))

# L'import fonctionnera maintenant à coup sûr !
import modulation.algo.qam.QAM_mod as QAM_mod


def sauvegarder_donnees_qam(ordre, labels, points):
    """
    Crée un sous-dossier 'datasets' s'il n'existe pas, et y sauvegarde 
    le mapping binaire -> symbole (I, Q) uniquement si le fichier n'existe pas déjà.
    """
    # Définition du chemin vers le dossier 'datasets' (dans le dossier plot)
    dossier_destination = Path(__file__).resolve().parent / "datasets"
    dossier_destination.mkdir(exist_ok=True)
    
    nom_fichier = dossier_destination / f"mapping_{ordre}qam.txt"

    if nom_fichier.exists():
        print(f"Le fichier de données '{nom_fichier}' existe déjà. Sauvegarde ignorée.")
        return

    print(f"Sauvegarde du mapping de la {ordre}-QAM dans '{nom_fichier}'...")
    with open(nom_fichier, "w", encoding="utf-8") as f:
        f.write(f"# Cartographie Complète de la {ordre}-QAM\n")
        f.write("# Format : Code_Binaire -> (En-Phase I, Quadrature Q)\n")
        f.write("-" * 50 + "\n")
        for bits_str, p in zip(labels, points):
            # p[0] est la composante I, p[1] est la composante Q
            f.write(f"{bits_str} -> ({p[0]}, {p[1]})\n")
    print(f"Fichier '{nom_fichier}' créé avec succès.")


# ==========================================
# GÉNÉRATION DES POINTS ET ENREGISTREMENT
# ==========================================

# 1. Génération de TOUS les points de la 16-QAM (16 symboles, 4 bits)
points_16 = []
labels_16 = []
for val in range(16):
    bits_str = format(val, "04b")
    points_16.append(QAM_mod.Transform(bits_str, 16))
    labels_16.append(bits_str)

sauvegarder_donnees_qam(16, labels_16, points_16)

# 2. Génération de TOUS les points de la 32-QAM (32 symboles, 5 bits)
points_32 = []
labels_32 = []
for val in range(32):
    bits_str = format(val, "05b")
    points_32.append(QAM_mod.Transform(bits_str, 32))
    labels_32.append(bits_str)

sauvegarder_donnees_qam(32, labels_32, points_32)


# ==========================================
# TRACÉ GRAPHIQUE (MATPLOTLIB)
# ==========================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# --- Affichage 16-QAM ---
I_16 = [p[0] for p in points_16]
Q_16 = [p[1] for p in points_16]
ax1.scatter(I_16, Q_16, color="blue", s=120, zorder=3)
for j, txt in enumerate(labels_16):
    ax1.annotate(
        txt,
        (I_16[j], Q_16[j]),
        textcoords="offset points",
        xytext=(0, 10),
        ha="center",
        fontsize=9,
        fontweight="bold",
    )

ax1.set_title("Constellation 16-QAM Complète (Grille Carrée)", fontsize=12)
ax1.set_xlim(-6, 6)
ax1.set_ylim(-6, 6)
ax1.grid(True, linestyle="--", alpha=0.5)
ax1.axhline(0, color="black", linewidth=1)
ax1.axvline(0, color="black", linewidth=1)

# --- Affichage 32-QAM ---
I_32 = [p[0] for p in points_32]
Q_32 = [p[1] for p in points_32]
ax2.scatter(I_32, Q_32, color="red", s=120, zorder=3)
for j, txt in enumerate(labels_32):
    ax2.annotate(
        txt,
        (I_32[j], Q_32[j]),
        textcoords="offset points",
        xytext=(0, 10),
        ha="center",
        fontsize=8,
        fontweight="bold",
    )

ax2.set_title("Constellation 32-QAM Complète (Forme Croix Broadcom)", fontsize=12)
ax2.set_xlim(-8, 8)
ax2.set_ylim(-8, 8)
ax2.grid(True, linestyle="--", alpha=0.5)
ax2.axhline(0, color="black", linewidth=1)
ax2.axvline(0, color="black", linewidth=1)

plt.tight_layout()
plt.show()
