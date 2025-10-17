from pico2d import load_image

class Rooks:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.face_dir = 1
        self.width = 183
        self.height = 179
        self.image = load_image('Rooks/1.png')

    def update(self):
        self.frame = (self.frame + 1) % 8
        pass

    def draw(self):
        self.image.clip_draw(0, 0, self.width, self.height, self.x, self.y)
        pass