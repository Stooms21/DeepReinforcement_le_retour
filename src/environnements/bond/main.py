import pygame
import sys
from config.bond_config import WINDOW_WIDTH, WINDOW_HEIGHT
from game_ui import GameUI
from Bond import Bond
from Piece import Piece


def main():
    # Initialisation de Pygame
    pygame.init()

    # Initialisation de la musique
    pygame.mixer.init()
    pygame.mixer.music.load("music.mp3")  # Remplace par le chemin de ton fichier audio
    pygame.mixer.music.play(-1)  # Jouer la musique en boucle

    # Créer la fenêtre Pygame
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Plateau de 4x4 avec placement de pions")

    # Initialiser le jeu
    bond = Bond()
    game_ui = GameUI(window, bond)

    x = 0
    y = 0
    # Boucle principale du jeu
    running = True
    selected_x, selected_y = 0,0
    while running:
        game_ui.afficher_plateau()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        highlighted_intersection = game_ui.check_intersection(mouse_x, mouse_y)
        if highlighted_intersection:
            selected_x ,  selected_y = highlighted_intersection[2],highlighted_intersection[3]
        state_move = bond.get_move_state()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:

                if (state_move == 2 or state_move == 3) and selected_x == x and selected_y == y:
                    bond.placer_pion(x, y, Piece(x, y, bond.get_turn()))
                    bond.check_piece_to_develop(x,y)
                    bond.set_turn()
                    game_ui.handle_click(None)
                elif (state_move == 3 and state_move == 4) and selected_x == x and selected_y == y:
                    bond.placer_pion(x, y, Piece(x, y, bond.get_turn()))
                    bond.check_piece_to_develop(x,y)
                    bond.set_turn()
                    game_ui.handle_click(None)
                else:
                    game_ui.handle_click(highlighted_intersection)
                    game_ui.handle_click_on_piece(highlighted_intersection)
                    if highlighted_intersection:
                        x = highlighted_intersection[2]
                        y = highlighted_intersection[3]
                        if state_move == 0:
                            bond.set_move_state(2)
                        elif state_move == 1:
                            bond.set_move_state(3)

            # Highlight the area under the mouse with a semi-transparent blue color
        if highlighted_intersection:
            game_ui.draw_area(highlighted_intersection[0], highlighted_intersection[1], game_ui.hover_color)

        bond.check_piece_to_scored()
        running = not bond.check_is_game_over()
        pygame.time.Clock().tick(60)
        pygame.display.flip()


if __name__ == "__main__":
    main()
