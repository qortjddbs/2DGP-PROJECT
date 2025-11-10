from pico2d import load_image, get_time, load_font, draw_rectangle
from sdl2 import SDL_KEYDOWN, SDLK_SPACE, SDLK_a, SDLK_d, SDL_KEYUP

import game_framework
import game_world

from state_machine import StateMachine

def a_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_a

def d_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_d

def a_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_a

def d_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_d

def space_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE

PIXEL_PER_METER = (10.0 / 0.3) # 10 pixel 30 cm
RUN_SPEED_KMPH = 20.0 # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 11

class Idle:
    def __init__(self, rooks):
        self.rooks = rooks

    def enter(self, event):
        self.rooks.dir = 0

    def exit(self, event):
        pass

    def do(self):
        self.rooks.frame = (self.rooks.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 1

    def draw(self):
        if self.rooks.face_dir == 1:
            self.rooks.images['Idle'][0].draw(self.rooks.x, self.rooks.y)
        else:
            self.rooks.images['Idle'][0].draw(self.rooks.x, self.rooks.y)


class Run:
    def __init__(self, rooks):
        self.rooks = rooks

    def enter(self, event):
        if a_down(event):
            self.rooks.dir = -1
            self.rooks.face_dir = -1
        elif d_down(event):
            self.rooks.dir = 1
            self.rooks.face_dir = 1

    def exit(self, event):
        pass

    def do(self):
        self.rooks.x += self.rooks.dir * RUN_SPEED_PPS * game_framework.frame_time

    def draw(self):
        if self.rooks.face_dir == -1:
            self.rooks.images['Idle'][int(self.rooks.frame)].composite_draw(0, 'h', self.rooks.x, self.rooks.y, 200, 200)
        else:
            self.rooks.images['Idle'][int(self.rooks.frame)].draw(self.rooks.x, self.rooks.y, 200, 200)


class Attack:
    def __init__(self, rooks):
        self.rooks = rooks

    def enter(self, event):
        self.rooks.frame = 0

    def exit(self, event):
        pass

    def do(self):
        self.rooks.frame = (self.rooks.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 11

    def draw(self):
        if self.rooks.face_dir == -1:
            self.rooks.images['Attack'][int(self.rooks.frame)].composite_draw(0, 'h', self.rooks.x, self.rooks.y, 200, 200)
        else:
            self.rooks.images['Attack'][int(self.rooks.frame)].draw(self.rooks.x, self.rooks.y, 200, 200)


class Skill:
    def __init__(self, rooks):
        self.rooks = rooks

    def enter(self, event):
        self.rooks.frame = 0

    def exit(self, event):
        pass

    def do(self):
        self.rooks.frame = (self.rooks.frame + 14 * ACTION_PER_TIME * game_framework.frame_time) % 14

    def draw(self):
        if self.rooks.face_dir == -1:
            self.rooks.images['Skill'][int(self.rooks.frame)].composite_draw(0, 'h', self.rooks.x, self.rooks.y, 200, 200)
        else:
            self.rooks.images['Skill'][int(self.rooks.frame)].draw(self.rooks.x, self.rooks.y, 200, 200)


class Ult:
    def __init__(self, rooks):
        self.rooks = rooks

    def enter(self, event):
        self.rooks.frame = 0

    def exit(self, event):
        pass

    def do(self):
        self.rooks.frame = (self.rooks.frame + 15 * ACTION_PER_TIME * game_framework.frame_time) % 15

    def draw(self):
        if self.rooks.face_dir == -1:
            self.rooks.images['Ult'][int(self.rooks.frame)].composite_draw(0, 'h', self.rooks.x, self.rooks.y, 200, 200)
        else:
            self.rooks.images['Ult'][int(self.rooks.frame)].draw(self.rooks.x, self.rooks.y, 200, 200)


class Rooks:
    images = None

    def load_images(self):
        if Rooks.images == None:
            Rooks.images = {}
            # Idle: 1장
            Rooks.images['Idle'] = [load_image("./Rooks/Idle (1).png")]
            # Attack: 11장 (1~11)
            Rooks.images['Attack'] = [load_image(f"./Rooks/Attack ({i}).png") for i in range(1, 12)]
            # Skill: 14장 (1~14)
            Rooks.images['Skill'] = [load_image(f"./Rooks/Skill ({i}).png") for i in range(1, 15)]
            # Ult: 15장 (1~15)
            Rooks.images['Ult'] = [load_image(f"./Rooks/Ult ({i}).png") for i in range(1, 16)]

    def __init__(self):
        self.x, self.y = 400, 200
        self.load_images()
        self.dir = 0
        self.frame = 0
        self.face_dir = 1

        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.ATTACK = Attack(self)
        self.SKILL = Skill(self)
        self.ULT = Ult(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE : {a_down: self.RUN, d_down: self.RUN, space_down: self.ATTACK},
                self.RUN : {a_up: self.IDLE, d_up: self.IDLE},
                self.ATTACK : {},
                self.SKILL : {},
                self.ULT : {},
            }
        )

    def get_bb(self):
        return self.x - 100, self.y - 100, self.x + 100, self.y + 100

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()
        draw_rectangle(*self.get_bb())

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))