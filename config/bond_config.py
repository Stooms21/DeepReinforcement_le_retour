# Dimensions du plateau
ROWS, COLS = 4, 4  # Changez ces valeurs pour ajuster la taille de la grille
CELL_SIZE = 150  # Taille de chaque case (en pixels)
MARGIN = 10  # Marge entre les cases (en pixels)
INTERSECTION_SIZE = 80  # Taille des zones cliquables (en pixels)

# Paramètres de l'affichage
TITLE_FONT_SIZE = 80  # Taille de la police pour le titre
OUTER_MARGIN = 0  # Marge extérieure autour du plateau (haut, bas, gauche, droite)

# Dimensions de la fenêtre (calculée dynamiquement)
WINDOW_WIDTH = COLS * CELL_SIZE + (COLS + 1) * MARGIN + 2 * OUTER_MARGIN
WINDOW_HEIGHT = ROWS * CELL_SIZE + (ROWS + 1) * MARGIN + 2 * OUTER_MARGIN + TITLE_FONT_SIZE
