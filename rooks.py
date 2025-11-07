from pico2d import load_image, get_time, load_font, draw_rectangle
from sdl2 import SDL_KEYDOWN, SDLK_SPACE, SDLK_RIGHT, SDL_KEYUP, SDLK_LEFT

import game_framework
import game_world

from state_machine import StateMachine

def a_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == 'a'

def d_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == 'd'

PIXEL_PER_METER = (10.0 / 0.3) # 10 pixel 30 cm
RUN_SPEED_KMPH = 20.0 # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 1

class Idle:

    def __init__(self, rooks):
        self.rooks = rooks

    def enter(self):
        self.rooks.dir = 0

    def exit(self):
        pass

    def do(self):
        pass

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
                Rooks.images[name] = [load_image("./Rooks/"+ name + " (%d)" % 1 + ".png")]

    def __init__(self):
        self.x, self.y = 400, 90
        self.load_images()
        self.frame = 0
        self.dir = 1

        self.IDLE = Idle(self)

    def get_bb(self):
        return self.x - 50, self.y - 50, self.x + 50, self.y + 50

    def update(self):
        pass

    def draw(self):
        if self.dir < 0:
            Rooks.images['Idle'][int(self.frame)].composite_draw(0, 'h', self.x, self.y, 200, 200)
        else:
            Rooks.images['Idle'][int(self.frame)].draw(self.x, self.y, 200, 200)
        draw_rectangle(*self.get_bb())

    def handle_event(self, event):
        pass