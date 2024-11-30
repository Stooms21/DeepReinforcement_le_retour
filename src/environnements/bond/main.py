import math

import pygame
import sys

import tqdm

from config.bond_config import WINDOW_WIDTH, WINDOW_HEIGHT
from game_ui import GameUI
from Bond import Bond
from Piece import Piece
import random
import torch
import numpy as np
from src.algorithmes.uct import uct
from src.algorithmes.random_rollout import random_rollout
from src.algorithmes.EXIT import load_model,PolicyNetwork,chose_action
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
    policy_network = PolicyNetwork(input_size=21, num_actions=env.num_actions())
    # Charger un modèle sauvegardé
    model_path = "../../../src/algorithmes/policy_network.pth"
    load_model(policy_network, model_path)

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
    algorithm_menu = False
    selected_algorithm = None  # Variable pour stocker l'algorithme sélectionné

    while running:
        if menu:
            button_1player, button_2player ,bt_simulate= game_ui.draw_buttons()
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
                        algorithm_menu = True  # Activer le menu pour choisir l'algorithme

                    elif button_2player.collidepoint(event.pos):
                        print("2 Joueurs sélectionné")
                        # Ajouter ici ce que vous voulez faire en mode 2 joueurs
                        menu = False
                        solo = False
                    elif bt3.collidepoint(event.pos):
                        menu = True
                        solo = False

        elif algorithm_menu:
            game_ui.clear()
            # Afficher les boutons pour choisir l'algorithme
            button_random, button_rollout, button_uct, button_exit = game_ui.draw_algorithm_buttons()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if button_random.collidepoint(event.pos):
                        selected_algorithm = "random"
                        algorithm_menu = False  # Quitter le menu de sélection
                    elif button_rollout.collidepoint(event.pos):
                        selected_algorithm = "rollout"
                        algorithm_menu = False
                    elif button_uct.collidepoint(event.pos):
                        selected_algorithm = "uct"
                        algorithm_menu = False
                    elif button_exit.collidepoint(event.pos):
                        selected_algorithm = "exit"
                        algorithm_menu = False

        else:
            game_ui.afficher_plateau()
            bt3 = game_ui.draw_button_menu()
            btB , btF = game_ui.draw_back_forward()

            mouse_x, mouse_y = pygame.mouse.get_pos()
            highlighted_intersection = game_ui.check_intersection(mouse_x, mouse_y)
            if highlighted_intersection:
                selected_x ,  selected_y = highlighted_intersection[2],highlighted_intersection[3]
            state_move = bond.get_move_state()

            if solo and bond.get_turn() == 1:

                if selected_algorithm == "random":
                    aa = bond.available_actions_ids()
                    action = random.choice(aa)
                    bond.step(action)
                elif selected_algorithm == "rollout":
                    a = random_rollout(bond, 6, -1)
                    bond.step(a, False)
                elif selected_algorithm == "uct":
                    a = uct(bond, 10, 5, -1)
                    bond.step(a, False)
                elif selected_algorithm == "exit":
                    action = chose_action(policy_network, bond)
                    bond.step(action)
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
                        piece_type = bond.get_plateau()[x, y].get_type()
                        bond.set_case(None,x, y)
                        bond.placer_pion(selected_x, selected_y, Piece(selected_x, selected_y, bond.get_turn(), piece_type))
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

        pygame.time.Clock().tick(60)
        pygame.display.flip()

if __name__ == "__main__":
    main()    #
