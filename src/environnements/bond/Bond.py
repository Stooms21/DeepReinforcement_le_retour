from PIL.ImageCms import Direction
from six import moves

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
        self.available_action = []
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
    def get_case(self,x,y):
        return self.get_plateau()[x][y]

    def check_piece_color(self, x, y):
        if self.get_case(x, y):
            return self.get_case(x, y).get_color() == self.get_turn()
        return None

    def get_turn(self):
        return self.move_state % 2

    def set_turn(self):
        self.move_state += 1
        self.move_state = self.move_state % 2

    def available_actions(self):
        total_moves = 8 * 16 + 16
        available_action = [0] * total_moves

        i = 0
        for y in range(self.x):
            for x in range(self.y):
                if not self.get_case(x, y):  # Si la case n'est pas vide
                    available_action[i] = 1
                i+=1


        directions = {'up': 0, 'down': 1, 'left': 2, 'right': 3, 'up2': 4, 'left2': 5, 'right2': 6, 'down2': 7}
        for x in range(self.x):
            for y in range(self.y):
                if self.get_case(x, y):
                    for direction, dir_idx in directions.items():
                        new_x, new_y = x, y
                        if direction == 'up':
                            new_y -= 1
                        elif direction == 'down':
                            new_y += 1
                        elif direction == 'left':
                            new_x -= 1
                        elif direction == 'right':
                            new_x += 1
                        elif direction == 'up2':
                            new_y -= 2
                        elif direction == 'left2':
                            new_x -= 2
                        elif direction == 'right2':
                            new_x += 2
                        elif direction == 'down2':
                            new_y += 2

                        # Vérifier si la nouvelle position est valide et vide
                        if 0 <= new_x < self.x and 0 <= new_y < self.y and self.check_piece_color(new_x, new_y):
                            self.available_action[i] = 1
                        i += 1

        return self.available_action

    def available_moves(self):
        i = 0
        available_move = []
        directions = {'up': 0, 'down': 1, 'left': 2, 'right': 3, 'up2': 4, 'left2': 5, 'right2': 6, 'down2': 7}
        for x in range(self.x):
            for y in range(self.y):
                for direction, dir_idx in directions.items():
                    new_x, new_y = x, y
                    if direction == 'up':
                        new_y -= 1
                    elif direction == 'down':
                        new_y += 1
                    elif direction == 'left':
                        new_x -= 1
                    elif direction == 'right':
                        new_x += 1
                    elif direction == 'up2':
                        new_y -= 2
                    elif direction == 'left2':
                        new_x -= 2
                    elif direction == 'right2':
                        new_x += 2
                    elif direction == 'down2':
                        new_y += 2
                    # Vérifier si la nouvelle position est valide et vide
                    if 0 <= new_x < self.x and 0 <= new_y < self.y and self.get_case(new_y, new_x) is None:
                        print(direction)
                        print(new_x, new_y)
                        print(self.get_case(new_x, new_y))
                        print(self.get_plateau()[x][y])
                        available_move.append(1)
                    else:
                        available_move.append(0)
                    i += 1


        return available_move

    def get_move_available(self,x,y):
        all_move = []
        move = self.available_moves()
        print(move)
        index_un = [i for i, val in enumerate(move) if val == 1]
        nb_case = x * self.y + y
        debut = nb_case * 8
        fin = debut + 8
        moves = move[debut:fin]
        return self.get_coordonnees_by_vector(moves,nb_case)

    def get_coordonnees_move(self,x,y):
        row = x
        col = y
        moves = []
        piece = self.get_case(row,col)
        if x - 1 >= 0:
            if self.get_case(row - 1, col) is None:
                moves.append(1)
            else:
                moves.append(0)
        else:
            moves.append(0)
        if x + 1 < self.x:
            if self.get_case(row + 1, col) is None:
                print(self.get_case(row + 1, col))
                moves.append(1)
            else:
                moves.append(0)
        else:
            moves.append(0)
        if y - 1 >= 0:
            if self.get_case(row, col - 1) is None:
                moves.append(1)
            else:
                moves.append(0)
        else:
            moves.append(0)
        if y + 1 < self.y:
            if self.get_case(row, col + 1) is None:
                moves.append(1)
            else:
                moves.append(0)
        else:
            moves.append(0)

        if x - 2 >= 0:
            if not self.get_case(row - 2, col) and piece.get_type() == 2:
                moves.append(1)
            else:
                moves.append(0)
        else:
            moves.append(0)
        if x + 2 < self.x:
            if not self.get_case(row + 2, col) and piece.get_type() == 2:
                moves.append(1)
            else:
                moves.append(0)
        else:
            moves.append(0)
        if y - 2 >= 0:
            if not self.get_case(row, col - 2) and piece.get_type() == 2:
                moves.append(1)
            else:
                moves.append(0)
        else:
            moves.append(0)
        if y + 2 < self.y:
            if not self.get_case(row, col + 2) and piece.get_type() == 2:
                moves.append(1)
            else:
                moves.append(0)
        else:
            moves.append(0)
        print(moves)
        coordonnees = []
        if piece:
            if moves[0] == 1:
                coordonnees.append((row - 1, col))
            if moves[1] == 1:
                coordonnees.append((row + 1, col))
            if moves[2] == 1:
                coordonnees.append((row, col - 1))
            if moves[3] == 1:
                coordonnees.append((row, col + 1))
            if moves[4] == 1:
                coordonnees.append((row - 2, col))
            if moves[5] == 1:
                coordonnees.append((row, col - 2))
            if moves[6] == 1:
                coordonnees.append((row, col + 2))
            if moves[7] == 1 :
                coordonnees.append((row + 2, col))
        print(coordonnees)
        return coordonnees

    def get_coordonnees_by_vector(self,moves,nb_case):
        row = nb_case // self.x
        col = nb_case % self.y
        piece = self.get_case(row,col)
        coordonnees = []
        if piece:
            if moves[0] == 1:
                coordonnees.append((row - 1, col))
            elif moves[1] == 1:
                coordonnees.append((row - 1, col))
            elif moves[2] == 1:
                coordonnees.append((row, col - 1))
            elif moves[3] == 1:
                coordonnees.append((row, col + 1))
            elif moves[4] == 1 and piece.get_type() == 2:
                coordonnees.append((row - 2, col))
            elif moves[5] == 1 and piece.get_type() == 2:
                coordonnees.append((row, col - 2))
            elif moves[6] == 1 and piece.get_type() == 2:
                coordonnees.append((row, col + 2))
            elif moves[7] == 1 and piece.get_type() == 2:
                coordonnees.append((row + 2, col))
        return coordonnees

    def reset(self):
        self.plateau = [[None for _ in range(self.x)] for _ in range(self.y)]
        self.piece_to_delete = []
        self.players = [Player(0), Player(1)]
        self.move_state = 0

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
