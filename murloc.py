from idlelib.macosx import hideTkConsole

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

    def __init__(self, murloc):
        self.murloc = murloc

    def enter(self, e):
        print('Idle State Entered with event:', e)
        self.murloc.dir = 0

    def exit(self, e):
        pass

    def do(self):
        pass

    def draw(self):
        if self.murloc.face_dir == -1:
            self.murloc.images['Idle'][0].composite_draw(0, 'h', self.murloc.x - 78, self.murloc.y)
        else:
            self.murloc.images['Idle'][0].draw(self.murloc.x + 78, self.murloc.y)

    def get_hitbox(self):
        pass

class Jump:
    FRAMES_PER_ACTION = 1

    def __init__(self, murloc):
        self.murloc = murloc

    def enter(self, e):
        print('Jump State Entered with event:', e)
        if self.murloc.y == self.murloc.ground_y:
            self.murloc.y_velocity = 500
            self.murloc.apply_gravity()

        self.murloc.is_air_action = True

        keys = SDL_GetKeyboardState(None)
        left_pressed = keys[SDL_GetScancodeFromKey(self.murloc.left_key)]
        right_pressed = keys[SDL_GetScancodeFromKey(self.murloc.right_key)]
        attack_pressed = keys[SDL_GetScancodeFromKey(self.murloc.attack_key)]
        skill_pressed = keys[SDL_GetScancodeFromKey(self.murloc.skill_key)]
        ult_pressed = keys[SDL_GetScancodeFromKey(self.murloc.ult_key)]

        if left_pressed and not right_pressed:
            self.murloc.dir = self.murloc.face_dir = -1
        elif right_pressed and not left_pressed:
            self.murloc.dir = self.murloc.face_dir = 1
        elif attack_pressed:
            self.murloc.state_machine.cur_state = self.murloc.ATTACK
            self.murloc.ATTACK.enter(('AIR_ATTACK_HELD', None))
            return  # JUMP.do()를 즉시 종료
        elif skill_pressed:
            self.murloc.state_machine.cur_state = self.murloc.SKILL
            self.murloc.SKILL.enter(('AIR_SKILL_HELD', None))
            return  # JUMP.do()를 즉시 종료
        elif ult_pressed:
            self.murloc.state_machine.cur_state = self.murloc.ULT
            self.murloc.ULT.enter(('AIR_ULT_HELD', None))
            return  # JUMP.do()를 즉시 종료
        else:
            self.murloc.dir = 0

    def exit(self, e):
        pass

    def do(self):
        keys = SDL_GetKeyboardState(None)
        attack_pressed = keys[SDL_GetScancodeFromKey(self.murloc.attack_key)]
        skill_pressed = keys[SDL_GetScancodeFromKey(self.murloc.skill_key)]
        ult_pressed = keys[SDL_GetScancodeFromKey(self.murloc.ult_key)]

        # JUMP 상태 전이 테이블(JUMP -> ATTACK)과 동일한 로직을 'do'에 추가
        # (이벤트가 아닌, '눌린 상태'로)
        if attack_pressed:
            self.murloc.state_machine.cur_state = self.murloc.ATTACK
            self.murloc.ATTACK.enter(('AIR_ATTACK_HELD', None))
            return  # JUMP.do()를 즉시 종료
        if skill_pressed:
            self.murloc.state_machine.cur_state = self.murloc.SKILL
            self.murloc.SKILL.enter(('AIR_SKILL_HELD', None))
            return  # JUMP.do()를 즉시 종료
        if ult_pressed:
            self.murloc.state_machine.cur_state = self.murloc.ULT
            self.murloc.ULT.enter(('AIR_ULT_HELD', None))
            return  # JUMP.do()를 즉시 종료

        # 1. 중력 적용
        self.murloc.apply_gravity()

        # 2. 공중에서 좌우 이동 (Air Control)
        if not self.murloc.x_locked:
            left_pressed = keys[SDL_GetScancodeFromKey(self.murloc.left_key)]
            right_pressed = keys[SDL_GetScancodeFromKey(self.murloc.right_key)]

            if left_pressed and not right_pressed:
                self.murloc.dir = self.murloc.face_dir = -1
            elif right_pressed and not left_pressed:
                self.murloc.dir = self.murloc.face_dir = 1
            else:
                # 키를 떼면 공중에서 해당 방향으로의 이동을 멈춤
                self.murloc.dir = 0

            self.murloc.x += self.murloc.dir * RUN_SPEED_PPS * game_framework.frame_time
            if self.murloc.x < 20:
                self.murloc.x = 20
            elif self.murloc.x > 530:
                self.murloc.x = 530

        else:   # x_locked 상태면 좌우 이동 불가
            self.murloc.dir = 0

        # 3. 착지 확인
        if self.murloc.check_landing():
            keys = SDL_GetKeyboardState(None)
            left_pressed = keys[SDL_GetScancodeFromKey(self.murloc.left_key)]
            right_pressed = keys[SDL_GetScancodeFromKey(self.murloc.right_key)]
            up_pressed = keys[SDL_GetScancodeFromKey(self.murloc.jump_key)]

            if up_pressed:
                self.murloc.state_machine.cur_state = self.murloc.JUMP
                self.murloc.JUMP.enter(('LAND_JUMP', None))  # enter에서 y==ground_y 체크
            elif left_pressed or right_pressed:
                self.murloc.state_machine.cur_state = self.murloc.RUN
                self.murloc.RUN.enter(('LAND_RUN', None))
            else:
                self.murloc.state_machine.cur_state = self.murloc.IDLE
                self.murloc.IDLE.enter(('LAND_IDLE', None))

    def draw(self):
        if self.murloc.face_dir == -1:
            self.murloc.images['Idle'][0].composite_draw(0, 'h', self.murloc.x - 78, self.murloc.y)
        else:
            self.murloc.images['Idle'][0].draw(self.murloc.x + 78, self.murloc.y)

    def get_hitbox(self):
        pass



