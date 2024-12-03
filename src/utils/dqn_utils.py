import numpy as np
import torch


def choose_epsilon_greedy_action(
        policy_network,
        s,
        available_actions, epsilon
):
    if np.random.rand() < epsilon:
        a = np.random.choice(available_actions)
    else:
        q_values = policy_network(s).detach().numpy()
        a = np.argmax(q_values)
        if a in available_actions:
            return a
        else:
            a = np.random.choice(available_actions)
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
        available_actions_prime=None
):
    if not env.is_game_over():
        if target_network is not None:
            q_values_prime = target_network.forward(s_prime).detach().numpy()
        else:
            q_values_prime = policy_network.forward(s_prime).detach().numpy()
        mask = np.zeros_like(q_values_prime[0])
        mask[available_actions_prime] = 1
        q_values_prime_masked = q_values_prime[0] * mask

        if q_values_prime_masked.sum() == 0:
            a = np.random.choice(available_actions_prime)
        else:
            q_values_prime_masked /= q_values_prime_masked.sum()
        q_target = reward + gamma * np.max(q_values_prime_masked)
    else:
        q_target = reward

    # Calcul de la prédiction actuelle Q(s, a)
    q_values_current = policy_network.forward(s)
    q_value = q_values_current[0, a]

    return q_value, q_target


def observe_R_S_prime(env, a):
    player = env.get_curr_player().color
    color = 1
    if player == 1:
        color = -1
    prev_score = env.score() * color
    env.step(a)
    new_score = env.score() * color

    reward = new_score - prev_score
    s_prime = torch.tensor(env.one_hot_state_desc().flatten(), dtype=torch.float32).unsqueeze(0)
    available_actions_prime = env.available_actions()
    return reward, s_prime, available_actions_prime