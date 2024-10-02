import pygame
import sys
import Bond as b
import Piece as p
from Piece import Piece
import Piece
from Player import Player
import pygame
import sys

pygame.init()

# Initialisation de la musique
#pygame.mixer.init()
#pygame.mixer.music.load("music.mp3")  # Remplace par le chemin de ton fichier audio
#pygame.mixer.music.play(-1)  # Jouer la musique en boucle (-1 pour la boucle infinie)

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
background_color = (255, 255, 255)  # Blanc

# Remplir le fond
window.fill(background_color)
# Initialisation de la police pour le titre
pygame.font.init()
title_font = pygame.font.SysFont(None, TITLE_FONT_SIZE)  # Utilisation de la police par défaut

# Texte pour le titre
title_text = title_font.render("BOND", True, (0, 0, 0))  # Noir
# Dessiner le titre en haut de l'écran avec la marge extérieure
window.blit(title_text,
            (WINDOW_WIDTH // 2 - title_text.get_width() // 2, OUTER_MARGIN // 2))  # Centrer le texte du titre

def draw_area(intersection_x, intersection_y, color):
    # Créer une surface semi-transparente pour la surbrillance bleue
    hover_surface = pygame.Surface((INTERSECTION_SIZE * 1.5, INTERSECTION_SIZE * 1.5), pygame.SRCALPHA)
    hover_surface.fill(color)
    # Ajuster la position pour rendre la surbrillance plus petite
    window.blit(hover_surface, (intersection_x - INTERSECTION_SIZE / 3,
                                intersection_y - INTERSECTION_SIZE / 3))
def afficher_plateau(bond):
    for row in range(bond.get_x() + 1):
        for col in range(bond.get_y() + 1):
            x = col * CELL_SIZE + (col + 1) * MARGIN + OUTER_MARGIN
            y = row * CELL_SIZE + (row + 1) * MARGIN + OUTER_MARGIN + TITLE_FONT_SIZE
            # Blit (afficher) l'image à la position (x, y)
            window.blit(case_image, (x, y))
    for row in range(bond.get_x()):
        for col in range(bond.get_y()):
            if bond.get_plateau()[row][col] is not None:
                piece = bond.get_plateau()[row][col]
                pion_pos = (piece.get_pos_x,piece.get_pos_y)
                window.blit(piece.get_img, pion_pos)

# Fonction pour vérifier si la souris est dans une intersection
def check_intersection(x, y):
    for row in range(ROWS -1):  # ROWS + 1 pour inclure les intersections en bas et à droite
        for col in range(COLS -1):  # COLS + 1 pour inclure les intersections à droite
            # Calculer la position de l'intersection
            intersection_x = (col + 1) * CELL_SIZE + col * MARGIN - INTERSECTION_SIZE // 2 + OUTER_MARGIN
            intersection_y = (row + 1) * CELL_SIZE + row * MARGIN - INTERSECTION_SIZE // 2 + OUTER_MARGIN + TITLE_FONT_SIZE
            # Vérifier si le point (x, y) est dans cette intersection
            if (intersection_x <= x <= intersection_x + INTERSECTION_SIZE) and (
                    intersection_y <= y <= intersection_y + INTERSECTION_SIZE
            ):

                return intersection_x, intersection_y,x,y
    return None

if __name__ == "__main__":
    highlight_color = (255, 255, 0, 200)  # Jaune semi-transparent (alpha 128)
    hover_color = (173, 216, 230, 200)
    selected = False
    selected_x = 0
    selected_y = 0
    val_x,val_y,x, y = (0,0,0, 0)
    bond = b.Bond()


    while True:
        afficher_plateau(bond)
        mouse_x, mouse_y = pygame.mouse.get_pos()
        highlighted_intersection = check_intersection(mouse_x, mouse_y)

        if highlighted_intersection is not None:
            val_x,val_y,x,y = highlighted_intersection[0], highlighted_intersection[1] ,highlighted_intersection[2],highlighted_intersection[3]

        if highlighted_intersection is not None:
            draw_area(val_x, val_y, hover_color)
            if not selected:
                bond.set_move_state(1)

        if selected:
            draw_area(selected_x, selected_y, highlight_color)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if bond.get_move_state() == 2 and val_x == selected_x and val_y == selected_y:
                    piece = p.Piece(selected_x, selected_y, "blanc")
                    bond.placer_pion(x, y, piece)
                    print(bond.get_plateau())
                else:
                    bond.set_move_state(1)

                if bond.get_move_state() == 1:
                    draw_area(x, y, highlight_color)
                    selected = True
                    selected_x = val_x
                    selected_y = val_y
                    bond.set_move_state(2)

        pygame.time.Clock().tick(60)
        # rafraichir l'écran
        pygame.display.flip()