class Run:
    FRAMES_PER_ACTION = 1

    def __init__(self, murloc):
        self.murloc = murloc

    def enter(self, e):
        print('Run State Entered with event:', e)
        self.murloc.frame = 0
        if self.murloc.left_down(e) or self.murloc.right_up(e):
            self.murloc.dir = self.murloc.face_dir = -1
        elif self.murloc.right_down(e) or self.murloc.left_up(e):
            self.murloc.dir = self.murloc.face_dir = 1

    def exit(self, e):
        pass

    def do(self):
        keys = SDL_GetKeyboardState(None)
        left_pressed = keys[SDL_GetScancodeFromKey(self.murloc.left_key)]
        right_pressed = keys[SDL_GetScancodeFromKey(self.murloc.right_key)]
        if left_pressed and right_pressed:
            # 둘 다 눌려있으면 멈춤
            self.murloc.dir = 0
        elif left_pressed and not right_pressed:
            self.murloc.dir = self.murloc.face_dir = -1
        elif right_pressed and not left_pressed:
            self.murloc.dir = self.murloc.face_dir = 1
        else:
            # 둘 다 안 눌려있으면 멈춤
            self.murloc.dir = 0
        self.murloc.x += self.murloc.dir * RUN_SPEED_PPS * game_framework.frame_time
        if self.murloc.x < 20:
            self.murloc.x = 20
        elif self.murloc.x > 530:
            self.murloc.x = 530

    def draw(self):
        if self.murloc.face_dir == -1:
            self.murloc.images['Idle'][0].composite_draw(0, 'h', self.murloc.x - 78, self.murloc.y)
        else:
            self.murloc.images['Idle'][0].draw(self.murloc.x + 78, self.murloc.y)

    def get_hitbox(self):
        pass


