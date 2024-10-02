from src.utils import utils as ut
import src.utils.dqn_utils as dqu
import tqdm
import models
from config.config import CONFIG_FILE, DQN_HIDDEN_LAYER_SIZE, ENV_MODULE_MAPPING


def deep_q_learning(
        env,
        alpha: float = 0.0001,
        epsilon: float = 1.0,
        epsilon_min: float = 0.01,
        epsilon_decay: float = 0.995,
        gamma: float = 0.999,
        nb_episode: int = 1000,
):
    # Initialize Q(s,a) arbitrarily
    input_layer_size = env.get_one_hot_size()
    output_layer_size = env.num_actions()
    policy_network = models.QNet(input_layer_size, output_layer_size, DQN_HIDDEN_LAYER_SIZE)

    # Loop for each episode
    for _ in tqdm.tqdm(range(nb_episode)):
        #Initialize S
        env.reset()
        # Loop for each step epiosde
        while not env.is_game_over():
            s = env.one_hot_state_desc()
            available_actions = env.available_actions()

            # Choose A from S using policy derived from Q
            a = dqu.choose_epsilon_greedy_action(policy_network, s, available_actions, epsilon)

            # Take action A, observe R, S'
            reward, s_prime, available_actions_prime = dqu.observe_R_S_prime(env, a)

            # Compute Q(s,a) and Q_target
            q_value, q_target = dqu.compute_q_values_and_q_target(env, policy_network, s, s_prime, a, gamma, reward)

            # Update Q(s,a)
            policy_network.backward(q_value, q_target)

        # epsilon decay
        epsilon = max(epsilon_min, epsilon * epsilon_decay)

    return policy_network


if __name__ == "__main__":
    env_name = "GridWorld"
    config = ut.load_config(CONFIG_FILE, env_name)
    env_module = ENV_MODULE_MAPPING[env_name]
    env_class = getattr(env_module, env_name)
    env = env_class(config)
    reward = 0
    for i in range(1, 11):
        env.reset()
        policy_network = deep_q_learning(env)
        reward += env.play(policy_network)
        print(f"Reward moyen: {reward / i} sur {i} parties")
