import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd
import Signal as Si


f_ech = 48000  

message = input("Donnez le texte à moduler : ")
binaire = ''.join(format(ord(c), '08b') for c in message)
print("Message binaire : ", binaire)

QAM_number = int(input("Donnez la modulation : (chiffre ex : 32)"))


message_mod, time_stop = Si.Modulation(f_ech, binaire, 5000, QAM_number, 0.5, True)

print("Envoi du signal dans la carte son (lecture + enregistrement)...")

for i in range(int(3*1/f_ech)): # corriger le décalgage de sd.playrec
    message_mod.append(0)


message_mod_recu = sd.playrec(message_mod, f_ech, channels=1)
sd.wait()
print("Enregistrement terminé.")



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


