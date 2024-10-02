class Piece:
    def __init__(self, x, y,color):
        self.pos_x = x
        self.pos_y = y
        self.type = 0 #gun 0,smg 1,bazooka 2
        self.img = "img/gun.png"
        self.color = color

        # Getters
        def get_pos_x(self):
            return self.pos_x

        def get_pos_y(self):
            return self.pos_y

        def get_type(self):
            return self.type

        def get_img(self):
            return self.img

        def get_color(self):
            return self.color

        # Setters
        def set_pos_x(self, x):
            self.pos_x = x

        def set_pos_y(self, y):
            self.pos_y = y

        def set_type(self, type):
            self.type = type

        def set_img(self, img):
            self.img = img

        def set_color(self, color):
            self.color = color