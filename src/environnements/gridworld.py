import numpy as np
import torch


class GridWorld:
    def __init__(self, config):
        self.size = config['size']
        self.actions = config['actions']
        self.rewards = config['rewards']
        self.terminals = config['terminals']
        self.scored = 0
        self.player_position = 6  # Start state

    def reset(self):
        self.player_position = 6  # Start state
        return self.player_position

    def num_actions(self) -> int:
        return len(self.actions)

    def num_rewards(self) -> int:
        return len(self.rewards)

    def reward(self, i: int) -> float:
        return self.rewards[i]

    def is_game_over(self) -> bool:
        is_end = self.player_position in self.terminals
        return is_end

    def display(self):
        grid = ['_' for _ in range(self.size**2)]
        # Marquer les bords de la grille avec 'X'
        for s in range(self.size**2):
            if s in self.terminals:
                grid[s] = 'X'
            if s == 18:
                grid[s] = '0'
        grid[self.player_position] = 'P'
        # Affichage de la grille
        for i in range(self.size):
            print(" ".join(grid[i * self.size: (i + 1) * self.size]))
        print("\n")

    def is_forbidden(self, action: int) -> int:
        return not action in self.actions

    def step(self, action: int):
        if action == 0:
            self.player_position -= 1
        if action == 1:
            self.player_position += 1
        if action == 2:
            self.player_position += self.size
        if action == 3:
            self.player_position -= self.size


    def score(self):
        if self.player_position in self.terminals and self.player_position == 18:
            self.scored = self.rewards[2]
        elif self.player_position in self.terminals and self.player_position != 18:
            self.scored = self.rewards[0]
        else:
            self.scored = self.rewards[1]
        return self.scored

    def one_hot_state_desc(self):
        state_desc = [0] * (self.size * self.size)
        state_desc[self.player_position] = 1
        return state_desc

    def get_one_hot_size(self):
        return len(self.one_hot_state_desc())

    def play(env, policy_network):
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

    def available_actions(self):
        return self.actions