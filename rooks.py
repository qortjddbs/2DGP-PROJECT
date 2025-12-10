from pico2d import load_image, get_time, load_font, draw_rectangle
from pygame.examples.testsprite import update_rects
from sdl2 import *
import ctypes

import game_framework
import game_world
import sound_manager

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
        # 가장자리에서 벗어나면 중력 적용
        if self.rooks.is_air_action:
            self.rooks.apply_gravity()
            self.rooks.check_platform_collision()

    def draw(self):
        visual_y = self.rooks.y + 52
        if self.rooks.face_dir == -1:
            self.rooks.images['Idle'][0].composite_draw(0, 'h', self.rooks.x, visual_y)
        else:
            self.rooks.images['Idle'][0].draw(self.rooks.x, visual_y)

    def get_hitbox(self):
        pass


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
        elif ult_pressed and self.rooks.mp >= 50:
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
        if ult_pressed and self.rooks.mp >= 50:
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
            if self.rooks.x < 15:
                self.rooks.x = 15
            elif self.rooks.x > 530:
                self.rooks.x = 530

        else:   # x_locked 상태면 좌우 이동 불가
            self.rooks.dir = 0

        # 3. 착지 확인
        if self.rooks.check_platform_collision():
            keys = SDL_GetKeyboardState(None)
            left_pressed = keys[SDL_GetScancodeFromKey(self.rooks.left_key)]
            right_pressed = keys[SDL_GetScancodeFromKey(self.rooks.right_key)]
            up_pressed = keys[SDL_GetScancodeFromKey(self.rooks.jump_key)]

            if up_pressed:
                self.rooks.state_machine.cur_state = self.rooks.JUMP
                self.rooks.JUMP.enter(('LAND_JUMP', None))  # enter에서 y==ground_y 체크
            elif left_pressed and right_pressed:
                self.rooks.state_machine.cur_state = self.rooks.IDLE
                self.rooks.IDLE.enter(('LAND_IDLE', None))
            elif left_pressed or right_pressed:
                self.rooks.state_machine.cur_state = self.rooks.RUN
                self.rooks.RUN.enter(('LAND_RUN', None))
            else:
                self.rooks.state_machine.cur_state = self.rooks.IDLE
                self.rooks.IDLE.enter(('LAND_IDLE', None))

    def draw(self):
        visual_y = self.rooks.y + 52
        if self.rooks.face_dir == -1:
            self.rooks.images['Idle'][0].composite_draw(0, 'h', self.rooks.x, visual_y)
        else:
            self.rooks.images['Idle'][0].draw(self.rooks.x, visual_y)

    def get_hitbox(self):
        return None

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
        self.rooks.x += self.rooks.dir * RUN_SPEED_PPS * game_framework.frame_time
        if self.rooks.x < 15:
            self.rooks.x = 15
        elif self.rooks.x > 530:
            self.rooks.x = 530

        # 가장자리에서 벗어나면 중력 적용
        if self.rooks.is_air_action:
            self.rooks.apply_gravity()
            # 착지 체크
            if self.rooks.check_platform_collision():
                # [FIX] 착지했는데 이동 키가 여전히 눌려있다면? -> RUN 유지
                if left_pressed or right_pressed:
                    # 아무것도 안 함 (RUN 상태 유지, is_air_action은 check_platform_collision에서 False가 됨)
                    pass
                else:
                    # 이동 키가 안 눌려있다면 -> IDLE로 전환
                    self.rooks.state_machine.cur_state = self.rooks.IDLE
                    self.rooks.IDLE.enter(('LAND_FROM_RUN', None))

    def draw(self):
        visual_y = self.rooks.y + 52
        if self.rooks.face_dir == -1:
            self.rooks.images['Idle'][0].composite_draw(0, 'h', self.rooks.x, visual_y)
        else:
            self.rooks.images['Idle'][0].draw(self.rooks.x, visual_y)

    def get_hitbox(self):
        return None