class Attack:
    FRAMES_PER_ACTION = 10

    def __init__(self, murloc):
        self.murloc = murloc

    def enter(self, e):
        print('Attack State Entered with event:', e)
        # 공격 진입 시 현재 키보드 상태 확인하여 이동 방향 설정
        keys = SDL_GetKeyboardState(None)
        up_pressed = keys[SDL_GetScancodeFromKey(self.murloc.jump_key)]
        left_pressed = keys[SDL_GetScancodeFromKey(self.murloc.left_key)]
        right_pressed = keys[SDL_GetScancodeFromKey(self.murloc.right_key)]

        if self.murloc.y == self.murloc.ground_y and up_pressed:
            # Attack 상태 진입을 취소하고 JUMP로 감
            self.murloc.state_machine.cur_state = self.murloc.JUMP
            self.murloc.JUMP.enter(('ATTACK_CANCEL_JUMP', None))
            return  # Attack.enter()를 여기서 중단

        # (점프가 안 눌렸거나, 공중 공격일 때만 아래 로직 실행)
        if self.murloc.y > self.murloc.ground_y:
            self.murloc.is_air_action = True
        # (이하 원본 코드의 else/elif는 버그를 유발하므로 삭제)
        else:
            self.murloc.is_air_action = False
            self.murloc.y_velocity = 0

        # 새로운 공격이면 프레임 초기화
        if self.murloc.frame >= 9.9 or self.murloc.frame == 0:
            self.murloc.frame = 0

        if left_pressed and right_pressed:
            # 둘 다 눌려있으면 멈추되, 바라보는 방향은 마지막 누른 키로
            self.murloc.dir = 0
            if self.murloc.left_down(e):
                self.murloc.face_dir = -1
            elif self.murloc.right_down(e):
                self.murloc.face_dir = 1
        elif left_pressed and not right_pressed:
            self.murloc.dir = self.murloc.face_dir = -1
        elif right_pressed and not left_pressed:
            self.murloc.dir = self.murloc.face_dir = 1
        else:
            self.murloc.dir = 0

    def exit(self, e):
        pass

    def do(self):
        # 수동 프레임 모드일 때는 자동 진행 중단
        if self.murloc.manual_frame:
            return

        keys = SDL_GetKeyboardState(None)
        left_pressed = keys[SDL_GetScancodeFromKey(self.murloc.left_key)]
        right_pressed = keys[SDL_GetScancodeFromKey(self.murloc.right_key)]
        up_pressed = keys[SDL_GetScancodeFromKey(self.murloc.jump_key)]

        if not self.murloc.is_air_action and up_pressed:
            # 지상에서 공격 중에 점프 키가 눌렸다면, 공격 취소하고 JUMP로 감
            self.murloc.state_machine.cur_state = self.murloc.JUMP
            self.murloc.JUMP.enter(('ATTACK_CANCEL_JUMP', None))
            return  # Attack.do()를 여기서 중단

        # 1. 공중 공격(액션)일 경우에만 중력 적용 및 착지 체크
        if self.murloc.is_air_action:
            self.murloc.apply_gravity()
            if self.murloc.check_landing():
                pass

        # 2. 좌우 이동 로직
        if left_pressed and right_pressed:
            # 둘 다 눌려있으면 멈춤
            self.murloc.dir = 0
        elif left_pressed and not right_pressed:
            self.murloc.dir = self.murloc.face_dir = -1
        elif right_pressed and not left_pressed:
            self.murloc.dir = self.murloc.face_dir = 1
        else:
            # 둘 다 안 눌려있으면 멈춤
            self.murloc.dir = 0

        # 공격하면서도 이동
        self.murloc.x += self.murloc.dir * RUN_SPEED_PPS * game_framework.frame_time
        if self.murloc.x < 20:
            self.murloc.x = 20
        elif self.murloc.x > 530:
            self.murloc.x = 530

        # 3. 애니메이션 프레임 업데이트 (기존과 동일)
        self.murloc.frame = (self.murloc.frame + self.FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time)

        # 4. 애니메이션 종료 체크
        if self.murloc.frame >= 9.9:
            self.murloc.frame = 0

            # 5. 종료 시점에 공중이었는지, 지상이었는지 체크
            if self.murloc.is_air_action:
                # (아직 공중) -> JUMP 상태로 복귀
                self.murloc.state_machine.cur_state = self.murloc.JUMP
                self.murloc.JUMP.enter(('FINISH_AIR_ATTACK', None))
            else:
                # (지상) -> 키 눌림 상태에 따라 다음 상태 결정
                keys = SDL_GetKeyboardState(None)
                if keys[SDL_GetScancodeFromKey(self.murloc.jump_key)]:
                    self.murloc.state_machine.cur_state = self.murloc.JUMP
                    self.murloc.JUMP.enter(('FINISH_GROUND_ATTACK_JUMP', None))
                elif keys[SDL_GetScancodeFromKey(self.murloc.attack_key)]:
                    self.murloc.state_machine.cur_state = self.murloc.ATTACK
                    self.murloc.ATTACK.enter(('RE_ATTACK', None))  # 연속 공격
                elif keys[SDL_GetScancodeFromKey(self.murloc.skill_key)]:
                    self.murloc.state_machine.cur_state = self.murloc.SKILL
                    self.murloc.SKILL.enter(('ATTACK_TO_SKILL', None))
                elif keys[SDL_GetScancodeFromKey(self.murloc.ult_key)]:
                    self.murloc.state_machine.cur_state = self.murloc.ULT
                    self.murloc.ULT.enter(('ATTACK_TO_ULT', None))
                elif self.murloc.dir != 0:
                    self.murloc.state_machine.cur_state = self.murloc.RUN
                    self.murloc.RUN.enter(('ATTACK_TO_RUN', None))
                else:
                    self.murloc.state_machine.cur_state = self.murloc.IDLE
                    self.murloc.IDLE.enter(('ATTACK_TO_IDLE', None))
            return  # do() 종료

    def draw(self):
        frame_index = min(int(self.murloc.frame), 9)
        if self.murloc.face_dir == -1:
            self.murloc.images['Attack'][frame_index].composite_draw(0, 'h', self.murloc.x - 78, self.murloc.y)
        else:
            self.murloc.images['Attack'][frame_index].draw(self.murloc.x + 78, self.murloc.y)

    def get_hitbox(self):
        frame = int(self.murloc.frame)
        x, y = self.murloc.x, self.murloc.y
        face_dir = self.murloc.face_dir

        # 프레임별 히트박스 정의 (캐릭터 중심 기준)
        hitbox_data = {
            0: None,  # 준비 동작
            1: (45, -20, 65, -10),  # 준비 동작
            2: (62, -20, 82, -10),  # 공격 시작
            3: (62, -20, 82, -10),  # 휘두르기 시작
            4: (62, -20, 82, -10),  # 중간 단계
            5: (62, -20, 82, -10),  # 최대 범위
            6: (62, -20, 82, -10),  # 감속 시작
            7: (62, -20, 82, -10),  # 공격 끝
            8: (45, -20, 65, -10),  # 회수 시작
            9: None,  # 회수 중
        }

        if frame not in hitbox_data or hitbox_data[frame] is None:
            return None

        dx, dy, width, height = hitbox_data[frame]

        if face_dir == 1:  # 오른쪽
            return x + dx, y + dy, x + width, y + height
        else:  # 왼쪽
            return x - width, y + dy, x - dx, y + height


