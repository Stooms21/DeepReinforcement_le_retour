class GridWorld:
    def __init__(self, config):
        self.size = (config['size'], config['size'])
        self.actions = config['actions']
        self.rewards = config['rewards']
        self.terminals = config['terminals']
        self.scored = 0
        self.player_position = self.size[0] * self.size[1] // 2  # Start state

    def reset(self):
        self.player_position = self.size[0] * self.size[1] // 2  # Start state
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
        grid = ['_' for _ in range(self.size[0] * self.size[1])]
        # Marquer les bords de la grille avec 'X'
        for s in range(self.size[0] * self.size[1]):
            if s in self.terminals:
                grid[s] = 'X'
            if s == 18:
                grid[s] = '0'
        grid[self.player_position] = 'P'
        # Affichage de la grille
        for i in range(self.size[1]):
            print(" ".join(grid[i * self.size[0]:(i + 1) * self.size[0]]))
        print("\n")

    def is_forbidden(self, action: int) -> int:
        return not action in self.actions

    def step(self, action: int):
        if action == 0:
            self.player_position -= 1
        if action == 1:
            self.player_position += 1
        if action == 2:
            self.player_position += self.size[0]
        if action == 3:
            self.player_position -= self.size[0]


    def score(self):
        if self.player_position in self.terminals and self.player_position == 18:
            self.scored = self.rewards[2]
        elif self.player_position in self.terminals and self.player_position != 18:
            self.scored = self.rewards[0]
        else:
            self.scored = self.rewards[1]
        return self.scored

    def one_hot_state_desc(self):
        state_desc = [0] * (self.size[0] * self.size[1])
        state_desc[self.player_position] = 1
        return state_desc

    def available_actions(self):
        return self.actions