class Attack:
    FRAMES_PER_ACTION = 11

    def __init__(self, rooks):
        self.rooks = rooks

    def enter(self, e):
        self.rooks.hit_log.clear()  # 새 공격 시작 시 로그 초기화
        print('Attack State Entered with event:', e)
        # 공격 진입 시 현재 키보드 상태 확인하여 이동 방향 설정

        # 공격 사운드 재생
        sound_manager.play_character_sound('Rooks', 'attack')

        keys = SDL_GetKeyboardState(None)
        left_pressed = keys[SDL_GetScancodeFromKey(self.rooks.left_key)]
        right_pressed = keys[SDL_GetScancodeFromKey(self.rooks.right_key)]

        # (점프가 안 눌렸거나, 공중 공격일 때만 아래 로직 실행)
        if self.rooks.y > self.rooks.ground_y:
            self.rooks.is_air_action = True
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
        if self.rooks.manual_frame:
            return

        keys = SDL_GetKeyboardState(None)
        left_pressed = keys[SDL_GetScancodeFromKey(self.rooks.left_key)]
        right_pressed = keys[SDL_GetScancodeFromKey(self.rooks.right_key)]
        up_pressed = keys[SDL_GetScancodeFromKey(self.rooks.jump_key)]

        if not self.rooks.is_air_action and up_pressed and self.rooks.y == self.rooks.ground_y:
            self.rooks.y_velocity = 500
            self.rooks.is_air_action = True

        # 1. 공중 공격(액션)일 경우에만 중력 적용 및 착지 체크
        if self.rooks.is_air_action:
            self.rooks.apply_gravity()
            if self.rooks.check_platform_collision():
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
        if self.rooks.x < 20:
            self.rooks.x = 20
        elif self.rooks.x > 530:
            self.rooks.x = 530

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
                elif keys[SDL_GetScancodeFromKey(self.rooks.ult_key)] and self.rooks.mp >= 50:
                    self.rooks.state_machine.cur_state = self.rooks.ULT
                    self.rooks.ULT.enter(('ATTACK_TO_ULT', None))
                elif self.rooks.dir != 0:
                    self.rooks.state_machine.cur_state = self.rooks.RUN
                    self.rooks.RUN.enter(('ATTACK_TO_RUN', None))
                else:
                    self.rooks.state_machine.cur_state = self.rooks.IDLE
                    self.rooks.IDLE.enter(('ATTACK_TO_IDLE', None))
            return  # do() 종료

    def draw(self):
        frame_index = min(int(self.rooks.frame), 10)
        visual_y = self.rooks.y + 52
        if self.rooks.face_dir == -1:
            self.rooks.images['Attack'][frame_index].composite_draw(0, 'h', self.rooks.x, visual_y)
        else:
            self.rooks.images['Attack'][frame_index].draw(self.rooks.x, visual_y)

    def get_hitbox(self):
        frame = int(self.rooks.frame)
        x, y = self.rooks.x, self.rooks.y
        face_dir = self.rooks.face_dir

        # 프레임별 히트박스 정의 (캐릭터 중심 기준)
        hitbox_data = {
            0: None,  # 준비 동작
            1: (-16, -71 + 52, -8, -64 + 52),  # 75 ~ 80, 65 ~ 70
            2: (-6, -68 + 52, 1, -61 + 52),  # 80 -> 90, 65 -> 68
            3: (2, -65 + 52, 10, -56 + 52),  # 휘두르기 시작
            4: (10, -60 + 52, 18, -52 + 52),  # 93 -> 100, 72 -> 75
            5: (10, -60 + 52, 18, -52 + 52),  # 93 -> 100, 72 -> 75
            6: (10, -60 + 52, 18, -52 + 52),  # 감속 시작
            7: None,  # 공격 끝
            8: None,  # 회수 시작
            9: None,  # 회수 중
            10: None  # 대기 복귀
        }

        if frame not in hitbox_data or hitbox_data[frame] is None:
            return None

        dx, dy, width, height = hitbox_data[frame]

        if face_dir == 1:  # 오른쪽
            return x + dx, y + dy, x + width, y + height
        else:  # 왼쪽
            return x - width, y + dy, x - dx, y + height


