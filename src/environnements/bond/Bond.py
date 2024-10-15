from Player import Player
from config.bond_config import ROWS, COLS
import Piece as p
import numpy as np

class Bond:
    def __init__(self, x=ROWS, y=COLS):  # Use ROWS and COLS from bond_config
        self.x = x
        self.y = y
        self.plateau = [[None for _ in range(self.x)] for _ in range(self.y)]
        self.piece_to_delete = []
        self.players = [Player(0), Player(1)]
        self.move_state = 0  # no color p1 0,no color p2 1 highlighted in yellow p1 2, highlighted in yellow p2 3
        self.aa = np.zeros(144).astype(int)
        self.all_actions = np.zeros(144)
        self.winners = []
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

    def get_winners(self):
        return self.winners

    def add_winner(self, winner):
        self.winners.append(winner)

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

    def set_case(self,Piece,x,y):
        self.get_plateau()[x][y] = Piece

    def check_piece_color(self, x, y):
        if self.plateau[x][y]:
            return self.plateau[x][y].get_color() == self.get_turn()
        return None

    def get_turn(self):
        return self.move_state % 2

    def set_turn(self):
        self.move_state += 1
        self.move_state = self.move_state % 2

    def available_action(self):
        return self.aa

    def update_available_actions(self):
        self.aa = np.zeros(144)
        i = 0
        for x in range(self.x):
            for y in range(self.y):
                if not self.plateau[x][y] and self.players[self.get_turn()].get_nbPieceRestante() >0 :  # Si la case n'est pas vide
                    self.aa[i] = 1
                i+=1


        directions = {'up': 0, 'down': 1, 'left': 2, 'right': 3, 'up2': 4, 'down2': 5, 'left2': 6, 'right2': 7}

        for x in range(self.x):
            for y in range(self.y):
                curr_type = 1
                for direction, dir_idx in directions.items():
                    new_x, new_y = x, y
                    if direction == 'up':
                        new_x -= 1
                    elif direction == 'down':
                        new_x += 1
                    elif direction == 'left':
                        new_y -= 1
                    elif direction == 'right':
                        new_y += 1
                    elif direction == 'up2':
                        new_x -= 2
                        curr_type = 2
                    elif direction == 'down2':
                        new_x += 2
                    elif direction == 'left2':
                        new_y -= 2
                    elif direction == 'right2':
                        new_y += 2
                    condition = True
                    if curr_type == 2 and self.plateau[x][y]:
                        condition = curr_type == self.get_case(x, y).get_type()
                    # Vérifier si la nouvelle position est valide et vide et que la piece courante est de la couleur du joueur courant
                    if 0 <= new_x < self.x and 0 <= new_y < self.y and not self.plateau[new_x][new_y] and self.check_piece_color(x, y) and condition:
                        self.aa[i] = 1
                    i += 1
        self.all_actions = self.aa
        self.aa = np.where(self.aa == 1)[0]

    def get_move_available(self,x,y):
        move = self.all_actions
        nb_case = x * self.x + y
        debut = nb_case * 8
        fin = debut + 8
        moves = move[debut + 16 :fin + 16]
        return self.get_coordonnees_by_vector(moves,nb_case)

    def step(self,action):
        if action<=15 :
            row = action // self.x
            col = action % self.y
            self.placer_pion(row,col,p.Piece(row,col,self.get_turn()))
            self.update_board(row,col)
        else:
            action -= 16
            nb_cases = action // 8
            row = nb_cases // self.x
            col = nb_cases % self.y
            piece = self.get_case(row,col)
            self.set_case(piece,row,col)
            row,col = self.get_direction(nb_cases,row,col)
            self.placer_pion(row,col,piece)
            self.update_board(row,col)

    def get_direction(self,index,row,col):
        directions = {'up': 0, 'down': 1, 'left': 2, 'right': 3, 'up2': 4, 'down2': 5, 'left2': 6, 'right2': 7}
        new_x, new_y = row, col

        for direction, dir_idx in directions.items():
            if dir_idx == index:
                new_x -= 1
            elif dir_idx == index:
                new_x += 1
            elif dir_idx == index:
                new_y -= 1
            elif dir_idx == index:
                new_y += 1
            elif dir_idx == index:
                new_x -= 2
            elif dir_idx == index:
                new_x += 2
            elif dir_idx == index:
                new_y -= 2
            elif dir_idx == index:
                new_y += 2

        return new_x, new_y

    def update_board(self,x,y):
        self.get_curr_player().set_nbPieceRestante()
        self.check_piece_to_develop(x, y)
        self.set_turn()
        self.update_available_actions()

    def get_coordonnees_by_vector(self,moves,nb_case):
        row = nb_case // self.x
        col = nb_case % self.y
        piece = self.get_case(row,col)
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
            if moves[4] == 1 and piece.get_type() == 2:
                coordonnees.append((row - 2, col))
            if moves[5] == 1 and piece.get_type() == 2:
                coordonnees.append((row + 2,col))
            if moves[6] == 1 and piece.get_type() == 2:
                coordonnees.append((row, col - 2))
            if moves[7] == 1 and piece.get_type() == 2:
                coordonnees.append((row, col + 2))
        return coordonnees

    def reset(self):
        self.plateau = [[None for _ in range(self.x)] for _ in range(self.y)]
        self.piece_to_delete = []
        self.players = [Player(0), Player(1)]
        self.move_state = 0

    def is_game_over(self):
        game_over = False
        for player in self.players:
            if player.get_nbPieceSortis() >= 10:
                #print("gagné par pièce sortis")
                self.add_winner(player.get_color())
                game_over = True
            elif player.get_nbPieceRestante() == 0:
                #print("perdu par manque de pièce")
                self.add_winner((player.get_color() + 1) %2)
                game_over = True

        curr_player = self.get_curr_player()

        if not self.aa.size == 0:
            if curr_player not in self.winners:
                #print("perdu par manque de coup")
                self.add_winner(curr_player.get_color())

        #if len(self.winners) == 2:
            #print("c'est égalité")

        return game_over or self.aa.size == 0

    def score(self):
        if self.is_game_over():
            if 0 in self.winners:
                if len(self.winners) == 2:
                    return 0.5
                return 1
            else:
                return 0
        else:
            return 0
    def get_curr_player(self):
        return self.players[self.get_turn()]

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
