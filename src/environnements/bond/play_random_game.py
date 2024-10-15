import time
import Bond as b
import random
import tqdm
import cProfile
#from numba import jit


# Fonction qui simule une partie de ton jeu
def play_game():
    bond = b.Bond()
    while(not bond.is_game_over()):
        aa = bond.available_action()
        action = random.choice(aa)
        bond.step(action)

# Fonction pour jouer plusieurs parties et mesurer le temps
def mesurer_vitesse(nombre_de_parties):
    # Prendre le temps au début
    debut = time.time()

    # Jouer un certain nombre de parties
    for _ in range(nombre_de_parties):
        play_game()

    # Prendre le temps à la fin
    fin = time.time()

    # Calculer le temps écoulé
    temps_total = fin - debut

    # Calculer le nombre de parties par seconde
    parties_par_seconde = nombre_de_parties / temps_total

    return temps_total, parties_par_seconde


# Mesurer pour 1000 parties
nombre_de_parties = 1000
temps_total, parties_par_seconde = mesurer_vitesse(nombre_de_parties) #cProfile.run('mesurer_vitesse(nombre_de_parties)')


print(f"Temps total pour {nombre_de_parties} parties : {temps_total:.2f} secondes")
print(f"Nombre de parties par seconde : {parties_par_seconde:.2f}")





