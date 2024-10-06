import random
import numpy as np

class TicTacToeEnv:
    def __init__(self):
        self.board = np.zeros((3, 3))  # Grille  de 3x3
        self.current_player = 1
        self.done = False
        self.winner = None

    def reset(self):
        """Réinitialise le plateau de jeu et le joueur courant"""
        self.board = np.zeros((3, 3))
        self.current_player = 1
        self.done = False
        self.winner = None
        return self.board

    def available_actions(self):
        """Retourne les actions disponibles (les cases vides)"""
        actions = []
        for i in range(3):
            for j in range(3):
                if self.board[i, j] == 0:  # Case vide
                    actions.append((i, j))  # Ajouter la case à la liste des actions disponibles
        return actions

    def step(self, action):
        """Joue l'action du joueur actuel."""
        if self.done:
            raise ValueError("Le jeu est terminé")
        
        i, j = action
        if self.board[i, j] != 0:
            raise ValueError("Case déjà occupée")
        
        # Le joueur actuel joue sur la case choisie
        self.board[i, j] = self.current_player
        
        if self.check_winner(self.current_player):
            self.done = True
            self.winner = self.current_player
            reward = 1  # Le joueur a gagné
        elif len(self.available_actions()) == 0:
            self.done = True
            reward = 0  # Match nul
        else:
            reward = 0  # Le jeu continue
        
        # Passe au joueur suivant
        self.current_player = 3 - self.current_player  # Alterne entre 1 et 2
        return self.board, reward, self.done

    def check_winner(self, player):
        """Vérifie si le joueur donné a gagné"""
        for i in range(3):
            if np.all(self.board[i, :] == player) or np.all(self.board[:, i] == player):
                return True
        if self.board[0, 0] == self.board[1, 1] == self.board[2, 2] == player or \
           self.board[0, 2] == self.board[1, 1] == self.board[2, 0] == player:
            return True
        return False

    def is_game_over(self):
        """Vérifie si le jeu est terminé"""
        return self.done

    def state_id(self):
        """Etat actuel du plateau"""
        return tuple(map(tuple, self.board))

    def display(self):
        """Affiche le plateau"""
        print(self.board)
