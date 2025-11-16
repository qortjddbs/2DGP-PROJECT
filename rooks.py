from pico2d import load_image, get_time, load_font, draw_rectangle
from pygame.examples.testsprite import update_rects
from sdl2 import *
import ctypes

import game_framework
import game_world

from state_machine import StateMachine

PIXEL_PER_METER = (10.0 / 0.3) # 10 pixel 30 cm / # 1pixel = 3cm, 1m = 33.33 pixel
RUN_SPEED_KMPH = 20.0 # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

GRAVITY = 9.8   # 중력 가속도 (m/s²)
TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION

class Idle:
    FRAMES_PER_ACTION = 1

    def __init__(self, rooks):
        self.rooks = rooks

    def enter(self, e):
        print('Idle State Entered with event:', e)
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
        print('Jump State Entered with event:', e)
        if self.rooks.y == self.rooks.ground_y:
            self.rooks.y_velocity = 500
            self.rooks.apply_gravity()

        self.rooks.is_air_action = True

        keys = SDL_GetKeyboardState(None)
        left_pressed = keys[SDL_GetScancodeFromKey(self.rooks.left_key)]
        right_pressed = keys[SDL_GetScancodeFromKey(self.rooks.right_key)]
        attack_pressed = keys[SDL_GetScancodeFromKey(self.rooks.attack_key)]
        skill_pressed = keys[SDL_GetScancodeFromKey(self.rooks.skill_key)]
        ult_pressed = keys[SDL_GetScancodeFromKey(self.rooks.ult_key)]

        if left_pressed and not right_pressed:
            self.rooks.dir = self.rooks.face_dir = -1
        elif right_pressed and not left_pressed:
            self.rooks.dir = self.rooks.face_dir = 1
        elif attack_pressed:
            self.rooks.state_machine.cur_state = self.rooks.ATTACK
            self.rooks.ATTACK.enter(('AIR_ATTACK_HELD', None))
            return  # JUMP.do()를 즉시 종료
        elif skill_pressed:
            self.rooks.state_machine.cur_state = self.rooks.SKILL
            self.rooks.SKILL.enter(('AIR_SKILL_HELD', None))
            return  # JUMP.do()를 즉시 종료
        elif ult_pressed:
            self.rooks.state_machine.cur_state = self.rooks.ULT
            self.rooks.ULT.enter(('AIR_ULT_HELD', None))
            return  # JUMP.do()를 즉시 종료
        else:
            self.rooks.dir = 0

    def exit(self, e):
        pass

    def do(self):
        keys = SDL_GetKeyboardState(None)
        attack_pressed = keys[SDL_GetScancodeFromKey(self.rooks.attack_key)]
        skill_pressed = keys[SDL_GetScancodeFromKey(self.rooks.skill_key)]
        ult_pressed = keys[SDL_GetScancodeFromKey(self.rooks.ult_key)]

        # JUMP 상태 전이 테이블(JUMP -> ATTACK)과 동일한 로직을 'do'에 추가
        # (이벤트가 아닌, '눌린 상태'로)
        if attack_pressed:
            self.rooks.state_machine.cur_state = self.rooks.ATTACK
            self.rooks.ATTACK.enter(('AIR_ATTACK_HELD', None))
            return  # JUMP.do()를 즉시 종료
        if skill_pressed:
            self.rooks.state_machine.cur_state = self.rooks.SKILL
            self.rooks.SKILL.enter(('AIR_SKILL_HELD', None))
            return  # JUMP.do()를 즉시 종료
        if ult_pressed:
            self.rooks.state_machine.cur_state = self.rooks.ULT
            self.rooks.ULT.enter(('AIR_ULT_HELD', None))
            return  # JUMP.do()를 즉시 종료

        # 1. 중력 적용
        self.rooks.apply_gravity()

        # 2. 공중에서 좌우 이동 (Air Control)
        if not self.rooks.x_locked:
            left_pressed = keys[SDL_GetScancodeFromKey(self.rooks.left_key)]
            right_pressed = keys[SDL_GetScancodeFromKey(self.rooks.right_key)]

            if left_pressed and not right_pressed:
                self.rooks.dir = self.rooks.face_dir = -1
            elif right_pressed and not left_pressed:
                self.rooks.dir = self.rooks.face_dir = 1
            else:
                # 키를 떼면 공중에서 해당 방향으로의 이동을 멈춤
                self.rooks.dir = 0

            self.rooks.x += self.rooks.dir * RUN_SPEED_PPS * game_framework.frame_time

        else:   # x_locked 상태면 좌우 이동 불가
            self.rooks.dir = 0

        # 3. 착지 확인
        if self.rooks.check_landing():
            keys = SDL_GetKeyboardState(None)
            left_pressed = keys[SDL_GetScancodeFromKey(self.rooks.left_key)]
            right_pressed = keys[SDL_GetScancodeFromKey(self.rooks.right_key)]
            up_pressed = keys[SDL_GetScancodeFromKey(self.rooks.jump_key)]

            if up_pressed:
                self.rooks.state_machine.cur_state = self.rooks.JUMP
                self.rooks.JUMP.enter(('LAND_JUMP', None))  # enter에서 y==ground_y 체크
            elif left_pressed or right_pressed:
                self.rooks.state_machine.cur_state = self.rooks.RUN
                self.rooks.RUN.enter(('LAND_RUN', None))
            else:
                self.rooks.state_machine.cur_state = self.rooks.IDLE
                self.rooks.IDLE.enter(('LAND_IDLE', None))

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
        print('Run State Entered with event:', e)
        self.rooks.frame = 0
        if self.rooks.left_down(e) or self.rooks.right_up(e):
            self.rooks.dir = self.rooks.face_dir = -1
        elif self.rooks.right_down(e) or self.rooks.left_up(e):
            self.rooks.dir = self.rooks.face_dir = 1

    def exit(self, e):
        pass

    def do(self):
        self.rooks.x += self.rooks.dir * RUN_SPEED_PPS * game_framework.frame_time
        if self.rooks.x < 20:
            self.rooks.x = 20
        elif self.rooks.x > 530:
            self.rooks.x = 530

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
        print('Attack State Entered with event:', e)
        # 공격 진입 시 현재 키보드 상태 확인하여 이동 방향 설정
        keys = SDL_GetKeyboardState(None)
        up_pressed = keys[SDL_GetScancodeFromKey(self.rooks.jump_key)]
        left_pressed = keys[SDL_GetScancodeFromKey(self.rooks.left_key)]
        right_pressed = keys[SDL_GetScancodeFromKey(self.rooks.right_key)]

        if self.rooks.y == self.rooks.ground_y and up_pressed:
            # Attack 상태 진입을 취소하고 JUMP로 감
            self.rooks.state_machine.cur_state = self.rooks.JUMP
            self.rooks.JUMP.enter(('ATTACK_CANCEL_JUMP', None))
            return  # Attack.enter()를 여기서 중단

        # (점프가 안 눌렸거나, 공중 공격일 때만 아래 로직 실행)
        if self.rooks.y > self.rooks.ground_y:
            self.rooks.is_air_action = True
        # (이하 원본 코드의 else/elif는 버그를 유발하므로 삭제)
        else:
            self.rooks.is_air_action = False
            self.rooks.y_velocity = 0

        # 새로운 공격이면 프레임 초기화
        if self.rooks.frame >= 10.9 or self.rooks.frame == 0:
            self.rooks.frame = 0

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
            self.rooks.dir = 0

    def exit(self, e):
        pass

    def do(self):
        keys = SDL_GetKeyboardState(None)
        left_pressed = keys[SDL_GetScancodeFromKey(self.rooks.left_key)]
        right_pressed = keys[SDL_GetScancodeFromKey(self.rooks.right_key)]
        up_pressed = keys[SDL_GetScancodeFromKey(self.rooks.jump_key)]

        if not self.rooks.is_air_action and up_pressed:
            # 지상에서 공격 중에 점프 키가 눌렸다면, 공격 취소하고 JUMP로 감
            self.rooks.state_machine.cur_state = self.rooks.JUMP
            self.rooks.JUMP.enter(('ATTACK_CANCEL_JUMP', None))
            return  # Attack.do()를 여기서 중단

        # 1. 공중 공격(액션)일 경우에만 중력 적용 및 착지 체크
        if self.rooks.is_air_action:
            self.rooks.apply_gravity()
            if self.rooks.check_landing():
                pass

        # 2. 좌우 이동 로직
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

        # 3. 애니메이션 프레임 업데이트 (기존과 동일)
        self.rooks.frame = (self.rooks.frame + self.FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time)

        # 4. 애니메이션 종료 체크
        if self.rooks.frame >= 10.9:
            self.rooks.frame = 0

            # 5. 종료 시점에 공중이었는지, 지상이었는지 체크
            if self.rooks.is_air_action:
                # (아직 공중) -> JUMP 상태로 복귀
                self.rooks.state_machine.cur_state = self.rooks.JUMP
                self.rooks.JUMP.enter(('FINISH_AIR_ATTACK', None))
            else:
                # (지상) -> 키 눌림 상태에 따라 다음 상태 결정
                keys = SDL_GetKeyboardState(None)
                if keys[SDL_GetScancodeFromKey(self.rooks.jump_key)]:
                    self.rooks.state_machine.cur_state = self.rooks.JUMP
                    self.rooks.JUMP.enter(('FINISH_GROUND_ATTACK_JUMP', None))
                elif keys[SDL_GetScancodeFromKey(self.rooks.attack_key)]:
                    self.rooks.state_machine.cur_state = self.rooks.ATTACK
                    self.rooks.ATTACK.enter(('RE_ATTACK', None))  # 연속 공격
                elif keys[SDL_GetScancodeFromKey(self.rooks.skill_key)]:
                    self.rooks.state_machine.cur_state = self.rooks.SKILL
                    self.rooks.SKILL.enter(('ATTACK_TO_SKILL', None))
                elif self.rooks.dir != 0:
                    self.rooks.state_machine.cur_state = self.rooks.RUN
                    self.rooks.RUN.enter(('ATTACK_TO_RUN', None))
                else:
                    self.rooks.state_machine.cur_state = self.rooks.IDLE
                    self.rooks.IDLE.enter(('ATTACK_TO_IDLE', None))
            return  # do() 종료

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
        print('Skill State Entered with event:', e)
        # 공격 진입 시 현재 키보드 상태 확인하여 이동 방향 설정
        keys = SDL_GetKeyboardState(None)
        up_pressed = keys[SDL_GetScancodeFromKey(self.rooks.jump_key)]
        left_pressed = keys[SDL_GetScancodeFromKey(self.rooks.left_key)]
        right_pressed = keys[SDL_GetScancodeFromKey(self.rooks.right_key)]

        if self.rooks.y == self.rooks.ground_y and up_pressed:
            # Attack 상태 진입을 취소하고 JUMP로 감
            self.rooks.state_machine.cur_state = self.rooks.JUMP
            self.rooks.JUMP.enter(('SKILL_CANCEL_JUMP', None))
            return

        # (점프가 안 눌렸거나, 공중 공격일 때만 아래 로직 실행)
        if self.rooks.y > self.rooks.ground_y:
            self.rooks.is_air_action = True
        # (이하 원본 코드의 else/elif는 버그를 유발하므로 삭제)
        else:
            self.rooks.is_air_action = False
            self.rooks.y_velocity = 0

        # 새로운 공격이면 프레임 초기화
        if self.rooks.frame >= 13.9 or self.rooks.frame == 0:
            self.rooks.frame = 0

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
            self.rooks.dir = 0

    def exit(self, e):
        pass

    def do(self):
        keys = SDL_GetKeyboardState(None)
        left_pressed = keys[SDL_GetScancodeFromKey(self.rooks.left_key)]
        right_pressed = keys[SDL_GetScancodeFromKey(self.rooks.right_key)]
        up_pressed = keys[SDL_GetScancodeFromKey(self.rooks.jump_key)]

        if not self.rooks.is_air_action and up_pressed:
            # 지상에서 공격 중에 점프 키가 눌렸다면, 공격 취소하고 JUMP로 감
            self.rooks.state_machine.cur_state = self.rooks.JUMP
            self.rooks.JUMP.enter(('SKILL_CANCEL_JUMP', None))
            return

        # 1. 공중 공격(액션)일 경우에만 중력 적용 및 착지 체크
        if self.rooks.is_air_action:
            self.rooks.apply_gravity()
            if self.rooks.check_landing():
                pass

        # 2. 좌우 이동 로직
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

        # 3. 애니메이션 프레임 업데이트 (기존과 동일)
        self.rooks.frame = (self.rooks.frame + self.FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time)

        # 4. 애니메이션 종료 체크
        if self.rooks.frame >= 13.9:
            self.rooks.frame = 0

            # 5. 종료 시점에 공중이었는지, 지상이었는지 체크
            if self.rooks.is_air_action:
                # (아직 공중) -> JUMP 상태로 복귀
                self.rooks.state_machine.cur_state = self.rooks.JUMP
                self.rooks.JUMP.enter(('FINISH_AIR_SKILL', None))
            else:
                # (지상) -> 키 눌림 상태에 따라 다음 상태 결정
                keys = SDL_GetKeyboardState(None)
                if keys[SDL_GetScancodeFromKey(self.rooks.jump_key)]:
                    self.rooks.state_machine.cur_state = self.rooks.JUMP
                    self.rooks.JUMP.enter(('FINISH_GROUND_SKILL_JUMP', None))
                elif keys[SDL_GetScancodeFromKey(self.rooks.attack_key)]:
                    self.rooks.state_machine.cur_state = self.rooks.ATTACK
                    self.rooks.ATTACK.enter(('SKILL_TO_ATTACK', None))  # 연속 공격
                elif keys[SDL_GetScancodeFromKey(self.rooks.skill_key)]:
                    self.rooks.state_machine.cur_state = self.rooks.SKILL
                    self.rooks.SKILL.enter(('RE_SKILL', None))
                elif self.rooks.dir != 0:
                    self.rooks.state_machine.cur_state = self.rooks.RUN
                    self.rooks.RUN.enter(('SKILL_TO_RUN', None))
                else:
                    self.rooks.state_machine.cur_state = self.rooks.IDLE
                    self.rooks.IDLE.enter(('SKILL_TO_IDLE', None))
            return  # do() 종료

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
        print('Ult State Entered with event:', e)
        # [FIX 1] 공중/지상 체크를 프레임 체크 밖으로 이동
        # Attack/Skill.enter와 동일한 구조
        if self.rooks.y > self.rooks.ground_y:
            self.rooks.is_air_action = True
        else:
            self.rooks.is_air_action = False
            self.rooks.y_velocity = 0

        self.rooks.x_locked = True  # 지상 궁극기는 고정 안 함
        self.rooks.frame = 0  # 항상 프레임 리셋
        self.rooks.dir = 0  # 궁극기는 항상 제자리
            #궁극기는 항상 제자리에서 사용 (dir = 0)
        self.rooks.dir = 0

        # (기존의 dir 설정 로직은 얼굴 방향 설정용으로만 사용)
        keys = SDL_GetKeyboardState(None)
        left_pressed = keys[SDL_GetScancodeFromKey(self.rooks.left_key)]
        right_pressed = keys[SDL_GetScancodeFromKey(self.rooks.right_key)]
        if left_pressed and right_pressed:
            if self.rooks.left_down(e):
                self.rooks.face_dir = -1
            elif self.rooks.right_down(e):
                self.rooks.face_dir = 1
        elif left_pressed and not right_pressed:
            self.rooks.face_dir = -1
        elif right_pressed and not left_pressed:
            self.rooks.face_dir = 1

    def exit(self, e):
        self.rooks.x_locked = False

    def do(self):
        # [FIX 3] Ult는 점프로 캔슬 불가 (state_machine 정의에 따름)

        # [FIX 4] 공중 궁극기일 경우에만 중력 적용
        if self.rooks.is_air_action:
            self.rooks.apply_gravity()
            if self.rooks.check_landing():
                # check_landing이 is_air_action과 x_locked를 False로 바꿔줌
                pass

        # [FIX 5] Ult는 좌우 이동 불가 (dir=0이므로 관련 로직 불필요)

        # 3. 애니메이션 프레임 업데이트
        self.rooks.frame = (self.rooks.frame + self.FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time)

        # 4. 애니메이션 종료 체크
        if self.rooks.frame >= 14.9:
            self.rooks.frame = 0
            self.rooks.x_locked = False  # 애니메이션 끝났으니 잠금 해제

            # [FIX 6] 종료 시점에 공중/지상 체크 (Attack/Skill.do와 동일)
            if self.rooks.is_air_action:
                # (아직 공중) -> JUMP 상태로 복귀
                self.rooks.state_machine.cur_state = self.rooks.JUMP
                self.rooks.JUMP.enter(('FINISH_AIR_ULT', None))
            else:
                # (지상) -> 키 눌림 상태에 따라 다음 상태 결정
                keys = SDL_GetKeyboardState(None)
                left_pressed = keys[SDL_GetScancodeFromKey(self.rooks.left_key)]
                right_pressed = keys[SDL_GetScancodeFromKey(self.rooks.right_key)]
                up_pressed = keys[SDL_GetScancodeFromKey(self.rooks.jump_key)]
                if up_pressed:
                    self.rooks.state_machine.cur_state = self.rooks.JUMP
                    self.rooks.JUMP.enter(('FINISH_GROUND_ULT_JUMP', None))
                elif left_pressed:
                    self.rooks.state_machine.cur_state = self.rooks.RUN
                    self.rooks.RUN.enter(('ULT_TO_RUN', None))
                elif right_pressed:
                    self.rooks.state_machine.cur_state = self.rooks.RUN
                    self.rooks.RUN.enter(('ULT_TO_RUN', None))
                elif self.rooks.dir != 0:  # (항상 0이겠지만, 혹시 모르니)
                    self.rooks.state_machine.cur_state = self.rooks.RUN
                    self.rooks.RUN.enter(('ULT_TO_RUN', None))
                else:
                    self.rooks.state_machine.cur_state = self.rooks.IDLE
                    self.rooks.IDLE.enter(('ULT_TO_IDLE', None))
            return  # do() 종료

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

        self.y_velocity = 0
        self.ground_y = 135

        self.is_air_action = False
        self.x_locked = False

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
                self.IDLE : {self.jump_down: self.JUMP, self.ult_down: self.ULT, self.skill_down: self.SKILL, self.left_down: self.RUN, self.right_down: self.RUN, self.attack_down: self.ATTACK, self.left_up: self.RUN, self.right_up: self.RUN},
                self.RUN : {self.jump_down: self.JUMP, self.ult_down: self.ULT, self.skill_down: self.SKILL, self.attack_down: self.ATTACK, self.left_up: self.IDLE, self.right_up: self.IDLE, self.left_down: self.IDLE, self.right_down: self.IDLE},
                self.ATTACK : {self.jump_down: self.JUMP, self.left_down: self.ATTACK, self.right_down: self.ATTACK, self.left_up: self.ATTACK, self.right_up: self.ATTACK},
                self.SKILL : {self.jump_down: self.JUMP, self.left_down: self.SKILL, self.right_down: self.SKILL, self.left_up: self.SKILL, self.right_up: self.SKILL},
                self.ULT : {},
                self.JUMP : {self.attack_down: self.ATTACK, self.skill_down: self.SKILL, self.ult_down: self.ULT}
            }
        )

    def apply_gravity(self):
        self.y_velocity -= GRAVITY * game_framework.frame_time * 150
        self.y += self.y_velocity * game_framework.frame_time

    def check_landing(self):
        if self.y <= self.ground_y:
            self.x_locked = False
            self.y = self.ground_y
            self.y_velocity = 0
            self.is_air_action = False
            return True
        return False

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
