from Player import Player
from config.bond_config import ROWS, COLS


class Bond:
    def __init__(self, x=ROWS, y=COLS):  # Use ROWS and COLS from bond_config
        self.x = x
        self.y = y
        self.plateau = [[None for _ in range(self.x)] for _ in range(self.y)]
        self.pieces = []
        self.players = [Player("blanc"), Player("noir")]
        self.move_state = 0  # no color 0, highlighted in blue 1, highlighted in yellow 2

    def get_x(self):
        return self.x

    def set_x(self, x):
        self._x = x

    # Getter et Setter pour y
    def get_y(self):
        return self.y

    def set_y(self, y):
        self._y = y

    # Getter et Setter pour plateau
    def get_plateau(self):
        return self.plateau

    def set_plateau(self, plateau):
        self._plateau = plateau

    # Getter et Setter pour pieces
    def get_pieces(self):
        return self.pieces

    def set_pieces(self, pieces):
        self._pieces = pieces

    # Getter et Setter pour players
    def get_players(self):
        return self.players

    def set_players(self, players):
        self._players = players

    # Getter et Setter pour move_state
    def get_move_state(self):
        return self.move_state

    def set_move_state(self, move_state):
        self.move_state = move_state

    def placer_pion(self, ligne, colonne, piece):

        if 0 <= ligne < self.x and 0 <= colonne < self.y:
            if self.plateau[ligne][colonne] is None:
                self.plateau[ligne][colonne] = piece
                return True
            else:
                return False
        else:
            return False

