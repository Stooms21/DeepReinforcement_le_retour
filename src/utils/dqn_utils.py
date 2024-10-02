import numpy as np


def choose_epsilon_greedy_action(
        policy_network,
        s,
        available_actions, epsilon
):
    if np.random.rand() < epsilon:
        a = np.random.choice(available_actions)
    else:
        q_values = policy_network(s).detach().numpy()
        a = available_actions[np.argmax(q_values)]
    return a


def compute_q_values_and_q_target(
        env,
        policy_network,
        s,
        s_prime,
        a,
        gamma,
        reward,
        target_network=None,
):
    if not env.is_game_over():
        if target_network is not None:
            q_values_prime = target_network.forward(s_prime).detach().numpy()
        else:
            q_values_prime = policy_network.forward(s_prime).detach().numpy()
        q_target = reward + gamma * np.max(q_values_prime)
    else:
        q_target = reward

    # Calcul de la prédiction actuelle Q(s, a)
    q_values_current = policy_network.forward(s)
    q_value = q_values_current[a]

    return q_value, q_target


def observe_R_S_prime(env, a):
    prev_score = env.score()
    env.step(a)
    new_score = env.score()
    reward = new_score - prev_score
    s_prime = env.one_hot_state_desc()
    available_actions_prime = env.available_actions()
    return reward, s_prime, available_actions_prime