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


def check_collision(player1, player2):
    """
    player1의 공격 히트박스와 player2의 피격 바운딩 박스 충돌 체크
    """
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

    # 충돌 체크 (플레이어 1이 플레이어 2를 공격)
    if check_collision(rooks, murloc):
        state_name = rooks.state_machine.cur_state.__class__.__name__
        frame = int(rooks.frame)
        print(f"[HIT] Rooks {state_name}(Frame {frame}) -> Murloc")

    # 충돌 체크 (플레이어 2가 플레이어 1을 공격)
    if check_collision(murloc, rooks):
        state_name = murloc.state_machine.cur_state.__class__.__name__
        frame = int(murloc.frame)
        print(f"[HIT] Murloc {state_name}(Frame {frame}) -> Rooks")


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

