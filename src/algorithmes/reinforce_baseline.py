from config.algos_config import CONFIG_FILE, ENV_MODULE_MAPPING
from src.utils.utils import load_config
from src.utils.dqn_utils import observe_R_S_prime
from src.algorithmes.models import PolicyNetworkReinforce, ValueNetwork
import numpy as np
from tqdm import tqdm
import tensorflow as tf
from src.environnements.bond.Bond import Bond


def reinforce_with_baseline(
        env,
        alpha_theta: float = 0.0001,
        alpha_w: float = 0.0001,
        gamma: float = 0.999,
        nb_episode: int = 100,
):
    """
    Implémentation de l'algorithme REINFORCE avec baseline.
    """

    # Initialisation des réseaux
    input_layer_size = env.get_one_hot_size()
    output_layer_size = env.num_actions()
    policy_network = PolicyNetworkReinforce(input_layer_size, output_layer_size, alpha=alpha_theta)
    value_network = ValueNetwork(input_layer_size, alpha=alpha_w)

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
        rewards = np.array(rewards, dtype=np.float32)
        discount_factors = np.power(gamma, np.arange(len(rewards)))
        returns = np.cumsum(rewards[::-1] * discount_factors[::-1])[::-1]

        # Mise à jour des paramètres pour chaque étape de l'épisode
        for t, (state, action, G_t) in enumerate(zip(states, actions, returns)):
            # Calcul de la valeur estimée et de l'avantage
            value_estimate = value_network.call(state)[0, 0].numpy()
            advantage = G_t - value_estimate

            # Mise à jour du réseau de valeur
            value_network.train_step(state, G_t)

            # Mise à jour du réseau de politique
            policy_network.train_step(state, action, advantage)

    return policy_network


if __name__ == "__main__":
    bond = Bond()
    policy_network = reinforce_with_baseline(bond, alpha_theta=0.001, alpha_w=0.001, gamma=0.999, nb_episode=1)
    # Exemple de données factices (taille de batch 1)
    dummy_input = tf.random.uniform((1, policy_network.state_dim))

    # Passe avant pour construire le modèle
    policy_network(dummy_input)
    # save model
    policy_network.save(
        '../utils/policy_network_reinforce_baseline_1000.keras')
