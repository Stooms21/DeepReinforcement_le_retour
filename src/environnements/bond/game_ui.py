import pygame
from config.bond_config import CELL_SIZE, MARGIN, OUTER_MARGIN, TITLE_FONT_SIZE, INTERSECTION_SIZE, ROWS, COLS

class GameUI:
    def __init__(self, window, bond):
        self.window = window
        self.bond = bond
        self.case_image = pygame.image.load("img/tuileV1.jpg")
        self.case_image = pygame.transform.scale(self.case_image, (CELL_SIZE, CELL_SIZE))
        self.title_font = pygame.font.SysFont(None, TITLE_FONT_SIZE)
        self.background_color = (255, 255, 255)
        self.hover_color = (173, 216, 230, 128)  # Couleur surbrillance bleue semi-transparente
        self.selected_color = (255, 255, 0, 128)  # Couleur surbrillance jaune semi-transparente
        self.selected_position = None
        self.window.fill(self.background_color)
        self.draw_title()

    def draw_title(self):
        title_text = self.title_font.render("BOND", True, (0, 0, 0))
        self.window.blit(title_text,
                         (self.window.get_width() // 2 - title_text.get_width() // 2, OUTER_MARGIN // 2))


    def afficher_plateau(self):
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
                    self.window.blit(piece.get_img(), (piece.get_pos_x(), piece.get_pos_y()))

        # Highlight selected area if it exists
        if self.selected_position:
            self.draw_area(self.selected_position[0], self.selected_position[1], self.selected_color)


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
                    return intersection_x, intersection_y
        return None

    def draw_area(self, intersection_x, intersection_y, color):
        hover_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        hover_surface.fill(color)
        self.window.blit(hover_surface, (intersection_x, intersection_y))

    def handle_click(self, highlighted_intersection):
        if highlighted_intersection:
            x, y = highlighted_intersection
            # Surligner la zone cliquée en jaune
            self.selected_position = (x, y)
