class Player:
    def __init__(self,color):
        self.nbPieceSortis = 0
        self.turn = False
        self.color = color

    # Getters
    def get_nbPieceSortis(self):
        return self.nbPieceSortis

    def get_turn(self):
        return self.turn

    def get_color(self):
        return self.color

    # Setters
    def set_nbPieceSortis(self, nb):
        self.nbPieceSortis = nb

    def set_turn(self, turn):
        self.turn = turn

    def set_color(self, color):
        self.color = color
