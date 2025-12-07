import random
from pico2d import *

import finish_mode
import game_framework
import game_world
import pause_mode
import sound_manager

from rooks import Rooks
from murloc import Murloc
from stan import Stan
from wilderness import Wilderness
from golden_temple import Temple
from player_ui import PlayerUI

# 선택된 캐릭터 저장
selected_p1 = None
selected_p2 = None

player1 = None
player2 = None
player1_ui = None
player2_ui = None
hp_setting = 1
mp_setting = 1

def set_selected_characters(p1, p2):
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
    global player1, player2, hp_setting, mp_setting, player1_ui , player2_ui, current_map

    hide_cursor()  # 마우스 커서 표시

    # HP/MP 설정값 계산 (1=10, 2=15, 3=20 등)
    max_hp_value = hp_setting * 50  # 1 : 50, 2 : 100, 3 : 150
    mp_increase_value = mp_setting * 3  # 또는 원하는 공식

    # 캐릭터 생성 시 설정값 전달
    player1 = Rooks(player_num=1, max_hp=max_hp_value, mp_increase=mp_increase_value)
    player2 = Rooks(player_num=2, max_hp=max_hp_value, mp_increase=mp_increase_value)

    # player1 생성 (항상 player_num=1)
    p1_choice = selected_p1
    if p1_choice == 'Random':
        p1_choice = random.choice(['Rooks', 'Murloc', 'Stan'])
        print(f"[Random] Player1 -> {p1_choice}")

    if p1_choice == 'Rooks':
        player1 = Rooks(player_num=1, max_hp=max_hp_value, mp_increase=mp_increase_value)
    elif p1_choice == 'Murloc':
        player1 = Murloc(player_num=1, max_hp=max_hp_value, mp_increase=mp_increase_value)
    else:
        player1 = Stan(player_num=1, max_hp=max_hp_value, mp_increase=mp_increase_value)

    game_world.add_object(player1, 1)

    # player2 생성 (항상 player_num=2)
    p2_choice = selected_p2
    if p2_choice == 'Random':
        p2_choice = random.choice(['Rooks', 'Murloc', 'Stan'])
        print(f"[Random] Player2 -> {p2_choice}")

    if p2_choice == 'Rooks':
        player2 = Rooks(player_num=2, max_hp=max_hp_value, mp_increase=mp_increase_value)
    elif p2_choice == 'Murloc':
        player2 = Murloc(player_num=2, max_hp=max_hp_value, mp_increase=mp_increase_value)
    else:
        player2 = Stan(player_num=2, max_hp=max_hp_value, mp_increase=mp_increase_value)

    game_world.add_object(player2, 1)

    # 배경
    map_choice = random.choice(['Wilderness', 'Temple'])
    current_map = 'map_choice'  # 현재 맵 저장
    print(f"Selected Map: {map_choice}")

    if map_choice == 'Wilderness':
        background = Wilderness()
        game_world.add_object(background, 0)
    else:
        background = Temple()
        game_world.add_object(background, 0)
        platforms = background.get_platforms()
        player1.set_platforms(platforms)
        player2.set_platforms(platforms)

    # UI 생성
    player1_ui = PlayerUI(player1, 1)
    player2_ui = PlayerUI(player2, 2)
    game_world.add_object(player1_ui, 2)
    game_world.add_object(player2_ui, 2)

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
    global player1, player2, current_map
    game_world.update()

    if not player1 or not player2:
        return

    player1_state = player1.state_machine.cur_state.__class__.__name__
    player2_state = player2.state_machine.cur_state.__class__.__name__

    # [FIX] Player 1 -> Player 2 공격 처리
    if check_collision(player1, player2):
        attack_id = f"{player1_state}_{id(player1.state_machine.cur_state)}"
        if attack_id not in player1.hit_log:
            # take_damage 호출 시 공격자(player1) 객체 자체를 넘깁니다.
            # 그러면 Stan 클래스 내부에서 프레임이나 거리를 계산할 수 있습니다.
            player2.take_damage(player1, player1_state)
            player1.hit_log.add(attack_id)
            print(f"[HIT] P1({player1_state}) -> P2")

    else:
        if player1_state not in ['Attack', 'Skill', 'Ult']:
            player1.hit_log.clear()

    # [FIX] Player 2 -> Player 1 공격 처리
    if check_collision(player2, player1):
        attack_id = f"{player2_state}_{id(player2.state_machine.cur_state)}"
        if attack_id not in player2.hit_log:
            player1.take_damage(player2, player2_state)
            player2.hit_log.add(attack_id)
            print(f"[HIT] P2({player2_state}) -> P1")

    else:
        if player2_state not in ['Attack', 'Skill', 'Ult']:
            player2.hit_log.clear()

    # 종료 체크: 어떤 플레이어라도 hp가 0 이하이면 finish_mode로 전환
    p1_hp = getattr(player1, 'hp', None)
    p2_hp = getattr(player2, 'hp', None)
    if (p1_hp is not None and p1_hp <= 0) or (p2_hp is not None and p2_hp <= 0):
        if player1.hp <= 0:
            # 실제 플레이한 캐릭터 타입 확인
            if type(player1).__name__ == 'Rooks':
                p1_actual = 'Rooks'
            elif type(player1).__name__ == 'Murloc':
                p1_actual = 'Murloc'
            else:
                p1_actual = 'Stan'
            if type(player2).__name__ == 'Rooks':
                p2_actual = 'Rooks'
            elif type(player2).__name__ == 'Murloc':
                p2_actual = 'Murloc'
            else:
                p2_actual = 'Stan'
            finish_mode.set_game_result(2, p1_actual, p2_actual, current_map)  # P2 승리
            game_framework.change_mode(finish_mode)
        elif player2.hp <= 0:
            if type(player1).__name__ == 'Rooks':
                p1_actual = 'Rooks'
            elif type(player1).__name__ == 'Murloc':
                p1_actual = 'Murloc'
            else:
                p1_actual = 'Stan'
            if type(player2).__name__ == 'Rooks':
                p2_actual = 'Rooks'
            elif type(player2).__name__ == 'Murloc':
                p2_actual = 'Murloc'
            else:
                p2_actual = 'Stan'
            finish_mode.set_game_result(1, p1_actual, p2_actual, current_map)  # P1 승리
            game_framework.change_mode(finish_mode)

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
    global hp_setting, mp_setting
    hp_setting = hp_set
    mp_setting = mp_set