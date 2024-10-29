import torch
from src.environnements.bond.Player import Player
from config.bond_config import ROWS, COLS
import src.environnements.bond.Piece as p
import numpy as np
import random
import copy
from src.algorithmes.utc import utc

class Bond:
    def __init__(self,plateau = np.full((4,4), None)):
        self.x = 4
        self.y = 4
        self.plateau = plateau
        self.piece_to_delete = []
        self.players = [Player(0), Player(1)]
        self.aa = np.zeros(144).astype(int)
        self.all_actions = np.zeros(144).astype(int)
        self.winners = []
        self.turn = 0

    def add_winner(self, winner):
        self.winners.append(winner)

    def placer_pion(self, x, y, piece):

        if 0 <= x < self.x and 0 <= y < self.y:
            if self.plateau[x, y] is None:
                self.plateau[x, y] = piece
                return True
            else:
                return False
        else:
            return False

    def set_case(self,Piece,x,y):
        self.plateau[x,y] = Piece

    def check_piece_color(self, x, y):
        piece = self.plateau[x, y]
        if piece:
            return piece.get_color() == self.get_turn()
        return None

    def get_turn(self):
        return self.turn

    def set_turn(self):
        self.turn += 1
        self.turn = self.turn % 2

    def available_actions(self):
        return self.all_actions

    def available_actions_ids(self):
        return self.aa

    def num_actions(self):
        return len(self.all_actions)

    def update_available_actions(self):
        aa = []
        i = 0
        for x in range(self.x):
            for y in range(self.y):
                if not self.plateau[x, y]:  # Si la case n'est pas vide
                    aa.append(i)
                i+=1


        directions = {'up': 0, 'down': 1, 'left': 2, 'right': 3, 'up2': 4, 'down2': 5, 'left2': 6, 'right2': 7}

        for x in range(self.x):
            for y in range(self.y):
                if self.check_piece_color(x, y):
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
                        type_condition = curr_type == self.plateau[x,y].get_type() or  self.plateau[x,y].get_type() == 2
                        # Vérifier si la nouvelle position est valide et vide et que la piece courante est de bon type
                        if 0 <= new_x < self.x and 0 <= new_y < self.y and not self.plateau[new_x, new_y] and type_condition:
                           aa.append(i)
                        i += 1
                else:
                    i+=8
        self.aa = np.array(aa)  # Conversion en tableau numpy une fois terminé
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
            piece_type = self.plateau[row,col].get_type()
            self.set_case(None,row,col)
            move = action % 8
            row,col = self.get_direction(move,row,col)
            self.placer_pion(row,col,p.Piece(row,col,self.get_turn(),piece_type))
            self.update_board(row,col)

    def get_direction(self,index,row,col):
        new_x, new_y = row, col
        if 0 == index:
            new_x -= 1
        elif 1 == index:
            new_x += 1
        elif 2 == index:
            new_y -= 1
        elif 3 == index:
            new_y += 1
        elif 4 == index:
            new_x -= 2
        elif 5 == index:
            new_x += 2
        elif 6 == index:
            new_y -= 2
        elif 7 == index:
            new_y += 2

        return new_x, new_y

    def update_board(self,x,y):
        self.get_curr_player().set_nbPieceRestante()
        self.check_piece_to_develop(x, y)
        self.set_turn()
        self.check_piece_to_scored()
        self.update_available_actions()

    def reset(self):
        self.plateau = np.full((self.y, self.x), None)
        self.piece_to_delete = []
        self.players = [Player(0), Player(1)]
        self.move_state = 0  # no color p1 0,no color p2 1 highlighted in yellow p1 2, highlighted in yellow p2 3
        self.aa = np.zeros(144).astype(int)
        self.all_actions = np.zeros(144).astype(int)
        self.winners = []

    def is_game_over(self):
        game_over = False
        for player in self.players:
            if player.get_nbPieceSortis() >= 10:
                self.add_winner(player.get_color())
                game_over = True
            elif player.get_nbPieceRestante() == 0:
                self.add_winner((player.get_color() + 1) %2)
                game_over = True

        curr_player = self.get_curr_player()
        if self.aa.size == 0:
            if curr_player not in self.winners:
                self.add_winner(curr_player.get_color())
                game_over = True


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
            if self.plateau[x - 1,y]:
                piece = self.plateau[x - 1,y]
                self.plateau[x - 1,y] = self.develop_piece(piece)
        if x + 1 < self.x:
            if self.plateau[x + 1,y]:
                piece = self.plateau[x + 1,y]
                self.plateau[x + 1,y] = self.develop_piece(piece)
        if y - 1 >= 0:
            if self.plateau[x,y - 1]:
                piece = self.plateau[x,y - 1]
                self.plateau[x,y - 1] = self.develop_piece(piece)
        if y + 1 < self.y:
            if self.plateau[x,y + 1]:
                piece = self.plateau[x,y + 1]
                self.plateau[x,y + 1] = self.develop_piece(piece)

    def develop_piece(self,piece):
        piece.set_type((piece.get_type() + 1)%3)
        return piece

    def check_piece_to_scored(self):
        self.piece_to_delete = []
        self.check_row()
        self.check_col()
        for piece in self.piece_to_delete: #supprime les rangées
            row = piece[0]
            col = piece[1]
            color = piece[2]
            nbPieceSortis = self.players[color % 2].get_nbPieceSortis()
            for player in self.players:
                if player.get_color() == color:
                    player.set_nbPieceSortis(nbPieceSortis + 1)
            self.plateau[row,col] = None
        score = (self.players[0].get_nbPieceSortis() ,  self.players[1].get_nbPieceSortis())

    def check_row(self):
        for x in range(self.x):
            lst = []
            type = 0
            for y in range(self.y):
                piece = self.plateau[x,y]
                if piece: #si c'est une piece
                    x = piece.get_pos_x()
                    y = piece.get_pos_y()
                    color = piece.get_color()
                    if not lst: #si la liste est vide
                        lst.append((x,y,color))
                        type = piece.get_type()
                    elif type == piece.get_type(): #si c'est du même type
                        lst.append((x,y,color))
                    else:
                        if len(lst) < 3:
                            lst.clear()
                            lst.append((x,y,color))
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
                piece = self.plateau[row,col]
                if piece:  # si c'est une piece
                    x = piece.get_pos_x()
                    y = piece.get_pos_y()
                    color = piece.get_color()
                    if not lst:  # si la liste est vide
                        lst.append((x,y,color))
                        type = piece.get_type()
                    elif type == piece.get_type():  # si c'est du même type
                        lst.append((x,y,color))
                    else:
                        lst.clear()
                        lst.append((x,y,color))
                else:
                    lst.clear()
                if len(lst) >= 3:
                    for element in lst:
                        if element not in self.piece_to_delete:
                            self.piece_to_delete.append(element)

    def copy(self):
        return copy.deepcopy(self)

    def play_with_utc(self):
        return utc(self,100)

    def play(self):
        total_reward = 0
        steps = 0
        self.reset()
        while not self.is_game_over():
            if self.get_turn()==0:
                a = self.play_with_utc()
                self.step(a)
                reward = self.score()
                total_reward += reward
            else:
                available_actions = self.available_actions_ids()
                action = random.choice(available_actions)
                self.step(action)

            steps += 1

        for p in self.players:
            print("Toueur du joueur", p.get_color())
            print(",il lui reste ", p.get_nbPieceRestante())
            print("et il a réussi à sortir ", p.get_nbPieceSortis())

        print(self.winners)
        print(f"Partie terminée en {steps} étapes avec une récompense totale de {total_reward}.")
        return total_reward