class Skill:
    FRAMES_PER_ACTION = 17

    def __init__(self, murloc):
        self.murloc = murloc

    def enter(self, e):
        print('Skill State Entered with event:', e)
        # [FIX 1] 공중/지상 체크를 프레임 체크 밖으로 이동
        # Attack/Skill.enter와 동일한 구조
        if self.murloc.y > self.murloc.ground_y:
            self.murloc.is_air_action = True
        else:
            self.murloc.is_air_action = False
            self.murloc.y_velocity = 0

        self.murloc.x_locked = True
        self.murloc.frame = 0  # 항상 프레임 리셋
        self.murloc.dir = 0  # 궁극기는 항상 제자리

        # (기존의 dir 설정 로직은 얼굴 방향 설정용으로만 사용)
        keys = SDL_GetKeyboardState(None)
        left_pressed = keys[SDL_GetScancodeFromKey(self.murloc.left_key)]
        right_pressed = keys[SDL_GetScancodeFromKey(self.murloc.right_key)]
        if left_pressed and right_pressed:
            if self.murloc.left_down(e):
                self.murloc.face_dir = -1
            elif self.murloc.right_down(e):
                self.murloc.face_dir = 1
        elif left_pressed and not right_pressed:
            self.murloc.face_dir = -1
        elif right_pressed and not left_pressed:
            self.murloc.face_dir = 1

    def exit(self, e):
        self.murloc.x_locked = False

    def do(self):
        # 수동 프레임 모드일 때는 자동 진행 중단
        if self.murloc.manual_frame:
            return

        keys = SDL_GetKeyboardState(None)
        up_pressed = keys[SDL_GetScancodeFromKey(self.murloc.jump_key)]

        if not self.murloc.is_air_action and up_pressed:
            # 지상에서 공격 중에 점프 키가 눌렸다면, 공격 취소하고 JUMP로 감
            self.murloc.state_machine.cur_state = self.murloc.JUMP
            self.murloc.JUMP.enter(('SKILL_CANCEL_JUMP', None))
            return

        # 1. 공중 공격(액션)일 경우에만 중력 적용 및 착지 체크
        if self.murloc.is_air_action:
            self.murloc.apply_gravity()
            if self.murloc.check_landing():
                pass

        # 3. 애니메이션 프레임 업데이트 (기존과 동일)
        self.murloc.frame = (self.murloc.frame + self.FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time)

        # 4. 애니메이션 종료 체크
        if self.murloc.frame >= 16.9:
            self.murloc.frame = 0
            self.murloc.x_locked = False

            # 5. 종료 시점에 공중이었는지, 지상이었는지 체크
            if self.murloc.is_air_action:
                # (아직 공중) -> JUMP 상태로 복귀
                self.murloc.state_machine.cur_state = self.murloc.JUMP
                self.murloc.JUMP.enter(('FINISH_AIR_SKILL', None))
            else:
                # (지상) -> 키 눌림 상태에 따라 다음 상태 결정
                keys = SDL_GetKeyboardState(None)
                left_pressed = keys[SDL_GetScancodeFromKey(self.murloc.left_key)]
                right_pressed = keys[SDL_GetScancodeFromKey(self.murloc.right_key)]

                if keys[SDL_GetScancodeFromKey(self.murloc.jump_key)]:
                    self.murloc.state_machine.cur_state = self.murloc.JUMP
                    self.murloc.JUMP.enter(('FINISH_GROUND_SKILL_JUMP', None))
                elif keys[SDL_GetScancodeFromKey(self.murloc.attack_key)]:
                    self.murloc.state_machine.cur_state = self.murloc.ATTACK
                    self.murloc.ATTACK.enter(('SKILL_TO_ATTACK', None))  # 연속 공격
                elif keys[SDL_GetScancodeFromKey(self.murloc.skill_key)]:
                    self.murloc.state_machine.cur_state = self.murloc.SKILL
                    self.murloc.SKILL.enter(('RE_SKILL', None))
                elif keys[SDL_GetScancodeFromKey(self.murloc.ult_key)]:
                    self.murloc.state_machine.cur_state = self.murloc.ULT
                    self.murloc.ULT.enter(('SKILL_TO_ULT', None))
                elif left_pressed and right_pressed:
                    self.murloc.state_machine.cur_state = self.murloc.IDLE
                    self.murloc.RUN.enter(('SKILL_TO_IDLE', None))
                elif left_pressed or right_pressed:
                    self.murloc.state_machine.cur_state = self.murloc.RUN
                    self.murloc.RUN.enter(('SKILL_TO_RUN', None))
                else:
                    self.murloc.state_machine.cur_state = self.murloc.IDLE
                    self.murloc.IDLE.enter(('SKILL_TO_IDLE', None))

    def draw(self):
        frame_index = min(int(self.murloc.frame), 16)
        if self.murloc.face_dir == -1:
            self.murloc.images['Skill'][frame_index].composite_draw(0, 'h', self.murloc.x - 78, self.murloc.y)
        else:
            self.murloc.images['Skill'][frame_index].draw(self.murloc.x + 78, self.murloc.y)

    def get_hitbox(self):
        frame = int(self.murloc.frame)
        x, y = self.murloc.x, self.murloc.y
        face_dir = self.murloc.face_dir

        # 프레임별 히트박스 정의 (캐릭터 중심 기준)
        hitbox_data = {
            0: None,  # 준비 동작
            1: None,  # 준비 동작
            2: None,  # 공격 시작
            3: None,  # 휘두르기 시작
            4: None,  # 중간 단계
            5: None,  # 최대 범위
            6: None,  # 감속 시작
            7: None,  # 공격 끝
            8: None,  # 회수 시작
            9: None,  # 회수 중
            10: (40, -30, 185, 10), # 275에서 195까지
            11: (40, -30, 105, 10), # 195에서 145까지
            12: (40, -30, 55, 10),
            13: None,
            14: None,
            15: None,
            16: None,
        }

        if frame not in hitbox_data or hitbox_data[frame] is None:
            return None

        dx, dy, width, height = hitbox_data[frame]

        if face_dir == 1:  # 오른쪽
            return x + dx, y + dy, x + width, y + height
        else:  # 왼쪽
            return x - width, y + dy, x - dx, y + height

