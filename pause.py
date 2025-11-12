from pico2d import load_image

class Pause:
    def __init__(self):
        self.image = load_image('./Background/pause.png')

    def update(self):
        pass

    def draw(self):
        self.image.draw(550 / 2, 400 / 2)