class Skill:
    FRAMES_PER_ACTION = 14

    def __init__(self, rooks):
        self.dash_applied = False
        self.rooks = rooks

    def enter(self, e):
        self.rooks.hit_log.clear()  # 새 스킬 시작 시 로그 초기화
        self.dash_applied = False
        print('Skill State Entered with event:', e)

        # 공격 사운드 재생
        sound_manager.play_character_sound('Rooks', 'skill')

        # 공격 진입 시 현재 키보드 상태 확인하여 이동 방향 설정
        keys = SDL_GetKeyboardState(None)
        left_pressed = keys[SDL_GetScancodeFromKey(self.rooks.left_key)]
        right_pressed = keys[SDL_GetScancodeFromKey(self.rooks.right_key)]

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
        self.dash_applied = False

    def do(self):
        if self.rooks.manual_frame:
            return

        keys = SDL_GetKeyboardState(None)
        left_pressed = keys[SDL_GetScancodeFromKey(self.rooks.left_key)]
        right_pressed = keys[SDL_GetScancodeFromKey(self.rooks.right_key)]
        up_pressed = keys[SDL_GetScancodeFromKey(self.rooks.jump_key)]

        if not self.rooks.is_air_action and up_pressed and self.rooks.y == self.rooks.ground_y:
            self.rooks.y_velocity = 500
            self.rooks.is_air_action = True

        # 1. 공중 공격(액션)일 경우에만 중력 적용 및 착지 체크
        if self.rooks.is_air_action:
            self.rooks.apply_gravity()
            if self.rooks.check_platform_collision():
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
        if self.rooks.x < 20:
            self.rooks.x = 20
        elif self.rooks.x > 530:
            self.rooks.x = 530

        prev_frame = int(self.rooks.frame)
        self.rooks.frame = (self.rooks.frame + self.FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time)
        curr_frame = int(self.rooks.frame)


        # 4. 애니메이션 종료 체크
        if self.rooks.frame >= 13.9:
            if not self.dash_applied:
                self.rooks.x += 71 * self.rooks.face_dir  # 이동 거리 조정 (71 -> 30)

            if self.rooks.x < 20:
                self.rooks.x = 20
            elif self.rooks.x > 530:
                self.rooks.x = 530
            self.dash_applied = True
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
                elif keys[SDL_GetScancodeFromKey(self.rooks.ult_key)] and self.rooks.mp >= 50:
                    self.rooks.state_machine.cur_state = self.rooks.ULT
                    self.rooks.ULT.enter(('SKILL_TO_ULT', None))
                elif self.rooks.dir != 0:
                    self.rooks.state_machine.cur_state = self.rooks.RUN
                    self.rooks.RUN.enter(('SKILL_TO_RUN', None))
                else:
                    self.rooks.state_machine.cur_state = self.rooks.IDLE
                    self.rooks.IDLE.enter(('SKILL_TO_IDLE', None))
            return  # do() 종료

    def draw(self):
        frame_index = min(int(self.rooks.frame), 13)
        visual_y = self.rooks.y + 52
        if self.rooks.face_dir == -1:
            self.rooks.images['Skill'][frame_index].composite_draw(0, 'h', self.rooks.x, visual_y)
        else:
            self.rooks.images['Skill'][frame_index].draw(self.rooks.x, visual_y)

    def get_hitbox(self):
        frame = int(self.rooks.frame)
        x, y = self.rooks.x, self.rooks.y
        face_dir = self.rooks.face_dir

        # 프레임별 히트박스 정의 (캐릭터 중심 기준)
        hitbox_data = {
            0: None,  # 준비 동작
            1: None,  # 75 ~ 80, 65 ~ 70
            2: None,  # 80 -> 90, 65 -> 68
            3: None,  # 휘두르기 시작
            4: None,  # 93 -> 100, 72 -> 75
            5: None,  # 93 -> 100, 72 -> 75
            6: (-28, -90 + 52, 52, -40 + 52),  # 62 ~ 142, 45 ~ 95
            7: (-28, -90 + 52, 92, -40 + 52),  # 62 ~ 182, 45 ~ 95
            8: (15, -90 + 52, 92, -40 + 52),  # 105 ~ 182, 45 ~ 95
            9: (50, -90 + 52, 92, -40 + 52),  # 140 ~ 182, 45 ~ 95
            10: None,  # 대기 복귀
            11: None,
            12: None,
            13: None
        }

        if frame not in hitbox_data or hitbox_data[frame] is None:
            return None

        dx, dy, width, height = hitbox_data[frame]

        if face_dir == 1:  # 오른쪽
            return x + dx, y + dy, x + width, y + height
        else:  # 왼쪽
            return x - width, y + dy, x - dx, y + height

