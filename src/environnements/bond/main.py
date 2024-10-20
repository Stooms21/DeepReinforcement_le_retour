import pygame
import sys
from config.bond_config import WINDOW_WIDTH, WINDOW_HEIGHT
from game_ui import GameUI
from Bond import Bond
from Piece import Piece
import random
import torch
import numpy as np
from src.algorithmes.deep_q_learning import deep_q_learning

def main():
    env = Bond()
    #policy_network = deep_q_learning(env)

    # Initialisation de Pygame
    pygame.init()

    # Initialisation de la musique
    #pygame.mixer.init()
    #pygame.mixer.music.load("music.mp3")  # Remplace par le chemin de ton fichier audio
    #pygame.mixer.music.play(-1)  # Jouer la musique en boucle

    # Créer la fenêtre Pygame
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Plateau de 4x4 avec placement de pions")

    # Initialiser le jeu
    bond = Bond()
    game_ui = GameUI(window, bond)

    x = 0
    y = 0

    xx = 0
    yy = 0
    # Boucle principale du jeu
    running = True
    selected_x, selected_y = 0,0
    solo = True
    menu = True
    aaa = True
    while running:
        if menu:
            button_1player, button_2player = game_ui.draw_buttons()
            bt3 = game_ui.draw_button_menu()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()


                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button_1player.collidepoint(event.pos):
                        print("1 Joueur sélectionné")
                        # Ajouter ici ce que vous voulez faire en mode 1 joueur
                        menu = False
                        solo = True
                    elif button_2player.collidepoint(event.pos):
                        print("2 Joueurs sélectionné")
                        # Ajouter ici ce que vous voulez faire en mode 2 joueurs
                        menu = False
                        solo = False

                    elif bt3.collidepoint(event.pos):
                        menu = True
                        solo = False

        else:
            if solo and bond.get_turn() == 1:
                #s = torch.tensor(bond.one_hot_state_desc(), dtype=torch.float32)
                #q_values = policy_network(s).detach().numpy()
                #a = np.argmax(q_values)
                #bond.step(a)

                #random
                aa = bond.get_aa()
                action = random.choice(aa)
                bond.step(action)
            if aaa:
                bond.placer_pion(0,0,Piece(0, 0, bond.get_turn()))
                bond.placer_pion(0, 2, Piece(0, 2, bond.get_turn()))
                bond.placer_pion(1, 0, Piece(1, 0, bond.get_turn()))
                bond.placer_pion(1, 1, Piece(1, 1, bond.get_turn()))
                bond.placer_pion(1, 2, Piece(1, 2, bond.get_turn()))
                aaa = False
            game_ui.afficher_plateau()
            bt3 = game_ui.draw_button_menu()
            btB , btF = game_ui.draw_back_forward()
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
                    if bt3.collidepoint(event.pos):
                        menu = True
                        game_ui.clear()
                        bond.reset()
                    if btF.collidepoint(event.pos):
                        if len(bond.get_lst_plateau()) > bond.get_curr_plateau() + 1:
                            bond.set_plateau(bond.get_lst_plateau()[bond.get_curr_plateau() + 1])
                            bond.set_curr_plateau(bond.get_curr_plateau() + 1)
                    if btB.collidepoint(event.pos):
                        if 0 <= bond.get_curr_plateau() - 1:
                            bond.set_plateau(bond.get_lst_plateau()[bond.get_curr_plateau() - 1])
                            bond.set_curr_plateau(bond.get_curr_plateau() - 1)

                    if (state_move == 2 or state_move == 3) and selected_x == x and selected_y == y:
                        bond.placer_pion(x, y, Piece(x, y, bond.get_turn()))
                        bond.update_board(x, y)
                        game_ui.handle_click(None)
                        game_ui.handle_click_on_piece(None)
                    elif state_move == 4 or state_move == 5 and highlighted_intersection:
                        piece = bond.get_plateau()[x,y]
                        bond.set_case(None,x, y)
                        piece.set_pos_x(selected_x)
                        piece.set_pos_y(selected_y)
                        bond.placer_pion(selected_x, selected_y, piece)
                        bond.update_board(selected_x, selected_y)
                        game_ui.handle_click(None)
                        game_ui.handle_click_on_piece(None)
                    else:
                        game_ui.handle_click_on_piece(highlighted_intersection)
                        if not game_ui.get_move_available():
                            game_ui.handle_click(highlighted_intersection)

                            if highlighted_intersection:
                                x = highlighted_intersection[2]
                                y = highlighted_intersection[3]
                                if state_move == 0:
                                    bond.set_move_state(2)
                                elif state_move == 1:
                                    bond.set_move_state(3)
                        else:
                            if highlighted_intersection:
                                x = highlighted_intersection[2]
                                y = highlighted_intersection[3]
                                if state_move == 0:
                                    bond.set_move_state(4)
                                elif state_move == 1:
                                    bond.set_move_state(5)

                # Highlight the area under the mouse with a semi-transparent blue color
            if highlighted_intersection:
                game_ui.draw_area(highlighted_intersection[0], highlighted_intersection[1], game_ui.hover_color)

        pygame.time.Clock().tick(30)
        pygame.display.flip()

        winners = bond.get_winners()
        if len(winners) == 2:
            print("C'est égalité !")
        elif 0 in winners:
            print("Joueur blanc a gagné !")
        elif 1 in winners:
            print("Joueur noir a gagné !")

if __name__ == "__main__":
    main()
