from pico2d import load_image, get_time, load_font, draw_rectangle
from sdl2 import *
import ctypes

import game_framework
import game_world

from state_machine import StateMachine

PIXEL_PER_METER = (10.0 / 0.3) # 10 pixel 30 cm
RUN_SPEED_KMPH = 20.0 # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION

class Idle:
    FRAMES_PER_ACTION = 1

    def __init__(self, rooks):
        self.rooks = rooks

    def enter(self, e):
        self.rooks.dir = 0

    def exit(self, e):
        pass

    def do(self):
        pass

    def draw(self):
        if self.rooks.face_dir == -1:
            self.rooks.images['Idle'][0].composite_draw(0, 'h', self.rooks.x, self.rooks.y)
        else:
            self.rooks.images['Idle'][0].draw(self.rooks.x, self.rooks.y)

class Jump:
    FRAMES_PER_ACTION = 1

    def __init__(self, rooks):
        self.rooks = rooks

    def enter(self, e):
        self.rooks.frame = 0
        if self.rooks.left_down(e) or self.rooks.right_up(e):
            self.rooks.dir = self.rooks.face_dir = -1
        elif self.rooks.right_down(e) or self.rooks.left_up(e):
            self.rooks.dir = self.rooks.face_dir = 1

    def exit(self, e):
        pass

    def do(self):
        self.rooks.x += self.rooks.dir * RUN_SPEED_PPS * game_framework.frame_time

    def draw(self):
        if self.rooks.face_dir == -1:
            self.rooks.images['Idle'][0].composite_draw(0, 'h', self.rooks.x, self.rooks.y)
        else:
            self.rooks.images['Idle'][0].draw(self.rooks.x, self.rooks.y)

class Run:
    FRAMES_PER_ACTION = 1

    def __init__(self, rooks):
        self.rooks = rooks

    def enter(self, e):
        self.rooks.frame = 0
        if self.rooks.left_down(e) or self.rooks.right_up(e):
            self.rooks.dir = self.rooks.face_dir = -1
        elif self.rooks.right_down(e) or self.rooks.left_up(e):
            self.rooks.dir = self.rooks.face_dir = 1

    def exit(self, e):
        pass

    def do(self):
        self.rooks.x += self.rooks.dir * RUN_SPEED_PPS * game_framework.frame_time

    def draw(self):
        if self.rooks.face_dir == -1:
            self.rooks.images['Idle'][0].composite_draw(0, 'h', self.rooks.x, self.rooks.y)
        else:
            self.rooks.images['Idle'][0].draw(self.rooks.x, self.rooks.y)