# 기력 40소모
class Ult:
    FRAMES_PER_ACTION = 12

    def __init__(self, murloc):
        self.murloc = murloc

    def enter(self, e):
        print('Ult State Entered with event:', e)
        # [FIX 1] 공중/지상 체크를 프레임 체크 밖으로 이동
        # Attack/Skill.enter와 동일한 구조
        if self.murloc.y > self.murloc.ground_y:
            self.murloc.is_air_action = True
        else:
            self.murloc.is_air_action = False
            self.murloc.y_velocity = 0

        self.murloc.x_locked = True
        self.murloc.frame = 0  # 항상 프레임 리셋
        self.murloc.dir = 0  # 궁극기는 항상 제자리

        # (기존의 dir 설정 로직은 얼굴 방향 설정용으로만 사용)
        keys = SDL_GetKeyboardState(None)
        left_pressed = keys[SDL_GetScancodeFromKey(self.murloc.left_key)]
        right_pressed = keys[SDL_GetScancodeFromKey(self.murloc.right_key)]
        if left_pressed and right_pressed:
            if self.murloc.left_down(e):
                self.murloc.face_dir = -1
            elif self.murloc.right_down(e):
                self.murloc.face_dir = 1
        elif left_pressed and not right_pressed:
            self.murloc.face_dir = -1
        elif right_pressed and not left_pressed:
            self.murloc.face_dir = 1

    def exit(self, e):
        self.murloc.x_locked = False

    def do(self):
        # 수동 프레임 모드일 때는 자동 진행 중단
        if self.murloc.manual_frame:
            return

        # [FIX 4] 공중 궁극기일 경우에만 중력 적용
        if self.murloc.is_air_action:
            self.murloc.apply_gravity()
            if self.murloc.check_landing():
                pass

        # [FIX 5] Ult는 좌우 이동 불가 (dir=0이므로 관련 로직 불필요)

        # 3. 애니메이션 프레임 업데이트
        self.murloc.frame = (self.murloc.frame + self.FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time)

        # 4. 애니메이션 종료 체크
        if self.murloc.frame >= 11.9:
            self.murloc.frame = 0
            self.murloc.x_locked = False  # 애니메이션 끝났으니 잠금 해제

            # [FIX 6] 종료 시점에 공중/지상 체크 (Attack/Skill.do와 동일)
            if self.murloc.is_air_action:
                # (아직 공중) -> JUMP 상태로 복귀
                self.murloc.state_machine.cur_state = self.murloc.JUMP
                self.murloc.JUMP.enter(('FINISH_AIR_ULT', None))
            else:
                # (지상) -> 키 눌림 상태에 따라 다음 상태 결정
                keys = SDL_GetKeyboardState(None)
                left_pressed = keys[SDL_GetScancodeFromKey(self.murloc.left_key)]
                right_pressed = keys[SDL_GetScancodeFromKey(self.murloc.right_key)]

                if keys[SDL_GetScancodeFromKey(self.murloc.jump_key)]:
                    self.murloc.state_machine.cur_state = self.murloc.JUMP
                    self.murloc.JUMP.enter(('FINISH_GROUND_ULT_JUMP', None))
                elif keys[SDL_GetScancodeFromKey(self.murloc.attack_key)]:
                    self.murloc.state_machine.cur_state = self.murloc.ATTACK
                    self.murloc.ATTACK.enter(('ULT_TO_ATTACK', None))  # 연속 공격
                elif keys[SDL_GetScancodeFromKey(self.murloc.skill_key)]:
                    self.murloc.state_machine.cur_state = self.murloc.SKILL
                    self.murloc.SKILL.enter(('ULT_TO_SKILL', None))
                elif keys[SDL_GetScancodeFromKey(self.murloc.ult_key)]:
                    self.murloc.state_machine.cur_state = self.murloc.ULT
                    self.murloc.ULT.enter(('RE_ULT', None))
                elif left_pressed and right_pressed:
                    self.murloc.state_machine.cur_state = self.murloc.IDLE
                    self.murloc.ULT.enter(('ULT_TO_IDLE', None))
                elif left_pressed or right_pressed:
                    self.murloc.state_machine.cur_state = self.murloc.RUN
                    self.murloc.RUN.enter(('ULT_TO_RUN', None))
                else:
                    self.murloc.state_machine.cur_state = self.murloc.IDLE
                    self.murloc.IDLE.enter(('ULT_TO_IDLE', None))
            return  # do() 종료

    def draw(self):
        frame_index = min(int(self.murloc.frame), 11)
        if self.murloc.face_dir == -1:
            self.murloc.images['Ult'][frame_index].composite_draw(0, 'h', self.murloc.x - 78, self.murloc.y)
        else:
            self.murloc.images['Ult'][frame_index].draw(self.murloc.x + 78, self.murloc.y)

    def get_hitbox(self):
        frame = int(self.murloc.frame)
        x, y = self.murloc.x, self.murloc.y
        face_dir = self.murloc.face_dir

        # 프레임별 히트박스 정의 (캐릭터 중심 기준)
        hitbox_data = {
            0: None,  # 준비 동작
            1: None,  # 준비 동작
            2: None,  # 공격 시작
            3: None,  # 휘두르기 시작
            4: None,  # 중간 단계
            5: (62, -20, 82, -10),  # 최대 범위
            6: (62, -20, 82, -10),  # 감속 시작
            7: (62, -20, 82, -10),  # 공격 끝
            8: (45, -20, 65, -10),  # 회수 시작
            9: None,  # 회수 중
        }

        if frame not in hitbox_data or hitbox_data[frame] is None:
            return None

        dx, dy, width, height = hitbox_data[frame]

        if face_dir == 1:  # 오른쪽
            return x + dx, y + dy, x + width, y + height
        else:  # 왼쪽
            return x - width, y + dy, x - dx, y + height

