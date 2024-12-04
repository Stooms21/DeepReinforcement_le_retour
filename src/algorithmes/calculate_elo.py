import math
import random

import numpy as np
import matplotlib.pyplot as plt
import tqdm

from src.environnements.bond.Bond import Bond
from src.algorithmes.uct import uct
from src.algorithmes.random_rollout import random_rollout
from src.algorithmes.EXIT import load_model, PolicyNetwork, chose_action
from src.algorithmes.double_deep_q_learning import load_double_deep, double_deep_chose_action
from src.algorithmes.deep_q_learning import load_deep_q,deep_chose_action



model = load_double_deep("double_deep_q_learning.pth")

model_deep_q = load_deep_q("deep_q_learning.pth")

policy_network = PolicyNetwork(input_size=21, num_actions=144)

model_path = "policy_network.pth"

load_model(policy_network, model_path)


def simulate_game(algo_a, algo_b):
    bond = Bond()
    nb_step = 0
    while not bond.is_game_over():
        action = 0
        if bond.get_turn() == 0:
            action = play_by_algo(bond, algo_a, 1)
        else:
            action = play_by_algo(bond, algo_b, -1)
        bond.step(action)
        nb_step += 1
    return bond.score(),nb_step


def play_by_algo(bond,curr_algo,color):
    if curr_algo == "Random":
        aa = bond.available_actions_ids()
        return random.choice(aa)
    elif curr_algo == "Random Rollout":
        return random_rollout(bond, 5, color)
    elif curr_algo == "EXIT":
        action = chose_action(policy_network,bond)
        return action
    elif curr_algo == "UCT":
        return uct(bond, 10, 1,color)
    elif curr_algo == "Double Deep":
        return double_deep_chose_action(model,bond)
    elif curr_algo == "Deep Q":
        return deep_chose_action(model_deep_q,bond)
    return 0

# Fonction pour calculer les probabilités d'Elo
def expected_score(rating_a, rating_b):
    """Calcule la probabilité que A gagne contre B"""
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

# Fonction pour mettre à jour les scores Elo
def update_elo(rating_a, rating_b, result_a, k=32):
    """Met à jour les scores Elo après un match.
    rating_a, rating_b : scores Elo actuels
    result_a : 1 si A gagne, -1 si B gagne, 0 pour une égalité
    k : facteur de sensibilité
    """
    adjusted_result_a = (result_a + 1) / 2  # Convertit -1/0/1 en 0/0.5/1 pour Elo
    expected_a = expected_score(rating_a, rating_b)
    expected_b = 1 - expected_a
    new_rating_a = rating_a + k * (adjusted_result_a - expected_a)
    new_rating_b = rating_b + k * ((1 - adjusted_result_a) - expected_b)
    return new_rating_a, new_rating_b

# Simulation des matchs entre algorithmes
def simulate_tournament(algorithms, num_matches=1000, k=32):
    """Simule un tournoi entre plusieurs algorithmes avec un classement Elo.
    algorithms : liste des noms d'algorithmes
    num_matches : nombre total de matchs simulés
    k : facteur de mise à jour de l'Elo
    """
    num_algorithms = len(algorithms)
    elo_scores = {algo: 1500 for algo in algorithms}  # Scores Elo initiaux
    history = {algo: [1500] for algo in algorithms}  # Historique pour les courbes

    # Matrice des résultats (gains et matchs nuls entre algorithmes)
    results_matrix = np.zeros((num_algorithms, num_algorithms), dtype=int)
    draws_matrix = np.zeros((num_algorithms, num_algorithms), dtype=int)
    mean_nb_step = 0
    for _ in range(num_matches):
        # Sélectionner deux algorithmes aléatoirement
        algo_a_idx, algo_b_idx = np.random.choice(range(num_algorithms), size=2, replace=False)
        algo_a, algo_b = algorithms[algo_a_idx], algorithms[algo_b_idx]
        rating_a, rating_b = elo_scores[algo_a], elo_scores[algo_b]

        # Simuler un résultat (1 pour A gagne, -1 pour B gagne, 0 pour nul)
        result_a,nb_step = simulate_game(algo_a, algo_b)
        mean_nb_step += nb_step
        # Mettre à jour les scores Elo
        new_rating_a, new_rating_b = update_elo(rating_a, rating_b, result_a, k)
        elo_scores[algo_a], elo_scores[algo_b] = new_rating_a, new_rating_b

        # Mettre à jour la matrice des résultats
        if result_a == 1:
            results_matrix[algo_a_idx, algo_b_idx] += 1  # A gagne contre B
        elif result_a == -1:
            results_matrix[algo_b_idx, algo_a_idx] += 1  # B gagne contre A
        elif result_a == 0:
            draws_matrix[algo_a_idx, algo_b_idx] += 1  # Nul entre A et B
            draws_matrix[algo_b_idx, algo_a_idx] += 1  # Symétrique pour nul

        # Ajouter à l'historique
        for algo in algorithms:
            history[algo].append(elo_scores[algo])
    mean_nb_step/=num_matches
    print("Moyenne des steps par match pour ", num_matches , " parties : ", mean_nb_step )
    return elo_scores, history, results_matrix, draws_matrix

# Fonction pour afficher les matrices des résultats
def print_results_matrices(algorithms, results_matrix, draws_matrix):
    """Affiche les matrices des résultats (victoires et nuls) sous forme de tableau."""
    print("\nRésultats des matchs (gagnés contre les autres) :")
    header = f"{'Algorithmes':<15}" + "".join([f"{algo:<15}" for algo in algorithms])
    print(header)
    print("-" * len(header))
    for i, algo in enumerate(algorithms):
        row = f"{algo:<15}" + "".join([f"{results_matrix[i, j]:<15}" for j in range(len(algorithms))])
        print(row)

    print("\nRésultats des matchs (matchs nuls entre les algorithmes) :")
    print(header)
    print("-" * len(header))
    for i, algo in enumerate(algorithms):
        row = f"{algo:<15}" + "".join([f"{draws_matrix[i, j]:<15}" for j in range(len(algorithms))])
        print(row)

# Affichage des courbes d'évolution Elo
def plot_elo_history(history):
    """Trace l'évolution des scores Elo pour chaque algorithme."""
    plt.figure(figsize=(12, 6))
    for algo, scores in history.items():
        plt.plot(scores, label=algo)
    plt.title("Évolution des scores Elo")
    plt.xlabel("Nombre de matchs")
    plt.ylabel("Score Elo")
    plt.legend()
    plt.grid(True)
    plt.show()

# Exemple d'algorithmes
algorithms = ["Random","Deep Q","Double Deep","UCT"]
# algorithms = ["UCT,"",EXIT","Random","Random Rollout", "reinforce_baseline"]

# Simulation
final_scores, elo_history, results_matrix, draws_matrix = simulate_tournament(algorithms, num_matches=10, k=32)

# Résultats finaux
print("Scores Elo finaux:")
for algo, score in sorted(final_scores.items(), key=lambda x: x[1], reverse=True):
    print(f"{algo}: {score:.2f}")

# Tracer les courbes
plot_elo_history(elo_history)

# Afficher les matrices des résultats
print_results_matrices(algorithms, results_matrix, draws_matrix)