class Attack:
    FRAMES_PER_ACTION = 11

    def __init__(self, rooks):
        self.rooks = rooks

    def enter(self, e):
        # 새로운 공격이면 프레임 초기화
        if self.rooks.frame >= 10.9 or self.rooks.frame == 0:
            self.rooks.frame = 0

        # 공격 진입 시 현재 키보드 상태 확인하여 이동 방향 설정
        keys = SDL_GetKeyboardState(None)
        left_pressed = keys[SDL_GetScancodeFromKey(self.rooks.left_key)]
        right_pressed = keys[SDL_GetScancodeFromKey(self.rooks.right_key)]

        if left_pressed and right_pressed:
            # 둘 다 눌려있으면 멈추되, 바라보는 방향은 마지막 누른 키로
            self.rooks.dir = 0
            if self.rooks.left_down(e):
                self.rooks.face_dir = -1
            elif self.rooks.right_down(e):
                self.rooks.face_dir = 1
        elif left_pressed and not right_pressed:
            self.rooks.dir = self.rooks.face_dir = -1
        elif right_pressed and not left_pressed:
            self.rooks.dir = self.rooks.face_dir = 1
        else:
            # 둘 다 안 눌려있으면 멈춤
            self.rooks.dir = 0

    def exit(self, e):
        pass

    def do(self):
        # 공격 중에도 현재 키 상태 확인하여 이동
        keys = SDL_GetKeyboardState(None)
        left_pressed = keys[SDL_GetScancodeFromKey(self.rooks.left_key)]
        right_pressed = keys[SDL_GetScancodeFromKey(self.rooks.right_key)]

        if left_pressed and right_pressed:
            # 둘 다 눌려있으면 멈춤
            self.rooks.dir = 0
        elif left_pressed and not right_pressed:
            self.rooks.dir = self.rooks.face_dir = -1
        elif right_pressed and not left_pressed:
            self.rooks.dir = self.rooks.face_dir = 1
        else:
            # 둘 다 안 눌려있으면 멈춤
            self.rooks.dir = 0

        # 공격하면서도 이동
        self.rooks.x += self.rooks.dir * RUN_SPEED_PPS * game_framework.frame_time

        self.rooks.frame = (self.rooks.frame + self.FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time)

        if self.rooks.frame >= 10.9:
            self.rooks.frame = 0

            # 공격 키가 여전히 눌려있으면 다시 공격
            if keys[SDL_GetScancodeFromKey(self.rooks.attack_key)]:
                self.rooks.state_machine.cur_state = self.rooks.ATTACK
            # 스킬 키가 눌려있으면 스킬로
            elif keys[SDL_GetScancodeFromKey(self.rooks.skill_key)]:
                self.rooks.state_machine.cur_state = self.rooks.SKILL
            # dir이 0이 아니면 RUN으로, 0이면 IDLE로
            elif self.rooks.dir != 0:
                self.rooks.state_machine.cur_state = self.rooks.RUN
            else:
                self.rooks.state_machine.cur_state = self.rooks.IDLE

    def draw(self):
        frame_index = min(int(self.rooks.frame), 10)
        if self.rooks.face_dir == -1:
            self.rooks.images['Attack'][frame_index].composite_draw(0, 'h', self.rooks.x, self.rooks.y)
        else:
            self.rooks.images['Attack'][frame_index].draw(self.rooks.x, self.rooks.y)


class Skill:
    FRAMES_PER_ACTION = 14

    def __init__(self, rooks):
        self.rooks = rooks

    def enter(self, e):
        # 새로운 스킬이면 프레임 초기화
        if self.rooks.frame >= 13.9 or self.rooks.frame == 0:
            self.rooks.frame = 0

        # 스킬 진입 시 현재 키보드 상태 확인하여 이동 방향 설정
        keys = SDL_GetKeyboardState(None)
        left_pressed = keys[SDL_GetScancodeFromKey(self.rooks.left_key)]
        right_pressed = keys[SDL_GetScancodeFromKey(self.rooks.right_key)]

        if left_pressed and right_pressed:
            # 둘 다 눌려있으면 멈추되, 바라보는 방향은 마지막 누른 키로
            self.rooks.dir = 0
            if self.rooks.left_down(e):
                self.rooks.face_dir = -1
            elif self.rooks.right_down(e):
                self.rooks.face_dir = 1
        elif left_pressed and not right_pressed:
            self.rooks.dir = self.rooks.face_dir = -1
        elif right_pressed and not left_pressed:
            self.rooks.dir = self.rooks.face_dir = 1
        else:
            # 둘 다 안 눌려있으면 멈춤
            self.rooks.dir = 0

    def exit(self, e):
        pass

    def do(self):
        # 스킬 중에도 현재 키 상태 확인하여 이동
        keys = SDL_GetKeyboardState(None)
        left_pressed = keys[SDL_GetScancodeFromKey(self.rooks.left_key)]
        right_pressed = keys[SDL_GetScancodeFromKey(self.rooks.right_key)]

        if left_pressed and right_pressed:
            # 둘 다 눌려있으면 멈춤
            self.rooks.dir = 0
        elif left_pressed and not right_pressed:
            self.rooks.dir = self.rooks.face_dir = -1
        elif right_pressed and not left_pressed:
            self.rooks.dir = self.rooks.face_dir = 1
        else:
            # 둘 다 안 눌려있으면 멈춤
            self.rooks.dir = 0

        # 스킬 사용하면서도 이동
        self.rooks.x += self.rooks.dir * RUN_SPEED_PPS * game_framework.frame_time

        self.rooks.frame = (self.rooks.frame + self.FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time)

        if self.rooks.frame >= 13.9:
            self.rooks.frame = 0

            # 스킬 키가 여전히 눌려있으면 다시 스킬
            if keys[SDL_GetScancodeFromKey(self.rooks.skill_key)]:
                self.rooks.state_machine.cur_state = self.rooks.SKILL
            # 공격 키가 눌려있으면 공격으로
            elif keys[SDL_GetScancodeFromKey(self.rooks.attack_key)]:
                self.rooks.state_machine.cur_state = self.rooks.ATTACK
            # dir이 0이 아니면 RUN으로, 0이면 IDLE로
            elif self.rooks.dir != 0:
                self.rooks.state_machine.cur_state = self.rooks.RUN
            else:
                self.rooks.state_machine.cur_state = self.rooks.IDLE

    def draw(self):
        frame_index = min(int(self.rooks.frame), 13)
        if self.rooks.face_dir == -1:
            self.rooks.images['Skill'][frame_index].composite_draw(0, 'h', self.rooks.x, self.rooks.y)
        else:
            self.rooks.images['Skill'][frame_index].draw(self.rooks.x, self.rooks.y)


