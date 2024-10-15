import time
import Bond as b
import random
import multiprocessing
import gc


# Fonction qui simule une partie du jeu
def play_game(_):
    bond = b.Bond()

    # On récupère toutes les actions possibles une fois et on les utilise pendant la partie
    while not bond.is_game_over():
        available_actions = bond.available_actions()
        action = random.choice(available_actions)
        bond.step(action)


# Fonction pour jouer plusieurs parties en parallèle (multiprocessing)
def jouer_parties_multiprocess(nombre_de_parties, nombre_de_processus):
    with multiprocessing.Pool(processes=nombre_de_processus) as pool:
        pool.map(play_game, range(nombre_de_parties))


# Fonction pour mesurer le temps et le nombre de parties par seconde avec multiprocessing
def mesurer_vitesse_multiprocessing(nombre_de_parties, nombre_de_processus):
    # Désactiver le garbage collector temporairement pour optimiser la mémoire
    gc.disable()

    # Prendre le temps au début
    debut = time.time()

    # Jouer les parties en parallèle avec multiprocessing
    jouer_parties_multiprocess(nombre_de_parties, nombre_de_processus)

    # Prendre le temps à la fin
    fin = time.time()

    # Réactiver le garbage collector après avoir terminé
    gc.enable()

    # Calculer le temps écoulé
    temps_total = fin - debut

    # Calculer le nombre de parties par seconde
    parties_par_seconde = nombre_de_parties / temps_total

    return temps_total, parties_par_seconde


# Encapsulation dans le bloc 'if __name__ == "__main__"'
if __name__ == "__main__":
    # Nombre de parties à jouer
    nombre_de_parties = 1000

    # Mesurer pour 1000 parties avec un nombre de processus égal aux cœurs CPU disponibles
    nombre_de_processus = multiprocessing.cpu_count()  # Utilise tous les cœurs disponibles
    temps_total, parties_par_seconde = mesurer_vitesse_multiprocessing(nombre_de_parties, 8)

    # Affichage des résultats
    print(f"Temps total pour {nombre_de_parties} parties avec {8} processus : {temps_total:.2f} secondes")
    print(f"Nombre de parties par seconde : {parties_par_seconde:.2f}")
