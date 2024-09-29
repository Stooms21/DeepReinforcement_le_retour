import src.environnements.lineworld as lw
import src.environnements.gridworld as gw
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import utils as ut
import tqdm


congig_file = "../../config/config.yaml"


# Create pytorch neural network
class QNet(nn.Module):
    def __init__(self, num_states_description, num_actions):
        super(QNet, self).__init__()
        self.input_layer = nn.Linear(num_states_description, 128)
        self.hidden1 = nn.Linear(128, 128)
        self.hidden2 = nn.Linear(128, 128)
        self.output_layer = nn.Linear(128, num_actions)

    def forward(self, x):
        # Propagation vers l'avant avec une fonction d'activation ReLU
        x = torch.relu(self.input_layer(x))
        x = torch.relu(self.hidden1(x))
        x = torch.relu(self.hidden2(x))
        x = self.output_layer(x)  # Pas d'activation sur la sortie (pour régression)
        return x


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
    input_layer_size = len(env.one_hot_state_desc())
    output_layer_size = env.num_actions()
    policy_network = QNet(input_layer_size, output_layer_size)

    criterion = nn.MSELoss()  # Pour une tâche de régression
    optimizer = optim.Adam(policy_network.parameters(), lr=alpha)

    # Loop for each episode

    for _ in tqdm.tqdm(range(nb_episode)):
        #Initialize S
        env.reset()
        # Loop for each step epiosde
        while not env.is_game_over():
            s = torch.tensor(env.one_hot_state_desc(), dtype=torch.float32)
            available_actions = env.available_actions()

            if np.random.rand() < epsilon:
                a = np.random.choice(available_actions)
            else:
                q_values = policy_network(s).detach().numpy()
                a = available_actions[np.argmax(q_values)]

            reward, s_prime, available_actions_prime = ut.observe_R_S_prime(env, a)

            if not env.is_game_over():
                q_values_prime = policy_network(torch.tensor(s_prime, dtype=torch.float32)).detach().numpy()
                q_target = reward + gamma * np.max(q_values_prime)
            else:
                q_target = reward

            # Calcul de la prédiction actuelle Q(s, a)
            q_values_current = policy_network(s)
            q_value = q_values_current[a]

            # Calcul de la perte L
            loss = criterion(q_value, torch.tensor(q_target, dtype=torch.float32))

            # Mise à jour des poids du réseau par rétropropagation
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        epsilon = max(epsilon_min, epsilon * epsilon_decay)

    return policy_network


def play_lineworld(env, policy_network):
    # Réinitialisation de l'environnement
    env.reset()
    total_reward = 0
    steps = 0

    # Boucle jusqu'à la fin de la partie
    while not env.is_game_over():
        # Affichage de l'état actuel
        env.display()

        # Obtention de la description de l'état courant
        s = torch.tensor(env.one_hot_state_desc(), dtype=torch.float32)

        # Calcul des valeurs Q pour l'état courant
        q_values = policy_network(s).detach().numpy()

        # Sélection des actions disponibles
        available_actions = env.available_actions()

        # Filtrage des valeurs Q pour les actions disponibles
        q_values_available = q_values[available_actions]

        # Sélection de l'action avec la valeur Q maximale parmi les actions disponibles
        a = available_actions[np.argmax(q_values_available)]

        # Exécution de l'action dans l'environnement
        env.step(a)

        # Obtention de la récompense
        reward = env.score()
        total_reward += reward
        steps += 1

    # Affichage de l'état final
    env.display()
    print(f"Partie terminée en {steps} étapes avec une récompense totale de {total_reward}.")
    return total_reward


def play_gridworld(env, policy_network):
    env.reset()
    total_reward = 0
    steps = 0

    while not env.is_game_over():
        env.display()
        s = torch.tensor(env.one_hot_state_desc(), dtype=torch.float32)
        q_values = policy_network(s).detach().numpy()
        a = np.argmax(q_values)
        env.step(a)
        reward = env.score()
        total_reward += reward
        steps += 1

    env.display()
    print(f"Partie terminée en {steps} étapes avec une récompense totale de {total_reward}.")
    return total_reward


if __name__ == "__main__":
    config = ut.load_config(congig_file, "GridWorld")
    env = gw.GridWorld(config)
    reward = 0
    print(env.one_hot_state_desc())
    for i in range(10):
        env.reset()
        policy_network = deep_q_learning(env)
        reward += play_gridworld(env, policy_network)
        print(f"Reward moyen: {reward / 10}")
