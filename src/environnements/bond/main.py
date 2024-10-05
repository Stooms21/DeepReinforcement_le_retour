import pygame
import sys
from config.bond_config import WINDOW_WIDTH, WINDOW_HEIGHT
from game_ui import GameUI
from Bond import Bond

def main():
    # Initialisation de Pygame
    pygame.init()

    # Initialisation de la musique
    pygame.mixer.init()
    pygame.mixer.music.load("music.mp3")  # Remplace par le chemin de ton fichier audio
    pygame.mixer.music.play(-1)  # Jouer la musique en boucle

    # Créer la fenêtre Pygame
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Plateau de 5x5 avec placement de pions")

    # Initialiser le jeu
    bond = Bond()
    game_ui = GameUI(window, bond)

    # Boucle principale du jeu
    running = True
    while running:
        game_ui.afficher_plateau()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        highlighted_intersection = game_ui.check_intersection(mouse_x, mouse_y)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                game_ui.handle_click(highlighted_intersection)

        # Highlight the area under the mouse with a semi-transparent blue color
        if highlighted_intersection:
            game_ui.draw_area(highlighted_intersection[0], highlighted_intersection[1], game_ui.hover_color)

        pygame.time.Clock().tick(60)
        pygame.display.flip()


if __name__ == "__main__":
    main()
