import random
import math
import game_framework
import game_world

from pico2d import *

class Idle:

    def __init__(self, rooks):
        self.rooks = rooks

    def enter(self):
        self.rooks.dir = 0

    def exit(self):
        pass

    def do(self):
        self.rooks.frame = (self.rooks.frame + 1) % 8

    def draw(self):
        if self.rooks.face_dir == 1: # right
            self.rooks.image.clip_draw(0, 0, 183, 179, self.rooks.x, self.rooks.y)
        else: # face_dir == -1: # left
            self.rooks.image.clip_draw(0, 0, 183, 179, self.rooks.x, self.rooks.y)


animation_names = ['Idle']

class Rooks:
    images = None

    def load_images(self):
        if Rooks.images == None:
            Rooks.images = {}
            for name in animation_names:
                Rooks.images[name] = [load_image("./Rooks/"+ name + " (%d)" % i + ".png") for i in range(1, 9)]

    def __init__(self):
        self.x, self.y = 400, 90
        self.load_images()
        self.frame = 1
        self.dir = 1

        self.IDLE = Idle(self)

    def update(self):
        pass

    def draw(self):
        pass
