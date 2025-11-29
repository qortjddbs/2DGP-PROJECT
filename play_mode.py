import random
from pico2d import *

import game_framework
import game_world
import pause_mode

from rooks import Rooks
from murloc import Murloc
from wilderness import Wilderness

# 선택된 캐릭터 저장
selected_p1 = None
selected_p2 = None

player1 = None
player2 = None

def set_selected_characters(p1, p2):
    """캐릭터 선택 모드에서 호출"""
    global selected_p1, selected_p2
    selected_p1 = p1
    selected_p2 = p2

def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.push_mode(pause_mode)
        else:
            if player1:
                player1.handle_event(event)
            if player2:
                player2.handle_event(event)

def init():
    global player1, player2

    # player1 생성 (항상 player_num=1)
    if selected_p1 == 'Rooks':
        player1 = Rooks(player_num=1)
    elif selected_p1 == 'Murloc':
        player1 = Murloc(player_num=1)
    else:
        print(f"[Warning] Player1 선택값이 없습니다. 기본값 Rooks 사용")
        player1 = Rooks(player_num=1)

    game_world.add_object(player1, 1)

    # player2 생성 (항상 player_num=2)
    if selected_p2 == 'Rooks':
        player2 = Rooks(player_num=2)
    elif selected_p2 == 'Murloc':
        player2 = Murloc(player_num=2)
    else:
        print(f"[Warning] Player2 선택값이 없습니다. 기본값 Murloc 사용")
        player2 = Murloc(player_num=2)

    game_world.add_object(player2, 1)

    wilderness = Wilderness()
    game_world.add_object(wilderness, 0)

    # 히트 추적용 딕셔너리 초기화
    if player1:
        player1.hit_log = {}
    if player2:
        player2.hit_log = {}


def check_collision(player_a, player_b):
    if not player_a or not player_b:
        return False

    hitbox = player_a.get_hitbox()
    bbox = player_b.get_bb()

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

    if not player1 or not player2:
        return

    # 현재 공격 상태 확인
    player1_state = player1.state_machine.cur_state.__class__.__name__
    player2_state = player2.state_machine.cur_state.__class__.__name__

    # player1이 player2를 공격했는지 체크
    if check_collision(player1, player2):
        attack_id = f"{player1_state}_{id(player1.state_machine.cur_state)}"
        if attack_id not in player1.hit_log:
            frame = int(player1.frame)
            print(f"[HIT] Player1 {player1_state}(Frame {frame}) -> Player2")
            player1.hit_log[attack_id] = True
    else:
        # 공격 상태가 아닐 때 로그 정리
        if player1_state not in ['Attack', 'Skill', 'Ult']:
            player1.hit_log.clear()

    # player2가 player1을 공격했는지 체크
    if check_collision(player2, player1):
        attack_id = f"{player2_state}_{id(player2.state_machine.cur_state)}"
        if attack_id not in player2.hit_log:
            frame = int(player2.frame)
            print(f"[HIT] Player2 {player2_state}(Frame {frame}) -> Player1")
            player2.hit_log[attack_id] = True
    else:
        if player2_state not in ['Attack', 'Skill', 'Ult']:
            player2.hit_log.clear()

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