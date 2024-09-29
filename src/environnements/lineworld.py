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
        if self.player_position == self.terminals[1]:
            self.scored = self.rewards[2]
        return self.scored

    def available_actions(self):
        return self.actions

    def one_hot_state_desc(self):
        # La description de l'état se fait en retournant un vecteur one-hot dans lequel
        # la position du joueur est à 1 et les autres positions sont à 0
        return [1 if i == self.player_position else 0 for i in range(self.size)]