# 기력 50소모
class Ult:
    FRAMES_PER_ACTION = 15

    def __init__(self, rooks):
        self.rooks = rooks

    def enter(self, e):
        self.rooks.mp -= 50

        self.rooks.hit_log.clear()  # 새 스킬 시작 시 로그 초기화
        print('Ult State Entered with event:', e)

        # 궁극기 사운드 재생
        sound_manager.play_character_sound('Rooks', 'ult')

        # [FIX 1] 공중/지상 체크를 프레임 체크 밖으로 이동
        # Attack/Skill.enter와 동일한 구조
        if self.rooks.y > self.rooks.ground_y:
            self.rooks.is_air_action = True
        else:
            self.rooks.is_air_action = False
            self.rooks.y_velocity = 0

        self.rooks.x_locked = True
        self.rooks.frame = 0  # 항상 프레임 리셋
        self.rooks.dir = 0  # 궁극기는 항상 제자리

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
        if self.rooks.manual_frame:
            return

        # 공중 궁극기일 경우에만 중력 적용
        if self.rooks.is_air_action:
            self.rooks.apply_gravity()
            if self.rooks.check_platform_collision():
                pass

        # 3. 애니메이션 프레임 업데이트
        self.rooks.frame = (self.rooks.frame + self.FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time)

        # 4. 애니메이션 종료 체크
        if self.rooks.frame >= 14.9:
            self.rooks.frame = 0
            self.rooks.x_locked = False  # 애니메이션 끝났으니 잠금 해제

            # 종료 시점에 공중/지상 체크
            if self.rooks.is_air_action:
                # (아직 공중) -> JUMP 상태로 복귀
                self.rooks.state_machine.cur_state = self.rooks.JUMP
                self.rooks.JUMP.enter(('FINISH_AIR_ULT', None))
            else:
                # (지상) -> 키 눌림 상태에 따라 다음 상태 결정
                keys = SDL_GetKeyboardState(None)
                left_pressed = keys[SDL_GetScancodeFromKey(self.rooks.left_key)]
                right_pressed = keys[SDL_GetScancodeFromKey(self.rooks.right_key)]

                if keys[SDL_GetScancodeFromKey(self.rooks.jump_key)]:
                    self.rooks.state_machine.cur_state = self.rooks.JUMP
                    self.rooks.JUMP.enter(('FINISH_GROUND_ULT_JUMP', None))
                elif keys[SDL_GetScancodeFromKey(self.rooks.attack_key)]:
                    self.rooks.state_machine.cur_state = self.rooks.ATTACK
                    self.rooks.ATTACK.enter(('ULT_TO_ATTACK', None))
                elif keys[SDL_GetScancodeFromKey(self.rooks.skill_key)]:
                    self.rooks.state_machine.cur_state = self.rooks.SKILL
                    self.rooks.SKILL.enter(('ULT_TO_SKILL', None))
                elif keys[SDL_GetScancodeFromKey(self.rooks.ult_key)] and self.rooks.mp >= 50:
                    self.rooks.state_machine.cur_state = self.rooks.ULT
                    self.rooks.ULT.enter(('RE_ULT', None))
                elif left_pressed or right_pressed:
                    self.rooks.state_machine.cur_state = self.rooks.RUN
                    self.rooks.RUN.enter(('ULT_TO_RUN', None))
                else:
                    self.rooks.state_machine.cur_state = self.rooks.IDLE
                    self.rooks.IDLE.enter(('ULT_TO_IDLE', None))
            return  # do() 종료

    def draw(self):
        frame_index = min(int(self.rooks.frame), 14)
        visual_y = self.rooks.y + 52
        if self.rooks.face_dir == -1:
            self.rooks.images['Ult'][frame_index].composite_draw(0, 'h', self.rooks.x, visual_y)
        else:
            self.rooks.images['Ult'][frame_index].draw(self.rooks.x, visual_y)

    def get_hitbox(self):
        frame = int(self.rooks.frame)
        x, y = self.rooks.x, self.rooks.y
        face_dir = self.rooks.face_dir

        # 프레임별 히트박스 정의 (캐릭터 중심 기준)
        hitbox_data = {
            0: None,  # 준비 동작
            1: None,  # 75 ~ 80, 65 ~ 70
            2: None,  # 80 -> 90, 65 -> 68
            3: None,  # 휘두르기 시작
            4: None,  # 93 -> 100, 72 -> 75
            5: None,  # 93 -> 100, 72 -> 75
            6: None,  # 62 ~ 142, 45 ~ 95
            7: (-90, -70 + 52, 75, 85 + 52),  # 0 ~ 165, 65 ~ 220
            8: (-90, -70 + 52, 75, 85 + 52),  # 105 ~ 182, 45 ~ 95
            9: (-90, -70 + 52, 75, 85 + 52),  # 140 ~ 182, 45 ~ 95
            10: (-90, -70 + 52, 75, 85 + 52),  # 대기 복귀
            11: (-90, -70 + 52, 75, 85 + 52), # 여기까지
            12: None,
            13: None,
            14: None
        }

        if frame not in hitbox_data or hitbox_data[frame] is None:
            return None

        dx, dy, width, height = hitbox_data[frame]

        if face_dir == 1:  # 오른쪽
            return x + dx, y + dy, x + width, y + height
        else:  # 왼쪽
            return x - width, y + dy, x - dx, y + height


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

    def __init__(self, player_num=1, max_hp=100, mp_increase=10):
        # 디버그 모드 추가
        self.debug_mode = False  # F1 키로 토글
        self.manual_frame = False  # F2 키로 토글
        self.frame_step = 0.0  # 수동 프레임 값
        self.last_click_pos = None  # 마지막 클릭 좌표

        self.load_images()
        self.dir = 0
        self.frame = 0

        self.player_num = player_num

        # HP, MP 시스템 - 매개변수 사용
        self.max_hp = max_hp  # 하드코딩된 값 대신 매개변수 사용
        self.hp = max_hp
        self.max_mp = 100
        self.mp = 0
        self.mp_increase = mp_increase  # 매개변수 사용

        self.y_velocity = 0
        self.ground_y = 83

        self.is_air_action = False
        self.x_locked = False

        self.hit_log = set()  # 공격 히트 로그

        self.damage_values = {
            'Attack': 2,
            'Skill': 5,
            'Ult': 15
        }

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
                self.ATTACK : {},
                self.SKILL : {},
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
        return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == self.ult_key and self.mp >= 50

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
        if self.face_dir == 1:
            return self.x - 17, self.y - 24, self.x + 10, self.y + 4
        else:
            return self.x - 12, self.y - 24, self.x + 16, self.y + 4

    def get_text_position(self):
        """텍스트 표시용 좌표 반환 (캐릭터 머리 위)"""
        return self.x, self.y + 122

    def get_hitbox(self):
        return self.state_machine.cur_state.get_hitbox()

    def update(self):
        self.increase_mp()
        self.state_machine.update()

        if not self.is_air_action:
            self.check_platform_edge()

    def take_damage(self, attacker, attack_type):
        # 1. 데미지 계산
        if hasattr(attacker, 'calculate_damage'):
            # 공격자가 Stan인 경우
            damage = attacker.calculate_damage(attack_type, attacker.frame)
        else:
            # 일반적인 경우
            damage = attacker.damage_values.get(attack_type, 0)

        self.hp = max(0, self.hp - damage)
        print(f"P{self.player_num} took {damage} damage! HP: {self.hp}/{self.max_hp}")

        # 2. 넉백 처리
        # Stan은 knockback_values가 있지만, Rooks/Murloc은 없을 수 있으므로 처리
        knockback_dict = getattr(attacker, 'knockback_values', {})
        knockback = knockback_dict.get(attack_type, 10) # 기본 넉백 10

        if attacker.x < self.x:
            self.x += knockback
            if self.x > 530: self.x = 530
        else:
            self.x -= knockback
            if self.x < 20: self.x = 20

    def increase_mp(self):
        self.mp = min(self.max_mp, self.mp + self.mp_increase * game_framework.frame_time)

    def draw(self):
        self.state_machine.draw()

        # 캐릭터 바운딩 박스
        # draw_rectangle(*self.get_bb())

        # 히트박스
        # hitbox = self.get_hitbox()
        # if hitbox:
        #     from pico2d import draw_rectangle as draw_rect
        #     x1, y1, x2, y2 = hitbox
        #     draw_rect(x1, y1, x2, y2)

        # 디버그 정보 표시
        # if self.debug_mode:
        #     state_name = self.state_machine.cur_state.__class__.__name__
        #     frame_num = int(self.frame)
        #     max_frame = self.state_machine.cur_state.FRAMES_PER_ACTION - 1
        #
        #     # 상태 및 프레임 정보
        #     info1 = f"P{self.player_num} {state_name}"
        #     info2 = f"Frame: {frame_num}/{max_frame}"
        #     info3 = f"Pos: ({int(self.x)}, {int(self.y)})"
        #     info4 = f"FaceDir: {'RIGHT' if self.face_dir == 1 else 'LEFT'}"
        #
        #     if hitbox:
        #         info5 = f"Hitbox: ({int(x1)},{int(y1)})-({int(x2)},{int(y2)})"
        #     else:
        #         info5 = "Hitbox: None"
        #
        #     if self.manual_frame:
        #         info6 = "MANUAL MODE (</> to change frame)"
        #     else:
        #         info6 = "AUTO MODE (F2 to toggle)"
        #
        #     # 마우스 클릭 좌표
        #     if self.last_click_pos:
        #         info7 = f"Last Click: ({self.last_click_pos[0]}, {self.last_click_pos[1]})"
        #     else:
        #         info7 = "Last Click: None"
        #
        #     if not hasattr(self, 'font'):
        #         self.font = load_font('ENCR10B.TTF', 14)
        #
        #     y_offset = self.y + 60
        #     self.font.draw(self.x - 60, y_offset, info1, (255, 255, 0))
        #     self.font.draw(self.x - 60, y_offset - 15, info2, (255, 255, 0))
        #     self.font.draw(self.x - 60, y_offset - 30, info3, (255, 255, 0))
        #     self.font.draw(self.x - 60, y_offset - 45, info4, (255, 255, 0))
        #     self.font.draw(self.x - 60, y_offset - 60, info5, (255, 255, 0))
        #     self.font.draw(self.x - 60, y_offset - 75, info6, (0, 255, 255))
        #     self.font.draw(self.x - 60, y_offset - 90, info7, (255, 100, 100))
        #
        #     # 클릭 위치에 십자선 표시
        #     if self.last_click_pos:
        #         from pico2d import draw_line
        #         cx, cy = self.last_click_pos
        #         draw_line(cx - 10, cy, cx + 10, cy)
        #         draw_line(cx, cy - 10, cx, cy + 10)

    def handle_event(self, event):
        # 디버그 키 처리
        # if event.type == SDL_KEYDOWN:
        #     if event.key == SDLK_F1:
        #         self.debug_mode = not self.debug_mode
        #         print(f"Debug Mode: {'ON' if self.debug_mode else 'OFF'}")
        #         return
        #     elif event.key == SDLK_F2:
        #         self.manual_frame = not self.manual_frame
        #         if self.manual_frame:
        #             self.frame_step = 0.0
        #         print(f"Manual Frame Mode: {'ON' if self.manual_frame else 'OFF'}")
        #         return
        #     elif self.manual_frame:
        #         # 수동 프레임 진행
        #         if event.key == SDLK_PERIOD:  # '>' 키
        #             max_frame = self.state_machine.cur_state.FRAMES_PER_ACTION - 1
        #             self.frame_step = min(self.frame_step + 1, max_frame)
        #             self.frame = self.frame_step
        #             print(f"Frame: {int(self.frame_step)}")
        #             return
        #         elif event.key == SDLK_COMMA:  # '<' 키
        #             self.frame_step = max(self.frame_step - 1, 0)
        #             self.frame = self.frame_step
        #             print(f"Frame: {int(self.frame_step)}")
        #             return
        #
        # # 마우스 클릭 처리
        # if self.debug_mode and event.type == SDL_MOUSEBUTTONDOWN:
        #     # pico2d의 이벤트는 SDL2 이벤트를 래핑한 것
        #     # x, y 좌표는 event.x, event.y로 직접 접근
        #     mouse_x = getattr(event, 'x', 0)
        #     mouse_y = getattr(event, 'y', 0)
        #     self.last_click_pos = (mouse_x, 400 - mouse_y)  # Y좌표 반전
        #     print(f"Mouse Click: ({self.last_click_pos[0]}, {self.last_click_pos[1]})")
        #     return

        self.state_machine.handle_state_event(('INPUT', event))

    def set_platforms(self, platforms):
        """맵의 플랫폼 정보 설정"""
        self.platforms = platforms

    def check_platform_collision(self):
        """플랫폼과의 충돌 체크 및 착지 처리"""
        # 1. 플랫폼 데이터가 없으면 기본 바닥 체크만 수행
        if not hasattr(self, 'platforms'):
            return self.check_landing()

        # 2. 캐릭터의 현재 바운딩 박스 가져오기
        char_left, char_bottom, char_right, char_top = self.get_bb()

        # [중요] 아래로 떨어지는 중일 때만 플랫폼 위에 착지 가능 (상향 점프 중에는 통과)
        if self.y_velocity <= 0:
            for x1, y1, x2, y2 in self.platforms:
                # 1. X축 범위 체크 (AND 연산자로 수정: 캐릭터가 플랫폼 너비 안에 있어야 함)
                if char_right > x1 and char_left < x2:

                    # [FIX] 자석 현상 완화: 발이 플랫폼을 '뚫고 지나갔거나', '거의 닿았을 때'만 처리
                    # y2 - 10 : 발이 플랫폼 안쪽 10px 이내로 들어왔을 때 (뚫고 지나감 방지)
                    # y2 + 5  : 발이 플랫폼 위 5px 이내일 때 (살짝 떠 있어도 착지 판정)
                    # 이 값을 줄일수록 더 정교해지지만, 너무 줄이면 빠른 속도로 떨어질 때 뚫고 지나갈 수 있음
                    if y2 - 10 <= char_bottom <= y2 + 5:
                        self.y = y2 + 24
                        self.y_velocity = 0
                        self.is_air_action = False
                        self.ground_y = y2 + 24
                        return True

        # 3. 기본 바닥 체크 (맵의 최하단, 예: y=83)
        # 맵 밖으로 떨어지는 것을 방지
        if self.y <= 83:
            self.y = 83
            self.y_velocity = 0
            self.is_air_action = False
            self.ground_y = 83
            return True

        return False

    def check_platform_edge(self):
        """플랫폼 가장자리에서 벗어났는지 체크"""
        # 플랫폼 정보가 없으면 기본 바닥만 체크
        if not hasattr(self, 'platforms'):
            return

        char_left, char_bottom, char_right, char_top = self.get_bb()

        # 현재 내가 밟고 서 있는 플랫폼이 여전히 내 발 밑에 있는지 확인
        on_platform = False

        # 1. 기본 바닥(y=83) 위에 있다면 떨어질 일이 없음
        if self.y <= 83 + 5:  # 오차 범위 약간 허용
            return

        # 2. 플랫폼 리스트 검사
        for x1, y1, x2, y2 in self.platforms:
            # 현재 캐릭터의 높이가 이 플랫폼의 높이와 비슷한지 확인 (밟고 있는지)
            # y2 + 23은 캐릭터가 플랫폼 위에 서 있을 때의 중심 y좌표
            if abs(self.y - (y2 + 24)) < 10:
                # 높이는 맞는데, X축 범위도 맞는지 확인
                if char_right > x1 and char_left < x2:
                    on_platform = True
                    break  # 발 밑에 플랫폼이 있음 확인

        # 3. 발 밑에 아무것도 없다면 추락 시작
        if not on_platform:
            self.is_air_action = True  # 공중 상태로 전환
            self.ground_y = 83  # 떨어질 목표 지점을 일단 맨 바닥으로 초기화
            # (떨어지다가 다른 플랫폼에 걸리면 check_platform_collision에서 다시 잡음)