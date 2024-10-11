import pygame
from config.bond_config import CELL_SIZE, MARGIN, OUTER_MARGIN, TITLE_FONT_SIZE, INTERSECTION_SIZE, ROWS, COLS, \
    WINDOW_WIDTH


class GameUI:
    def __init__(self, window, bond):
        self.window = window
        self.bond = bond
        self.case_image = pygame.image.load("img/tuile3.jpg")
        self.case_image = pygame.transform.scale(self.case_image, (CELL_SIZE, CELL_SIZE))
        self.title_font = pygame.font.SysFont(None, TITLE_FONT_SIZE)
        self.background_color = (255, 255, 255)
        self.hover_color = (173, 216, 230, 200)  # Couleur surbrillance bleue semi-transparente
        self.selected_color = (0, 255, 0, 230)  # Couleur surbrillance jaune semi-transparente
        self.selected_position = None
        self.window.fill(self.background_color)
        self.draw_title()
        self.move_available = []
    def get_move_available(self):
        return self.move_available

    def draw_title(self):
        title_text = self.title_font.render("BOND", True, (0, 0, 0))
        self.window.blit(title_text,
                         (self.window.get_width() // 2 - title_text.get_width() // 2, OUTER_MARGIN // 2))

    def afficher_plateau(self):
        self.window.fill(self.background_color)
        self.draw_title()
        # Calculate the dynamic size of the board
        plateau_width = COLS * CELL_SIZE + (COLS - 1) * MARGIN
        plateau_height = ROWS * CELL_SIZE + (ROWS - 1) * MARGIN
        start_x = (self.window.get_width() - plateau_width) // 2  # Center horizontally
        start_y = (
                          self.window.get_height() - plateau_height - TITLE_FONT_SIZE) // 2 + TITLE_FONT_SIZE  # Center vertically

        for row in range(self.bond.get_x()):
            for col in range(self.bond.get_y()):
                x = start_x + col * (CELL_SIZE + MARGIN)
                y = start_y + row * (CELL_SIZE + MARGIN)
                self.window.blit(self.case_image, (x, y))
                if self.bond.get_plateau()[row][col] is not None:
                    piece = self.bond.get_plateau()[row][col]
                    pygame_img = pygame.image.load(piece.get_img())
                    pygame_img = pygame.transform.scale(pygame_img, (0.8 * CELL_SIZE, 0.8 * CELL_SIZE))
                    self.window.blit(pygame_img, (x + 0.1 * CELL_SIZE, 0.1 * CELL_SIZE + y))

        # Highlight selected area if it exists
        if self.selected_position:
            self.draw_area(self.selected_position[0], self.selected_position[1], self.selected_color)
        if self.move_available:
            for move in self.move_available:
                print(move)
                self.draw_area(start_x + move[1] * (CELL_SIZE + MARGIN) , start_y + move[0] * (CELL_SIZE + MARGIN) , self.selected_color)
        font = pygame.font.SysFont(None, 40)
        if not self.bond.get_turn():
            title_text = font.render("Tour du joueur blanc", True, (0, 0, 0))
        else:
            title_text = font.render("Tour du joueur noir", True, (0, 0, 0))

        self.window.blit(title_text,
                         (self.window.get_width() // 2 - title_text.get_width() // 2, OUTER_MARGIN // 2 + 50))
        players = self.bond.get_players()
        nbsortisP1 =  "B: " + str(players[0].get_nbPieceSortis())
        nbsortisP2 = "N: " + str(players[1].get_nbPieceSortis())
        title_text = font.render(nbsortisP1, True, (0, 0, 0))
        self.window.blit(title_text,
                         (20, OUTER_MARGIN // 2 + 50))
        title_text = font.render(nbsortisP2, True, (0, 0, 0))
        self.window.blit(title_text,
                         (WINDOW_WIDTH - 80, OUTER_MARGIN // 2 + 50))

    def check_intersection(self, mouse_x, mouse_y):
        # Calcul du centrage du plateau
        plateau_width = COLS * CELL_SIZE + (COLS - 1) * MARGIN
        plateau_height = ROWS * CELL_SIZE + (ROWS - 1) * MARGIN
        start_x = (self.window.get_width() - plateau_width) // 2
        start_y = (self.window.get_height() - plateau_height - TITLE_FONT_SIZE) // 2 + TITLE_FONT_SIZE

        for row in range(self.bond.get_x()):
            for col in range(self.bond.get_y()):
                intersection_x = start_x + col * (CELL_SIZE + MARGIN)
                intersection_y = start_y + row * (CELL_SIZE + MARGIN)
                if (intersection_x <= mouse_x <= intersection_x + CELL_SIZE) and \
                        (intersection_y <= mouse_y <= intersection_y + CELL_SIZE):
                    return intersection_x, intersection_y, row, col
        return None

    def draw_area(self, intersection_x, intersection_y, color):
        hover_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        hover_surface.fill(color)
        self.window.blit(hover_surface, (intersection_x, intersection_y))

    def handle_click(self, highlighted_intersection):
        if highlighted_intersection:
            x, y, xx, yy = highlighted_intersection
            # Surligner la zone cliquée en jaune
            self.selected_position = (x, y)
        else:
            self.selected_position = None

    def handle_click_on_piece(self, highlighted_intersection):
        if highlighted_intersection:
            x, y, xx, yy = highlighted_intersection
            if self.bond.check_piece_color(xx, yy):
                self.move_available = self.bond.get_move_available(xx,yy)
            else:
                self.move_available = None
        else:
            self.move_available = None

    # Fonction pour dessiner les boutons
    def draw_buttons(self):
        # Définir quelques couleurs
        BLACK = (0, 0, 0)
        BLUE = (0, 0, 255)
        GREEN = (0, 255, 0)
        WHITE = (255, 255, 255)

        # Définir la police
        font = pygame.font.SysFont(None, 50)

        # Créer les boutons
        button_1player = pygame.Rect(220, 150, 200, 50)
        button_2player = pygame.Rect(220, 250, 200, 50)
        # Définir les textes des boutons
        text_1player = font.render('1 Joueur', True, WHITE)
        text_2player = font.render('2 Joueurs', True, WHITE)
        pygame.draw.rect(self.window, BLUE, button_1player)
        pygame.draw.rect(self.window, GREEN, button_2player)
        self.window.blit(text_1player, (button_1player.x + 35, button_1player.y + 5))
        self.window.blit(text_2player, (button_2player.x + 25, button_2player.y + 5))

        return button_1player, button_2player

    def draw_button_menu(self):
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)

        font = pygame.font.SysFont(None, 30)
        button_3player = pygame.Rect(0, 0, 70, 50)
        text_3player = font.render('Menu', True, WHITE)
        pygame.draw.rect(self.window, BLACK, button_3player)

        self.window.blit(text_3player, (button_3player.x + 12, button_3player.y + 12))
        return button_3player
    def clear(self):
        self.window.fill(self.background_color)

