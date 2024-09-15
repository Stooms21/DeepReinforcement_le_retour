import pygame
import sys
import Bond
def playGame():
    # Initialisation de Pygame
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

    # Charger et redimensionner les deux images de pions
    pion_image = pygame.image.load(pion_image_path)
    pion_image = pygame.transform.scale(pion_image, (INTERSECTION_SIZE, INTERSECTION_SIZE))

    second_pion_image = pygame.image.load(second_pion_image_path)
    second_pion_image = pygame.transform.scale(second_pion_image, (INTERSECTION_SIZE * 1.5, INTERSECTION_SIZE * 1.5))

    # Couleur de fond et de surbrillance
    background_color = (255, 255, 255)  # Blanc
    highlight_color = (255, 255, 0, 200)  # Jaune semi-transparent (alpha 128)
    hover_color = (173, 216, 230, 200)  # Bleu clair semi-transparent (alpha 128)

    # Initialisation de la police pour le titre
    pygame.font.init()
    title_font = pygame.font.SysFont(None, TITLE_FONT_SIZE)  # Utilisation de la police par défaut

    # Texte pour le titre
    title_text = title_font.render("BOND", True, (0, 0, 0))  # Noir

    # Liste pour garder les positions des pions et le nombre de pions à chaque intersection
    pions_positions = {}  # Clé : coordonnées de l'intersection, Valeur : nombre de pions (1 ou 2)

    # Garde la position de l'intersection actuellement surlignée et survolée
    highlighted_intersection = None
    hovered_intersection = None  # Pour garder la zone survolée par la souris

    # Fonction pour vérifier si la souris est dans une intersection
    def check_intersection(x, y):
        for row in range(ROWS + 1):  # ROWS + 1 pour inclure les intersections en bas et à droite
            for col in range(COLS + 1):  # COLS + 1 pour inclure les intersections à droite
                # Calculer la position de l'intersection
                intersection_x = col * CELL_SIZE + col * MARGIN - INTERSECTION_SIZE // 2 + OUTER_MARGIN
                intersection_y = row * CELL_SIZE + row * MARGIN - INTERSECTION_SIZE // 2 + OUTER_MARGIN + TITLE_FONT_SIZE
                # Vérifier si le point (x, y) est dans cette intersection
                if (intersection_x <= x <= intersection_x + INTERSECTION_SIZE) and (
                    intersection_y <= y <= intersection_y + INTERSECTION_SIZE
                ):
                    return intersection_x, intersection_y
        return None

    # Boucle principale
    running = True
    while running:
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Obtenir les coordonnées du clic
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # Vérifier si le clic est dans une intersection
                intersection = check_intersection(mouse_x, mouse_y)

                if intersection:
                    # Si l'utilisateur clique sur l'intersection déjà surlignée, on place ou remplace le pion
                    if highlighted_intersection == intersection:
                        # Vérifier si un pion est déjà présent à cette position
                        if intersection in pions_positions:
                            if pions_positions[intersection] == 1:
                                # Passer au deuxième type de pion
                                pions_positions[intersection] = 2
                            else:
                                # Si le deuxième pion est déjà placé, on ne fait rien (ou on peut ajouter d'autres actions)
                                pass
                        else:
                            # Si aucun pion n'est présent, placer le premier pion
                            pions_positions[intersection] = 1

                        highlighted_intersection = None  # Retirer la surbrillance après avoir placé le pion
                    else:
                        # Si un autre endroit est cliqué, changer la surbrillance
                        highlighted_intersection = intersection
                else:
                    # Si on clique ailleurs, enlever la surbrillance
                    highlighted_intersection = None

        # Obtenir les coordonnées de la souris pour vérifier si elle survole une intersection
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hovered_intersection = check_intersection(mouse_x, mouse_y)

        # Remplir le fond
        window.fill(background_color)

        # Dessiner le titre en haut de l'écran avec la marge extérieure
        window.blit(title_text, (WINDOW_WIDTH // 2 - title_text.get_width() // 2, OUTER_MARGIN // 2))  # Centrer le texte du titre

        # Dessiner le plateau de 5x5
        for row in range(ROWS):
            for col in range(COLS):
                # Calculer les coordonnées (x, y) de chaque case en ajoutant la marge extérieure
                x = col * CELL_SIZE + (col + 1) * MARGIN + OUTER_MARGIN
                y = row * CELL_SIZE + (row + 1) * MARGIN + OUTER_MARGIN + TITLE_FONT_SIZE
                # Blit (afficher) l'image à la position (x, y)
                window.blit(case_image, (x, y))

        # Dessiner la surbrillance si une intersection est sélectionnée
        if highlighted_intersection:
            # Créer une surface semi-transparente pour la surbrillance jaune
            highlight_surface = pygame.Surface((INTERSECTION_SIZE * 1.5, INTERSECTION_SIZE * 1.5), pygame.SRCALPHA)
            highlight_surface.fill(highlight_color)
            # Ajuster la position pour rendre la surbrillance plus petite
            window.blit(highlight_surface, (highlighted_intersection[0] - INTERSECTION_SIZE / 3,
                                            highlighted_intersection[1] - INTERSECTION_SIZE / 3))

        # Dessiner la surbrillance si la souris survole une intersection
        if hovered_intersection:
            # Créer une surface semi-transparente pour la surbrillance bleue
            hover_surface = pygame.Surface((INTERSECTION_SIZE * 1.5, INTERSECTION_SIZE * 1.5), pygame.SRCALPHA)
            hover_surface.fill(hover_color)
            # Ajuster la position pour rendre la surbrillance plus petite
            window.blit(hover_surface, (hovered_intersection[0] - INTERSECTION_SIZE / 3,
                                        hovered_intersection[1] - INTERSECTION_SIZE / 3))

        # Dessiner les pions aux intersections cliquées
        for pion_pos, pion_type in pions_positions.items():
            if pion_type == 1:
                window.blit(pion_image, pion_pos)
            elif pion_type == 2:
                window.blit(second_pion_image, tuple(map(lambda a ,b : a - b ,pion_pos , (INTERSECTION_SIZE / 2.3,INTERSECTION_SIZE / 2.3))))

        # Rafraîchir l'écran
        pygame.display.flip()

    # Quitter Pygame proprement
    pygame.quit()
if __name__=="__main__":
    #playGame()
    while True:
        for event in pygame.event.get():
            bond = Bond.Bond(3, 3)
            bond.afficher_plateau()
            pygame.display.flip()