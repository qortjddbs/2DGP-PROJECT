import random
from pico2d import *

import game_framework
import game_world
import pause_mode

from rooks import Rooks
from murloc import Murloc
from wilderness import Wilderness

rooks = None
murloc = None

def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.push_mode(pause_mode)
        else:
            rooks.handle_event(event)
            murloc.handle_event(event)

def init():
    global rooks
    global murloc

    rooks = Rooks()
    game_world.add_object(rooks, 1)

    murloc = Murloc()
    game_world.add_object(murloc, 1)

    wilderness = Wilderness()
    game_world.add_object(wilderness, 0)

    # 히트 추적용 딕셔너리 초기화
    rooks.hit_log = {}
    murloc.hit_log = {}


def check_collision(player1, player2):
    hitbox = player1.get_hitbox()
    bbox = player2.get_bb()

    if hitbox is None or bbox is None:
        return False

    # hitbox: (x1, y1, x2, y2)
    # bbox: (left, bottom, right, top)
    hx1, hy1, hx2, hy2 = hitbox
    bx1, by1, bx2, by2 = bbox

    # AABB 충돌 체크
    if hx1 < bx2 and hx2 > bx1 and hy1 < by2 and hy2 > by1:
        return True
    return False


def update():
    game_world.update()

    # 현재 공격 상태 확인
    rooks_state = rooks.state_machine.cur_state.__class__.__name__
    murloc_state = murloc.state_machine.cur_state.__class__.__name__

    # Rooks가 Murloc을 공격
    if check_collision(rooks, murloc):
        # 공격 ID 생성 (상태 + 진입 시간)
        attack_id = f"{rooks_state}_{id(rooks.state_machine.cur_state)}"

        if attack_id not in rooks.hit_log:
            frame = int(rooks.frame)
            print(f"[HIT] Rooks {rooks_state}(Frame {frame}) -> Murloc")
            rooks.hit_log[attack_id] = True
    else:
        # 충돌이 끝나면 로그 정리
        if rooks_state not in ['Attack', 'Skill', 'Ult']:
            rooks.hit_log.clear()

    # Murloc이 Rooks를 공격
    if check_collision(murloc, rooks):
        attack_id = f"{murloc_state}_{id(murloc.state_machine.cur_state)}"

        if attack_id not in murloc.hit_log:
            frame = int(murloc.frame)
            print(f"[HIT] Murloc {murloc_state}(Frame {frame}) -> Rooks")
            murloc.hit_log[attack_id] = True
    else:
        if murloc_state not in ['Attack', 'Skill', 'Ult']:
            murloc.hit_log.clear()

def draw():
    clear_canvas()
    game_world.render()
    update_canvas()


def finish():
    game_world.clear()

def pause():
    pass

def resume():
    pass


def set_player_stats(hp_set, mp_set):
    return None