class Murloc:
    images = None

    def load_images(self):
        if Murloc.images == None:
            Murloc.images = {}
            # Idle: 1장
            Murloc.images['Idle'] = [load_image("./Character/murloc/Idle (1).png")]
            # Attack: 10장
            Murloc.images['Attack'] = [load_image(f"./Character/murloc/Attack ({i}).png") for i in range(1, 11)]
            # Skill: 17장
            Murloc.images['Skill'] = [load_image(f"./Character/murloc/Skill ({i}).png") for i in range(1, 18)]
            # Ult: 12장
            Murloc.images['Ult'] = [load_image(f"./Character/murloc/Ult ({i}).png") for i in range(1, 13)]

    def __init__(self, player_num=1):
        # 디버그 모드 추가
        self.debug_mode = False  # F1 키로 토글
        self.manual_frame = False  # F2 키로 토글
        self.frame_step = 0.0  # 수동 프레임 값
        self.last_click_pos = None  # 마지막 클릭 좌표

        self.load_images()
        self.dir = 0
        self.frame = 0

        self.player_num = player_num

        self.y_velocity = 0
        self.ground_y = 83

        self.is_air_action = False
        self.x_locked = False

        # 플레이어별 키 설정
        if self.player_num == 1:
            self.x, self.y = 90, 83
            self.face_dir = 1
            self.left_key = SDLK_a
            self.right_key = SDLK_d
            self.attack_key = SDLK_e
            self.skill_key = SDLK_r
            self.ult_key = SDLK_s
            self.jump_key = SDLK_w
        elif self.player_num == 2:
            from sdl2 import SDLK_LEFT, SDLK_RIGHT, SDLK_RETURN
            self.x, self.y = 450, 83
            self.face_dir = -1
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
                self.SKILL : {self.jump_down: self.JUMP},
                self.ULT : {},
                self.JUMP : {self.attack_down: self.ATTACK, self.skill_down: self.SKILL, self.ult_down: self.ULT}
            }
        )

    def apply_gravity(self):
        self.y_velocity -= GRAVITY * game_framework.frame_time * 150
        self.y += self.y_velocity * game_framework.frame_time

    def check_landing(self):
        if self.y <= self.ground_y:
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
        return self.x - 13, self.y - 23, self.x + 12, self.y + 2

    def update(self):
        self.state_machine.update()

    def get_hitbox(self):
        return self.state_machine.cur_state.get_hitbox()

    def draw(self):
        self.state_machine.draw()

        # 캐릭터 바운딩 박스
        draw_rectangle(*self.get_bb())

        # 히트박스
        hitbox = self.get_hitbox()
        if hitbox:
            from pico2d import draw_rectangle as draw_rect
            x1, y1, x2, y2 = hitbox
            draw_rect(x1, y1, x2, y2)

        # 디버그 정보 표시
        if self.debug_mode:
            state_name = self.state_machine.cur_state.__class__.__name__
            frame_num = int(self.frame)
            max_frame = self.state_machine.cur_state.FRAMES_PER_ACTION - 1

            # 상태 및 프레임 정보
            info1 = f"P{self.player_num} {state_name}"
            info2 = f"Frame: {frame_num}/{max_frame}"
            info3 = f"Pos: ({int(self.x)}, {int(self.y)})"
            info4 = f"FaceDir: {'RIGHT' if self.face_dir == 1 else 'LEFT'}"

            if hitbox:
                info5 = f"Hitbox: ({int(x1)},{int(y1)})-({int(x2)},{int(y2)})"
            else:
                info5 = "Hitbox: None"

            if self.manual_frame:
                info6 = "MANUAL MODE (</> to change frame)"
            else:
                info6 = "AUTO MODE (F2 to toggle)"

            # 마우스 클릭 좌표
            if self.last_click_pos:
                info7 = f"Last Click: ({self.last_click_pos[0]}, {self.last_click_pos[1]})"
            else:
                info7 = "Last Click: None"

            if not hasattr(self, 'font'):
                self.font = load_font('ENCR10B.TTF', 14)

            y_offset = self.y + 60
            self.font.draw(self.x - 60, y_offset, info1, (255, 255, 0))
            self.font.draw(self.x - 60, y_offset - 15, info2, (255, 255, 0))
            self.font.draw(self.x - 60, y_offset - 30, info3, (255, 255, 0))
            self.font.draw(self.x - 60, y_offset - 45, info4, (255, 255, 0))
            self.font.draw(self.x - 60, y_offset - 60, info5, (255, 255, 0))
            self.font.draw(self.x - 60, y_offset - 75, info6, (0, 255, 255))
            self.font.draw(self.x - 60, y_offset - 90, info7, (255, 100, 100))

            # 클릭 위치에 십자선 표시
            if self.last_click_pos:
                from pico2d import draw_line
                cx, cy = self.last_click_pos
                draw_line(cx - 10, cy, cx + 10, cy)
                draw_line(cx, cy - 10, cx, cy + 10)

    def handle_event(self, event):
        # 디버그 키 처리
        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_F1:
                self.debug_mode = not self.debug_mode
                print(f"Debug Mode: {'ON' if self.debug_mode else 'OFF'}")
                return
            elif event.key == SDLK_F2:
                self.manual_frame = not self.manual_frame
                if self.manual_frame:
                    self.frame_step = 0.0
                print(f"Manual Frame Mode: {'ON' if self.manual_frame else 'OFF'}")
                return
            elif self.manual_frame:
                # 수동 프레임 진행
                if event.key == SDLK_PERIOD:  # '>' 키
                    max_frame = self.state_machine.cur_state.FRAMES_PER_ACTION - 1
                    self.frame_step = min(self.frame_step + 1, max_frame)
                    self.frame = self.frame_step
                    print(f"Frame: {int(self.frame_step)}")
                    return
                elif event.key == SDLK_COMMA:  # '<' 키
                    self.frame_step = max(self.frame_step - 1, 0)
                    self.frame = self.frame_step
                    print(f"Frame: {int(self.frame_step)}")
                    return

        # 마우스 클릭 처리
        if self.debug_mode and event.type == SDL_MOUSEBUTTONDOWN:
            # pico2d의 이벤트는 SDL2 이벤트를 래핑한 것
            # x, y 좌표는 event.x, event.y로 직접 접근
            mouse_x = getattr(event, 'x', 0)
            mouse_y = getattr(event, 'y', 0)
            self.last_click_pos = (mouse_x, 400 - mouse_y)  # Y좌표 반전
            print(f"Mouse Click: ({self.last_click_pos[0]}, {self.last_click_pos[1]})")
            return

        self.state_machine.handle_state_event(('INPUT', event))