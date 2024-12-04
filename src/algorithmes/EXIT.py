
import random
import math as m
import time
import numpy as np
import random
import torch
import torch.nn as nn
import torch.optim as optim
from tqdm import tqdm  # Pour afficher une barre de progression
from src.environnements.bond.Bond import Bond

def MCTS(env, state, policy_apprentice, nb_action, c):
    env.reset()
    env.create_game_by_state(state)
    color = env.get_turn()
    if color == 0:
        color = 1
    else:
        color = -1
    tree = {}
    root = env.state_id()  # Identifier l'état racine
    tree = update_tree(env, tree, root)
    for nb_move in (range(nb_action)):
        # Copie initiale de l'environnement
        env_copy = env.copy()

        # Étape 1: Sélection
        state_id, actions_played, visited_states = selection(env_copy, tree, root, c,policy_apprentice)

        # Étape 2: Expansion (si nécessaire)
        if state_id not in tree:
            tree = update_tree(env_copy, tree, state_id)

        # Étape 3: Simulation
        score_final = rollout(env_copy, color)

        # Étape 4: Backpropagation
        backpropagation(tree, visited_states, actions_played, score_final)

    # Sélection de la meilleure action depuis la racine
    best_action = select_best_action(tree[root])
    root_node = tree[root]
    nb_visited_total = sum(triplet[1] for triplet in root_node.values())
    total_actions = env.num_actions()  # Nombre total d'actions possibles
    distribution = np.zeros(total_actions)  # Distribution initialisée à 0
    if nb_visited_total > 0:
        for a in env.available_actions():  # Remplir uniquement les actions légales
            distribution[a] = root_node[a][1] / nb_visited_total
    distribution = normalize_distribution(distribution)

    return distribution


def selection(env, tree, root, c, policy_apprentice):
    """
    Sélectionne un chemin dans l'arbre jusqu'à un nœud inexistant ou un état terminal.
    """
    state_id = root
    actions_played = []
    visited_states = [state_id]

    while state_id in tree and not env.is_game_over():
        current_node = tree[state_id]
        action_select,nb_visited = select_action(env, current_node, c, policy_apprentice)
        if nb_visited == 0:
            actions_played.append(action_select)
            visited_states.append(state_id)
            return state_id, actions_played, visited_states
        env.step(action_select)
        state_id = env.state_id()

        actions_played.append(action_select)
        visited_states.append(state_id)

    return state_id, actions_played, visited_states


def select_action(env, node, c, policy_apprentice):
    """
    Sélectionne l'action avec le plus grand score UCB ou une action non explorée.
    """
    nb_visited_total = sum(triplet[1] for triplet in node.values())
    best_ucb = float('-inf')
    action_select = None
    vector = env.one_hot_state_desc()
    for action, (score, nb_visited) in node.items():
        if nb_visited == 0:
            # Priorité aux actions non visitées
            return action,0
        # Calcul du score UCB
        exploitation = score / nb_visited
        exploration = c * m.sqrt(m.log(nb_visited_total) / nb_visited)
        ucb = exploitation + exploration
        w = 10
        state = torch.tensor(vector)
        state = state.unsqueeze(0)
        action_probabilities = policy_apprentice(state.float())  # Action probabilities de taille (1, 144)
        estimated_proba = action_probabilities[0, action]
        ucb = ucb + w * (estimated_proba / (nb_visited + 1))
        if ucb > best_ucb:
            best_ucb = ucb
            action_select = action

    return action_select,1


def update_tree(env, tree, state_id):
    """
    Ajoute de nouveaux nœuds et actions à l'arbre si l'état est inconnu.
    """
    if state_id not in tree:
        tree[state_id] = {a: (0, 0) for a in env.available_actions()}
    return tree


def rollout(env_copy, color):
    """
    Effectue une simulation aléatoire depuis l'état actuel jusqu'à une fin de partie.
    """
    while not env_copy.is_game_over():
        random_action = random.choice(env_copy.available_actions())
        env_copy.step(random_action)
    return env_copy.score() * color


def backpropagation(tree, visited_states, actions_played, score_final):
    """
    Met à jour les scores et les compteurs pour toutes les actions jouées lors de la simulation.
    """
    for i, state_id in enumerate(visited_states[:-1]):  # Ne pas inclure l'état terminal
        action = actions_played[i]
        node = tree[state_id]
        score, nb_visited = node[action]

        # Mise à jour du score et du nombre de visites
        node[action] = (score + score_final, nb_visited + 1)


def select_best_action(node):
    """
    Sélectionne l'action la plus visitée à partir d'un nœud.
    """
    best_action = max(node.items(), key=lambda x: x[1][1])[0]
    return best_action

def normalize_distribution(distribution):
    """
    Normalise une distribution de probabilités pour qu'elle somme à 1.
    Si la somme est 0 (pas d'actions légales visitées), la distribution reste inchangée.
    """
    total = np.sum(distribution)
    if total > 0:
        return distribution / total
    return distribution

# Définition du réseau de neurones pour l'apprenti
class PolicyNetwork(nn.Module):
    def __init__(self, input_size, num_actions):
        super(PolicyNetwork, self).__init__()
        self.model = nn.Sequential(
            nn.Flatten(),
            nn.Linear(input_size, 64),
            nn.ReLU(),
            nn.Linear(64, 64),
            nn.ReLU(),
            nn.Linear(64, num_actions),
            nn.Softmax(dim=-1)  # Distribution de probabilité sur les actions
        )

    def forward(self, x):
        return self.model(x)

