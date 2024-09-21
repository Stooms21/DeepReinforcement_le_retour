from collections import namedtuple
import numpy as np


class LineWorld:
    def __init__(self, config):
        self.states = config['states']
        self.actions = config['actions']
        self.rewards = config['rewards']
        self.terminals = config['terminals']
        self.scored = 0
        self.state = 2
        self.action_space = namedtuple('ActionSpace', ['n'])
        self.action_space.n = len(self.actions)

    def reset(self):
        self.state = 2  # Start state
        return self.state

    def num_states(self) -> int:
        return len(self.states)

    def num_actions(self) -> int:
        return len(self.actions)

    def num_rewards(self) -> int:
        return len(self.rewards)

    def reward(self, i: int) -> float:
        return self.rewards[i]

    # Monte Carlo and TD Methods related functions:
    def state_id(self) -> int:
        return self.state

    def display(self):
        lineworld = ['_' for _ in range(5)]
        lineworld[self.state] = 'X'
        print("".join(lineworld))

    def is_forbidden(self, action: int) -> int:
        return not action in self.actions

    def is_game_over(self) -> bool:
        is_end = self.state in self.terminals
        return is_end

    def step(self, action: int):
        if action == 1:
            self.state += 1
        if action == 0:
            self.state -= 1
    def score(self):
        if self.state == 4:
            self.scored = self.rewards[2]
        if self.state == 0:
            self.scored = self.rewards[0]
        return self.scored

    def available_actions(self):
        return self.actions