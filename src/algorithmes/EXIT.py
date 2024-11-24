
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

def MCTS(env,state,policy_network, nb_action, c):
    env.reset()
    env.create_game_by_state(state)
    color = env.get_turn()
    tree = {}
    root = env.state_id()  # Identifier l'état racine
    tree = update_tree(env, tree, root)
    start_time = time.time()
    for _ in range(nb_action):
        # Copie initiale de l'environnement
        env_copy = env.copy()

        # Étape 1: Sélection
        state_id, actions_played, visited_states = selection(env_copy, tree, root, c)

        # Étape 2: Expansion (si nécessaire)
        if state_id not in tree:
            tree = update_tree(env_copy, tree, state_id)

        # Étape 3: Simulation
        score_final = rollout(env_copy, color)

        # Étape 4: Backpropagation
        backpropagation(tree, visited_states, actions_played, score_final)

    # Sélection de la meilleure action depuis la racine
    best_action = select_best_action(tree[root])
    return best_action


def selection(env, tree, root, c):
    """
    Sélectionne un chemin dans l'arbre jusqu'à un nœud inexistant ou un état terminal.
    """
    state_id = root
    actions_played = []
    visited_states = [state_id]

    while state_id in tree and not env.is_game_over():
        current_node = tree[state_id]
        action_select = select_action(current_node, c)
        env.step(action_select)
        state_id = env.state_id()

        actions_played.append(action_select)
        visited_states.append(state_id)

    return state_id, actions_played, visited_states


def select_action(node, c):
    """
    Sélectionne l'action avec le plus grand score UCB ou une action non explorée.
    """
    nb_visited_total = sum(triplet[1] for triplet in node.values())
    best_ucb = float('-inf')
    action_select = None

    for action, (score, nb_visited) in node.items():
        if nb_visited == 0:
            # Priorité aux actions non visitées
            return action
        # Calcul du score UCB
        exploitation = score / nb_visited
        exploration = c * m.sqrt(m.log(nb_visited_total) / nb_visited)
        ucb = exploitation + exploration

        if ucb > best_ucb:
            best_ucb = ucb
            action_select = action

    return action_select


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


def sample_self_play(param):
    pass


def imitation_learning_target(param):
    pass


def train_policy(Di):
    pass


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
def train_policy_network(policy_network, optimizer, dataset, num_epochs=10, batch_size=32):
    loss_fn = nn.CrossEntropyLoss()
    policy_network.train()

    states, target_policies = zip(*dataset)
    states = torch.tensor(np.array(states), dtype=torch.float32)
    target_policies = torch.tensor(np.array(target_policies), dtype=torch.float32)

    dataset_size = len(states)
    for epoch in range(num_epochs):
        permutation = torch.randperm(dataset_size)
        for i in range(0, dataset_size, batch_size):
            indices = permutation[i:i+batch_size]
            batch_states = states[indices]
            batch_targets = target_policies[indices]
            batch_targets = batch_targets.long()

            # Prédictions et perte
            predictions = policy_network(batch_states)
            loss = loss_fn(predictions, batch_targets)  # Pas besoin de .argmax()

            # Backpropagation
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

# Expert Iteration (EXIT)
def expert_iteration(env, policy_network, num_iterations=10, games_per_iteration=25):
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
                    action = random.choices(legal_actions, weights=[action_probs[a] for a in legal_actions])[0]

                    states.append(state)
                    actions.append(action)

                    # Appliquer l'action
                    env.step(action)

                # Ajouter les données de la partie dans le dataset
                for state, action in zip(states, actions):
                    policy = np.zeros(144)  # 9 : nombre total d'actions possibles
                    policy[action] = 1.0
                    dataset.append((state, policy))
                pbar.update(1)
        # Étape 2 : Planification avec MCTS (amélioration de l'expert)
        with tqdm(total=len(dataset), desc="MCTS", unit="step") as pbar_mcts:
            for i, (state, _) in enumerate(dataset):
                mcts_policy = MCTS(env,state, policy_network,500,2)  # Appel à l'expert
                dataset[i] = (state, mcts_policy)  # Mise à jour avec la politique améliorée
                pbar_mcts.update(1)

        # Étape 3 : Apprentissage supervisé (imitation de l'expert)
        train_policy_network(policy_network, optimizer, dataset)
    save_model(policy_network, "policy_network.pth")
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
    model.load_state_dict(torch.load(filepath))
    model.eval()  # Passer en mode évaluation (désactive dropout, batchnorm, etc.)
    print(f"Modèle chargé depuis {filepath}")

def play_game_against_random(env, policy_network):
    """
    Joue une partie contre un adversaire aléatoire.
    Le réseau de neurones joue toujours en premier.
    """
    env.reset()

    while not env.is_game_over():

        if env.get_turn() == 0:
            # Le réseau choisit une action
            state = torch.tensor(env.one_hot_state_desc(), dtype=torch.float32).unsqueeze(0)
            legal_actions = env.available_actions()

            with torch.no_grad():
                action_probs = policy_network(state).numpy().flatten()
            action = random.choices(legal_actions, weights=[action_probs[a] for a in legal_actions])[0]
            print(f"Réseau joue : {action}")
        else:
            # Joueur aléatoire choisit une action
            legal_actions = env.available_actions()
            action = random.choice(legal_actions)
            print(f"Joueur aléatoire joue : {action}")

        # Appliquer l'action
        env.step(action)

    print(env.get_winners())


if __name__ == "__main__":
    # Initialisation
    bond = Bond()
    policy_network = PolicyNetwork(input_size=21, num_actions=bond.num_actions())  # Plateau 3x3 => 9 cases/actions
    #
    # Lancer l'algorithme EXIT
    expert_iteration(bond, policy_network, num_iterations=1, games_per_iteration=1)
    # # Charger un modèle sauvegardé
    # model_path = "policy_network.pth"
    # load_model(policy_network, model_path)
    # bond = Bond()
    # # Jouer une partie contre un joueur aléatoire
    # play_game_against_random(bond, policy_network)