# Entraînement de l'apprenti avec des cibles d'imitation
def train_policy_network(policy_network, optimizer, dataset, num_epochs=100, batch_size=8):
    loss_fn = nn.CrossEntropyLoss()
    policy_network.train()

    states, target_policies = zip(*dataset)
    states = torch.tensor(np.array(states), dtype=torch.float32)
    num_actions = 144  # Nombre total d'actions possibles
    target_policies_fixed = []

    for policy in target_policies:
        if len(policy) < num_actions:
            # Remplir avec des zéros pour atteindre la taille num_actions
            fixed_policy = np.zeros(num_actions, dtype=np.float32)
            fixed_policy[:len(policy)] = policy  # Copiez les valeurs existantes
            target_policies_fixed.append(fixed_policy)
        else:
            target_policies_fixed.append(policy)

    # Maintenant, utilisez target_policies_fixed pour créer le tensor
    target_policies = torch.tensor(np.array(target_policies_fixed), dtype=torch.float32)

    dataset_size = len(states)
    for epoch in range(num_epochs):
        permutation = torch.randperm(dataset_size)
        for i in range(0, dataset_size, batch_size):
            indices = permutation[i:i+batch_size]
            batch_states = states[indices]
            batch_targets = target_policies[indices]
            batch_targets = batch_targets

            # Prédictions et perte
            predictions = policy_network(batch_states)
            loss = loss_fn(predictions, batch_targets.argmax(dim=1))  # Cross-Entropy

            # Backpropagation
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

# Expert Iteration (EXIT)
def expert_iteration(env, policy_network, num_iterations=10, games_per_iteration=25,nb_mcts=1000):
    optimizer = optim.Adam(policy_network.parameters(), lr=0.001)

    for iteration in tqdm(range(num_iterations)):

        # Étape 1 : Collecte de données via self-play
        dataset = []
        with tqdm(total=games_per_iteration, desc="Self-play", unit="game") as pbar:
            for _ in range(games_per_iteration):
                env.reset()
                states, actions = [], []
                while not env.is_game_over():
                    state = torch.tensor(env.one_hot_state_desc().flatten(), dtype=torch.float32).unsqueeze(0)
                    legal_actions = env.available_actions()

                    # Utiliser l'apprenti pour choisir une action
                    with torch.no_grad():
                        action_probs = policy_network(state).numpy().flatten()
                    # Obtenir la liste des actions possibles
                    possible_actions = env.available_actions()  # Exemple: [1, 5, 10, ...]

                    # Créer un masque pour les actions impossibles
                    mask = np.zeros_like(action_probs)
                    mask[possible_actions] = 1  # Mettre 1 pour les indices correspondants aux actions possibles

                    # Appliquer le masque : les probabilités des actions impossibles deviennent 0
                    masked_probs = action_probs * mask

                    # Normaliser les probabilités (nécessaire pour une sélection valide)
                    if masked_probs.sum() == 0:
                        action = np.random.choice(possible_actions)
                    else:
                        masked_probs /= masked_probs.sum()

                    # Sélectionner une action en fonction des probabilités masquées
                    action = np.random.choice(len(masked_probs), p=masked_probs)

                    states.append(state)
                    actions.append(action)

                    # Appliquer l'action
                    env.step(action)

                # Ajouter les données de la partie dans le dataset
                for state, action in zip(states, actions):
                    policy = np.zeros(144)
                    policy[action] = 1.0
                    dataset.append((state, policy))
                pbar.update(1)
        # Étape 2 : Planification avec MCTS (amélioration de l'expert)
        with tqdm(total=len(dataset), desc="MCTS", unit="step") as pbar_mcts:
            for i, (state, _) in enumerate(dataset):
                mcts_policy = MCTS(env,state, policy_network,nb_mcts,1)  # Appel à l'expert
                dataset[i] = (state, mcts_policy)  # Mise à jour avec la politique améliorée
                pbar_mcts.update(1)

        # Étape 3 : Apprentissage supervisé (imitation de l'expert)
        train_policy_network(policy_network, optimizer, dataset)
    # save_model(policy_network, "policy_network.pth")

def save_model(model, filepath):
    """
    Sauvegarde le modèle entraîné dans un fichier.
    """
    torch.save(model.state_dict(), filepath)

    print(f"Modèle sauvegardé à {filepath}")

def load_model(model, filepath):
    """
    Charge les poids d'un modèle depuis un fichier.
    """

    state_dict = torch.load(filepath, weights_only=True)
    model.load_state_dict(state_dict)
    print(f"Modèle chargé depuis {filepath}")

def chose_action(train_policy_network,env):
    state = torch.tensor(env.one_hot_state_desc().flatten(), dtype=torch.float32).unsqueeze(0)
    # Utiliser l'apprenti pour choisir une action
    with torch.no_grad():
        action_probs = train_policy_network(state).numpy().flatten()
    # Obtenir la liste des actions possibles
    possible_actions = env.available_actions()  # Exemple: [1, 5, 10, ...]

    # Créer un masque pour les actions impossibles
    mask = np.zeros_like(action_probs)
    mask[possible_actions] = 1  # Mettre 1 pour les indices correspondants aux actions possibles

    # Appliquer le masque : les probabilités des actions impossibles deviennent 0
    masked_probs = action_probs * mask

    # Normaliser les probabilités (nécessaire pour une sélection valide)
    if masked_probs.sum() == 0:
        action = np.random.choice(possible_actions)
    else:
        masked_probs /= masked_probs.sum()

    # Sélectionner une action en fonction des probabilités masquées
    action = np.argmax(masked_probs)
    return action
if __name__ == "__main__":
    # Initialisation
    bond = Bond()
    policy_network = PolicyNetwork(input_size=21, num_actions=144)  # Plateau 3x3 => 9 cases/actions
    # #
    # # Lancer l'algorithme EXIT
    expert_iteration(bond, policy_network, num_iterations=10, games_per_iteration=10,nb_mcts=1000)