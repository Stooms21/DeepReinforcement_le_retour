from config.algos_config import CONFIG_FILE, ENV_MODULE_MAPPING
from src.utils.dqn_utils import observe_R_S_prime
from src.utils.utils import load_config
from src.algorithmes.models import PolicyNetwork
import numpy as np
from tqdm import tqdm
import tensorflow as tf
from src.environnements.bond.Bond import Bond


def reinforce(
        env,
        alpha: float = 0.0001,
        gamma: float = 0.999,
        nb_episode: int = 100,
):
    """
    Fonction d'apprentissage REINFORCE. Elle retourne le réseau de neurone entrainé.
    Ce réseau de neurone est ensuite utilisé pour estimer la meilleure action à prendre à chaque état.
    """

    # Initialisation du policy network de manière arbitraire
    input_layer_size = env.get_one_hot_size()
    output_layer_size = env.num_actions()
    policy_network = PolicyNetwork(input_layer_size, output_layer_size, alpha=alpha)
    for _ in tqdm(range(nb_episode)):
        env.reset()  # Réinitialiser l'environnement
        states, actions, rewards = [], [], []

        # Générer un épisode
        done = False
        while not done:
            s = env.one_hot_state_desc()
            states.append(tf.convert_to_tensor(s, dtype=tf.float32))

            # Prédiction et choix d'action
            action_probs = policy_network.call(s)
            possible_actions = env.available_actions()
            mask = np.zeros_like(action_probs)
            mask[possible_actions] = 1
            masked_probs = action_probs * mask

            if masked_probs.sum() == 0:
                a = np.random.choice(possible_actions)
            else:
                masked_probs /= masked_probs.sum()

            a = tf.random.categorical(tf.math.log([masked_probs]), 1).numpy()[0, 0]
            actions.append(a)

            r, s_prime, available_actions_prime = observe_R_S_prime(env, a)
            rewards.append(r)
            done = env.is_game_over()

        # Calcul des retours G_t
        rewards = np.array(rewards)
        discount_factors = np.power(gamma, np.arange(len(rewards)))
        returns = np.cumsum(rewards[::-1] * discount_factors[::-1])[::-1]

        # Mise à jour des paramètres pour chaque étape de l'épisode
        for state, action, G_t in zip(states, actions, returns):
            policy_network.train_step(state, action, G_t)

    return policy_network

if __name__ == "__main__":
    # # Nom de l'environnement
    # env_name = "GridWorld"
    # # Charger la configuration de l'environnement
    # config = load_config(CONFIG_FILE, env_name)
    # # Obtenir le module de l'environnement
    # env_module = ENV_MODULE_MAPPING[env_name]
    # # Obtenir la classe de l'environnement
    # env_class = getattr(env_module, env_name)
    # # Initialiser l'environnement avec la configuration
    # env = env_class(config)
    # reward = 0
    # policy_network = reinforce(env, alpha=0.001, gamma=0.999, nb_episode=100)
    # env.play(policy_network)
    bond = Bond()
    policy_network = reinforce(bond, alpha=0.0001, gamma=0.999, nb_episode=1000)
    # Exemple de données factices (taille de batch 1)
    dummy_input = tf.random.uniform((1, policy_network.state_dim))

    # Passe avant pour construire le modèle
    policy_network(dummy_input)
    # save model
    policy_network.save('/home/leonard/Documents/PythonProjects/DeepReinforcement2/src/utils/policy_network_10000.keras')

    # load model
    #policy_network = PolicyNetwork.load('/home/leonard/Documents/PythonProjects/DeepReinforcement2/src/utils/policy_network.keras')
    #bond.play(policy_network)
