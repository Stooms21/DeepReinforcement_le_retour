import Piece
import pygame
import sys

pygame.init()

# Initialisation de la musique
pygame.mixer.init()
pygame.mixer.music.load("music.mp3")  # Remplace par le chemin de ton fichier audio
pygame.mixer.music.play(-1)  # Jouer la musique en boucle (-1 pour la boucle infinie)

# Dimensions du plateau
ROWS, COLS = 5, 5
CELL_SIZE = 100  # Taille de chaque case (en pixels)
MARGIN = 0  # Marge entre les cases (en pixels)
INTERSECTION_SIZE = 80  # Taille des zones cliquables (en pixels)

# Paramètres de l'affichage
TITLE_FONT_SIZE = 100  # Taille de la police pour le titre
OUTER_MARGIN = 100  # Marge extérieure autour du plateau (haut, bas, gauche, droite)

# Dimensions de la fenêtre (largeur et hauteur)
WINDOW_WIDTH = COLS * CELL_SIZE + (COLS + 1) * MARGIN + 2 * OUTER_MARGIN
WINDOW_HEIGHT = ROWS * CELL_SIZE + (ROWS + 1) * MARGIN + 2 * OUTER_MARGIN + TITLE_FONT_SIZE

# Créer la fenêtre Pygame
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Plateau de 5x5 avec placement de pions")

# Charger l'image pour une case et les deux images de pions
image_path = "img/tuileV1.jpg"  # Chemin vers l'image de la case (à remplacer par votre image)
pion_image_path = "img/gun.png"  # Chemin vers la première image du pion
second_pion_image_path = "img/mitraillette.png"  # Chemin vers la seconde image du pion

# Charger l'image de la case
case_image = pygame.image.load(image_path)
case_image = pygame.transform.scale(case_image, (CELL_SIZE, CELL_SIZE))

class Bond:
    def __init__(self, n, m):
        # n est le nombre de lignes
        # m est le nombre de colonnes
        self.n = n
        self.m = m
        # On crée un plateau de n x m avec des intersections vides
        self.plateau = [[None for _ in range(m)] for _ in range(n)]
        self.pieces = []
    def placer_pion(self, ligne, colonne, piece):

        if 0 <= ligne < self.n and 0 <= colonne < self.m:
            if self.plateau[ligne][colonne] is None:
                self.plateau[ligne][colonne] = piece
                self.pieces.append(piece)
                return True
            else:
                return False
        else:
            return False

    def afficher_plateau(self):

        for row in range(self.n):
            for col in range(self.m):
                x = col * CELL_SIZE + (col + 1) * MARGIN + OUTER_MARGIN
                y = row * CELL_SIZE + (row + 1) * MARGIN + OUTER_MARGIN + TITLE_FONT_SIZE
                # Blit (afficher) l'image à la position (x, y)
                window.blit(case_image, (x, y))