import numpy as np
import torch


class LineWorld:
    def __init__(self, config):
        self.size = config['size']
        self.actions = config['actions']
        self.rewards = config['rewards']
        self.terminals = config['terminals']
        self.scored = 0
        self.player_position = self.size // 2  # Start state

    def reset(self):
        self.player_position = self.size // 2  # Start state
        return self.player_position

    def num_actions(self) -> int:
        return len(self.actions)

    def num_rewards(self) -> int:
        return len(self.rewards)

    def reward(self, i: int) -> float:
        return self.rewards[i]

    def display(self):
        lineworld = ['_' for _ in range(self.size)]
        lineworld[self.player_position] = 'X'
        print("".join(lineworld))

    def is_forbidden(self, action: int) -> int:
        return not action in self.actions

    def is_game_over(self) -> bool:
        is_end = self.player_position in self.terminals
        return is_end

    def step(self, action: int):
        if action == 1:
            self.player_position += 1
        if action == 0:
            self.player_position -= 1

    def score(self):
        if self.player_position == self.terminals[0]:
            self.scored = self.rewards[0]
        elif self.player_position == self.terminals[1]:
            self.scored = self.rewards[2]
        else:
            self.scored = self.rewards[1]
        return self.scored

    def available_actions(self):
        return self.actions

    def one_hot_state_desc(self):
        # La description de l'état se fait en retournant un vecteur one-hot dans lequel
        # la position du joueur est à 1 et les autres positions sont à 0
        return torch.tensor([1 if i == self.player_position else 0 for i in range(self.size)], dtype=torch.float32)

    def get_one_hot_size(self):
        return self.one_hot_state_desc().numel()

    def play(self, policy_network):
        # Réinitialisation de l'environnement
        self.reset()
        total_reward = 0
        steps = 0

        # Boucle jusqu'à la fin de la partie
        while not self.is_game_over():
            # Affichage de l'état actuel
            self.display()
            # Obtention de la description de l'état courant
            s = torch.tensor(self.one_hot_state_desc(), dtype=torch.float32)
            # Calcul des valeurs Q pour l'état courant
            q_values = policy_network.forward(s).detach().numpy()
            # Sélection des actions disponibles
            available_actions = self.available_actions()
            # Filtrage des valeurs Q pour les actions disponibles
            q_values_available = q_values[available_actions]
            # Sélection de l'action avec la valeur Q maximale parmi les actions disponibles
            a = available_actions[np.argmax(q_values_available)]
            # Exécution de l'action dans l'selfironnement
            self.step(a)
            # Obtention de la récompense
            reward = self.score()
            total_reward += reward
            steps += 1

        # Affichage de l'état final
        self.display()
        print(f"Partie terminée en {steps} étapes avec une récompense totale de {total_reward}.")
        return total_reward