import math
import random

import numpy as np
import matplotlib.pyplot as plt
import tqdm

from src.environnements.bond.Bond import Bond
from src.algorithmes.uct import uct
from src.algorithmes.random_rollout import random_rollout
import torch
from src.algorithmes.EXIT import load_model,PolicyNetwork

import tensorflow as tf
from src.algorithmes.models import PolicyNetwork
policy_network = PolicyNetwork(input_size=21, num_actions=144)

model_path = "policy_network.pth"
load_model(policy_network, model_path)

def simulate_game(algo_a, algo_b):
    bond = Bond()
    while not bond.is_game_over():
        action = 0
        if bond.get_turn() == 0:
            action = play_by_algo(bond, algo_a, 1)
        else:
            action = play_by_algo(bond, algo_b, -1)
        bond.step(action)
    return bond.score()


def play_by_algo(bond,curr_algo,color):
    if curr_algo == "Random":
        aa = bond.available_actions_ids()
        return random.choice(aa)
    elif curr_algo == "Random Rollout":
        return random_rollout(bond, 6, color)
    elif curr_algo == "EXIT":
        # Le réseau choisit une action
        state = torch.tensor(bond.one_hot_state_desc(), dtype=torch.float32).unsqueeze(0)
        legal_actions = bond.available_actions()

        with torch.no_grad():
            action_probs = policy_network(state).numpy().flatten()
        # Obtenir la liste des actions possibles
        possible_actions = bond.available_actions()  # Exemple: [1, 5, 10, ...]

        # Créer un masque pour les actions impossibles
        mask = np.zeros_like(action_probs)
        mask[possible_actions] = 1  # Mettre 1 pour les indices correspondants aux actions possibles

        # Appliquer le masque : les probabilités des actions impossibles deviennent 0
        masked_probs = action_probs * mask

        # Normaliser les probabilités (nécessaire pour une sélection valide)
        if masked_probs.sum() == 0:
            action = np.random.choice(possible_actions)
            print("random")
        else:
            masked_probs /= masked_probs.sum()

            # Sélectionner une action en fonction des probabilités masquées
            action = np.random.choice(len(masked_probs), p=masked_probs)

            state = torch.tensor(bond.one_hot_state_desc())
            state = state.unsqueeze(0)
            action_probabilities = policy_network(state.float())  # Action probabilities de taille (1, 144)
            estimated_proba = action_probabilities[0, action]
        return action
    elif curr_algo == "UCT":
        return uct(bond, 10, 1, color,2500)
    elif curr_algo == "reinforce":
        state = bond.one_hot_state_desc()
        action_probs = policy_network.call(state)
        possible_actions = bond.available_actions()
        mask = np.zeros_like(action_probs)
        mask[possible_actions] = 1
        masked_probs = action_probs * mask
        # Normaliser les probabilités (nécessaire pour une sélection valide)
        if masked_probs.sum() == 0:
            action = np.random.choice(possible_actions)
            print("random")
        else:
            masked_probs /= masked_probs.sum()

            # Sélectionner une action en fonction des probabilités masquées
            action = np.random.choice(len(masked_probs), p=masked_probs)
        bond.step(action)

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

    for _ in range(num_matches):
        # Sélectionner deux algorithmes aléatoirement
        algo_a_idx, algo_b_idx = np.random.choice(range(num_algorithms), size=2, replace=False)
        algo_a, algo_b = algorithms[algo_a_idx], algorithms[algo_b_idx]
        rating_a, rating_b = elo_scores[algo_a], elo_scores[algo_b]

        # Simuler un résultat (1 pour A gagne, -1 pour B gagne, 0 pour nul)
        result_a = simulate_game(algo_a, algo_b)

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
algorithms = ["UCT,"",EXIT","Random","Random Rollout"]

# Simulation
final_scores, elo_history, results_matrix, draws_matrix = simulate_tournament(algorithms, num_matches=100, k=32)

# Résultats finaux
print("Scores Elo finaux:")
for algo, score in sorted(final_scores.items(), key=lambda x: x[1], reverse=True):
    print(f"{algo}: {score:.2f}")

# Tracer les courbes
plot_elo_history(elo_history)

# Afficher les matrices des résultats
print_results_matrices(algorithms, results_matrix, draws_matrix)




