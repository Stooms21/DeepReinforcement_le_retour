from src.utils import utils as ut
import src.utils.dqn_utils as dqu
import tqdm
import models
from config.algos_config import CONFIG_FILE, DDQN_HIDDEN_LAYER_SIZE, ENV_MODULE_MAPPING


def deep_q_learning(
        env,
        alpha: float = 0.0001,
        epsilon: float = 1.0,
        epsilon_min: float = 0.01,
        epsilon_decay: float = 0.995,
        gamma: float = 0.999,
        nb_episode: int = 1000,
        nb_target_update: int = 10
):
    """
    Fonction d'apprentissage par Q-learning profond avec double réseau de neurones. 
    Elle retourne le réseau de neurone de politique entrainé.
    """

    # Initialiser Q(s,a) de manière arbitraire
    input_layer_size = env.get_one_hot_size()
    output_layer_size = env.num_actions()
    policy_network = models.QNet(input_layer_size, output_layer_size, DDQN_HIDDEN_LAYER_SIZE)

    # Initialiser le réseau cible
    target_network = models.QNet(input_layer_size, output_layer_size, DDQN_HIDDEN_LAYER_SIZE)
    target_network.load_state_dict(policy_network.state_dict())

    # Boucle pour chaque épisode
    for _ in tqdm.tqdm(range(nb_episode)):
        # Initialiser S
        env.reset()
        # Copier le réseau de politique dans le réseau cible nb_target_update fois
        if _ % (nb_episode // nb_target_update) == 0:
            target_network.load_state_dict(policy_network.state_dict())

        # Boucle pour chaque étape de l'épisode
        while not env.is_game_over():
            s = env.one_hot_state_desc()
            available_actions = env.available_actions()

            # Choisir A à partir de S en utilisant la politique dérivée de Q
            a = dqu.choose_epsilon_greedy_action(policy_network, s, available_actions, epsilon)

            # Prendre l'action A, observer R, S'
            reward, s_prime, available_actions_prime = dqu.observe_R_S_prime(env, a)

            # Calculer Q(s,a) et Q_target
            q_value, q_target = dqu.compute_q_values_and_q_target(env, policy_network, s, s_prime, a, gamma, reward, target_network)

            # Mettre à jour Q(s,a)
            policy_network.backward(q_value, q_target)

        # Décroissance de epsilon
        epsilon = max(epsilon_min, epsilon * epsilon_decay)

    return policy_network

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
    reward = 0
    # Boucle pour jouer 10 parties
    for i in range(1, 11):
        # Réinitialiser l'environnement
        env.reset()
        # Appliquer l'apprentissage par Q-learning profond
        policy_network = deep_q_learning(env)
        # Jouer une partie avec le réseau de politique appris
        reward += env.play(policy_network)
        # Afficher la récompense moyenne sur les parties jouées
        print(f"Reward moyen: {reward / i} sur {i} parties")