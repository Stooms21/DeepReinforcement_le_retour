import random
import math as m
from tqdm import tqdm  # Pour afficher une barre de progression


def uct(env, nb_action_play, c, color=1):
    tree = {}
    root = env.state_id()  # Identifier l'état racine
    tree = update_tree(env, tree, root)

    for _ in tqdm(range(nb_action_play)):
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
