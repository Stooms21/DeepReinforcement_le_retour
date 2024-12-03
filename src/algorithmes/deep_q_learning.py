import torch

from src.utils import utils as ut
import src.utils.dqn_utils as dqu
import tqdm
import src.algorithmes.models as models
from config.algos_config import CONFIG_FILE, DQN_HIDDEN_LAYER_SIZE, ENV_MODULE_MAPPING
import src.environnements.bond.Bond as b
import numpy as np

def deep_q_learning(
        env,
        alpha: float = 0.0001,
        epsilon: float = 1.0,
        epsilon_min: float = 0.01,
        epsilon_decay: float = 0.995,
        gamma: float = 0.999,
        nb_episode: int = 1000,
):
    """
    Fonction d'apprentissage par Q-learning profond. Elle retourne le réseau de neurone entrainé.
    Ce réseau de neurone est ensuite utilisé pour estimer la meilleure action à prendre à chaque état.
    """

    # Initialiser Q(s,a) de manière arbitraire
    input_layer_size = env.get_one_hot_size()
    output_layer_size = env.num_actions()
    policy_network = models.QNet(input_layer_size, output_layer_size, DQN_HIDDEN_LAYER_SIZE)

    # Boucle pour chaque épisode
    for _ in tqdm.tqdm(range(nb_episode)):
        # Initialiser S
        env.reset()
        # Boucle pour chaque étape de l'épisode
        while not env.is_game_over():
            s = torch.tensor(env.one_hot_state_desc().flatten(), dtype=torch.float32).unsqueeze(0)
            available_actions = env.available_actions()

            # Choisir A à partir de S en utilisant la politique dérivée de Q
            a = dqu.choose_epsilon_greedy_action(policy_network, s, available_actions, epsilon)

            # Prendre l'action A, observer R, S'
            reward, s_prime, available_actions_prime = dqu.observe_R_S_prime(env, a)

            available_actions_prime = env.available_actions()

            # Calculer Q(s,a) et Q_target
            q_value, q_target = dqu.compute_q_values_and_q_target(env, policy_network, s, s_prime, a, gamma, reward, available_actions_prime=available_actions_prime)

            # Mettre à jour Q(s,a)
            policy_network.backward(q_value, q_target)

        # Décroissance de epsilon
        epsilon = max(epsilon_min, epsilon * epsilon_decay)

    save_path =  "deep_q_learning.pth"
    # Sauvegarde du réseau entraîné
    torch.save(policy_network.state_dict(), save_path)
    print(f"Modèle sauvegardé à {save_path}")
    return policy_network


def load_deep_q(model_path: str):
    """
    Charger un réseau de neurones sauvegardé et jouer une partie.
    """
    input_layer_size =21
    output_layer_size = 144
    loaded_model = models.QNet(input_layer_size, output_layer_size, DQN_HIDDEN_LAYER_SIZE)

    # Charger les poids sauvegardés
    state_dict = torch.load(model_path,weights_only=True)
    loaded_model.load_state_dict(state_dict)
    return loaded_model

def deep_chose_action(train_policy_network,env_bond):
    state = torch.tensor(env_bond.one_hot_state_desc().flatten(), dtype=torch.float32).unsqueeze(0)
    # Utiliser l'apprenti pour choisir une action
    with torch.no_grad():
        action_probs = train_policy_network(state).numpy().flatten()
    # Obtenir la liste des actions possibles
    possible_actions = env_bond.available_actions()  # Exemple: [1, 5, 10, ...]

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
    # Nom de l'environnement
    env_name = "LineWorld"
    # Charger la configuration de l'environnement
    config = ut.load_config(CONFIG_FILE, env_name)
    # Obtenir le module de l'environnement
    env_module = ENV_MODULE_MAPPING[env_name]
    # Obtenir la classe de l'environnement
    env_class = getattr(env_module, env_name)
    # Initialiser l'environnement avec la configuration
    env = env_class(config)
    env = b.Bond()
    reward = 0
    # Boucle pour jouer 10 parties
    for i in range(1, 2):
        # Réinitialiser l'environnement
        env.reset()
        # Appliquer l'apprentissage par Q-learning profond
        policy_network = deep_q_learning(env)
        # Jouer une partie avec le réseau de politique appris


