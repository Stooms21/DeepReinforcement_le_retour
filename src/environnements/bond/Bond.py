from Player import Player
from config.bond_config import ROWS, COLS

import Piece

class Bond:
    def __init__(self, x=ROWS, y=COLS):  # Use ROWS and COLS from bond_config
        self.x = x
        self.y = y
        self.plateau = [[None for _ in range(self.x)] for _ in range(self.y)]
        self.piece_to_delete = []
        self.players = [Player(0), Player(1)]
        self.move_state = 0  # no color p1 0,no color p2 1 highlighted in yellow p1 2, highlighted in yellow p2 3

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

    def placer_pion(self, x, y, piece):

        if 0 <= x < self.x and 0 <= y < self.y:
            if self.plateau[x][y] is None:
                self.plateau[x][y] = piece
                return True
            else:
                return False
        else:
            return False

    def check_is_game_over(self):
        game_over = False
        for player in self.players:
            if player.get_nbPieceSortis() >= 10:
                print(f'{player.color} a gagné ')
                game_over = True
        return game_over
    def check_piece_to_develop(self,x,y):
        if x - 1 >= 0:
            if self.plateau[x - 1][y]:
                piece = self.plateau[x - 1][y]
                self.plateau[x - 1][y] = self.develop_piece(piece)
        if x + 1 < self.x:
            if self.plateau[x + 1][y]:
                piece = self.plateau[x + 1][y]
                self.plateau[x + 1][y] = self.develop_piece(piece)
        if y - 1 >= 0:
            if self.plateau[x][y - 1]:
                piece = self.plateau[x][y - 1]
                self.plateau[x][y - 1] = self.develop_piece(piece)
        if y + 1 < self.y:
            if self.plateau[x][y + 1]:
                piece = self.plateau[x][y + 1]
                self.plateau[x][y + 1] = self.develop_piece(piece)

    def develop_piece(self,piece):
        piece.set_type((piece.get_type() + 1)%3)
        return piece

    def check_piece_to_scored(self):
        self.piece_to_delete = []
        self.check_row()
        self.check_col()

        for piece in self.piece_to_delete: #supprime les rangées
            row = piece.get_pos_x()
            col = piece.get_pos_y()
            color = piece.get_color()
            nbPieceSortis = self.players[color % 2].get_nbPieceSortis()
            self.players[color % 2].set_nbPieceSortis(nbPieceSortis + 1)
            self.plateau[row][col] = None
    def check_row(self):
        for row in self.plateau:
            lst = []
            for case in row:
                if case: #si c'est une piece
                    if not lst: #si la liste est vide
                        lst.append(case)
                    elif lst[-1].get_type() == case.get_type(): #si c'est du même type
                        lst.append(case)
                    else:
                        if len(lst) < 3:
                            lst.clear()
                            lst.append(case)
                else:
                    if len(lst) < 3:
                        lst.clear()


            if len(lst) >=3:
                for element in lst:
                    if element not in self.piece_to_delete:
                        self.piece_to_delete.append(element)

    def check_col(self):
        for col in range(self.y):
            lst = []
            for row in range(self.x):
                case = self.plateau[row][col]
                if case:  # si c'est une piece
                    if not lst:  # si la liste est vide
                        lst.append(case)
                    elif lst[-1].get_type() == case.get_type():  # si c'est du même type
                        lst.append(case)
                    else:
                        lst.clear()
                        lst.append(case)
                else:
                    lst.clear()
                if len(lst) >= 3:
                    for element in lst:
                        if element not in self.piece_to_delete:
                            self.piece_to_delete.append(element)
