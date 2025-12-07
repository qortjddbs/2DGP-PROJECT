from pico2d import *

class Wilderness:
    def __init__(self):
        self.image = load_image('./Maps/wilderness.png')

    def update(self):
        pass

    def draw(self):
        self.image.draw(550/2, 400/2)