class Ult:
    FRAMES_PER_ACTION = 15

    def __init__(self, rooks):
        self.rooks = rooks

    def enter(self, e):
        # 새로운 스킬이면 프레임 초기화
        if self.rooks.frame >= 14.9 or self.rooks.frame == 0:
            self.rooks.frame = 0

        # 스킬 진입 시 현재 키보드 상태 확인하여 이동 방향 설정
        keys = SDL_GetKeyboardState(None)
        left_pressed = keys[SDL_GetScancodeFromKey(self.rooks.left_key)]
        right_pressed = keys[SDL_GetScancodeFromKey(self.rooks.right_key)]

        if left_pressed and right_pressed:
            # 둘 다 눌려있으면 멈추되, 바라보는 방향은 마지막 누른 키로
            self.rooks.dir = 0
            if self.rooks.left_down(e):
                self.rooks.face_dir = -1
            elif self.rooks.right_down(e):
                self.rooks.face_dir = 1
        elif left_pressed and not right_pressed:
            self.rooks.dir = self.rooks.face_dir = -1
        elif right_pressed and not left_pressed:
            self.rooks.dir = self.rooks.face_dir = 1
        else:
            # 둘 다 안 눌려있으면 멈춤
            self.rooks.dir = 0

    def exit(self, e):
        pass

    def do(self):
        # 스킬 중에도 현재 키 상태 확인하여 이동
        keys = SDL_GetKeyboardState(None)
        left_pressed = keys[SDL_GetScancodeFromKey(self.rooks.left_key)]
        right_pressed = keys[SDL_GetScancodeFromKey(self.rooks.right_key)]

        if left_pressed and right_pressed:
            # 둘 다 눌려있으면 멈춤
            self.rooks.dir = 0
        elif left_pressed and not right_pressed:
            self.rooks.dir = self.rooks.face_dir = -1
        elif right_pressed and not left_pressed:
            self.rooks.dir = self.rooks.face_dir = 1
        else:
            # 둘 다 안 눌려있으면 멈춤
            self.rooks.dir = 0

        self.rooks.frame = (self.rooks.frame + self.FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time)

        if self.rooks.frame >= 14.9:
            self.rooks.frame = 0

            if self.rooks.dir != 0:
                self.rooks.state_machine.cur_state = self.rooks.RUN
            else:
                self.rooks.state_machine.cur_state = self.rooks.IDLE

    def draw(self):
        frame_index = min(int(self.rooks.frame), 14)
        if self.rooks.face_dir == -1:
            self.rooks.images['Ult'][frame_index].composite_draw(0, 'h', self.rooks.x, self.rooks.y)
        else:
            self.rooks.images['Ult'][frame_index].draw(self.rooks.x, self.rooks.y)


class Rooks:
    images = None

    def load_images(self):
        if Rooks.images == None:
            Rooks.images = {}
            # Idle: 1장
            Rooks.images['Idle'] = [load_image("./Character/Rooks/Idle (1).png")]
            # Attack: 11장 (1~11)
            Rooks.images['Attack'] = [load_image(f"./Character/Rooks/Attack ({i}).png") for i in range(1, 12)]
            # Skill: 14장 (1~14)
            Rooks.images['Skill'] = [load_image(f"./Character/Rooks/Skill ({i}).png") for i in range(1, 15)]
            # Ult: 15장 (1~15)
            Rooks.images['Ult'] = [load_image(f"./Character/Rooks/Ult ({i}).png") for i in range(1, 16)]

    def __init__(self, player_num=1):
        self.x, self.y = 400, 135
        self.load_images()
        self.dir = 0
        self.frame = 0
        self.face_dir = 1
        self.player_num = player_num

        # 플레이어별 키 설정
        if self.player_num == 1:
            self.left_key = SDLK_a
            self.right_key = SDLK_d
            self.attack_key = SDLK_e
            self.skill_key = SDLK_r
            self.ult_key = SDLK_s
            self.jump_key = SDLK_w
        elif self.player_num == 2:
            from sdl2 import SDLK_LEFT, SDLK_RIGHT, SDLK_RETURN
            self.left_key = SDLK_LEFT
            self.right_key = SDLK_RIGHT
            self.attack_key = SDLK_RETURN
            self.skill_key = SDLK_RSHIFT
            self.ult_key = SDLK_DOWN
            self.jump_key = SDLK_UP

        # 상태 객체들 먼저 생성
        self.IDLE = Idle(self)
        self.JUMP = Jump(self)
        self.RUN = Run(self)
        self.ATTACK = Attack(self)
        self.SKILL = Skill(self)
        self.ULT = Ult(self)

        # 상태 머신 초기화
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE : {self.ult_down: self.ULT, self.skill_down: self.SKILL, self.left_down: self.RUN, self.right_down: self.RUN, self.attack_down: self.ATTACK, self.left_up: self.RUN, self.right_up: self.RUN},
                self.RUN : {self.skill_down: self.SKILL, self.attack_down: self.ATTACK, self.left_up: self.IDLE, self.right_up: self.IDLE, self.left_down: self.IDLE, self.right_down: self.IDLE},
                self.ATTACK : {self.left_down: self.ATTACK, self.right_down: self.ATTACK, self.left_up: self.ATTACK, self.right_up: self.ATTACK},
                self.SKILL : {self.left_down: self.SKILL, self.right_down: self.SKILL, self.left_up: self.SKILL, self.right_up: self.SKILL},
                self.ULT : {},
                self.JUMP : {}
            }
        )

    def jump_down(self, e):
        return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == self.jump_key

    def ult_down(self, e):
        return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == self.ult_key

    def skill_down(self, e):
        return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == self.skill_key

    def left_down(self, e):
        return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == self.left_key

    def right_down(self, e):
        return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == self.right_key

    def left_up(self, e):
        return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == self.left_key

    def right_up(self, e):
        return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == self.right_key

    def attack_down(self, e):
        return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == self.attack_key

    def get_bb(self):
        return self.x - 15, self.y - 75, self.x + 15, self.y - 50

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()
        draw_rectangle(*self.get_bb())

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))
