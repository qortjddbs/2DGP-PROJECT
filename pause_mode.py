from pico2d import *
from sdl2 import SDL_QUIT, SDL_MOUSEBUTTONDOWN, SDL_BUTTON_LEFT
import mouse_manager

import game_framework
import game_world
import play_mode
import title_mode
from pause import Pause

cursor_image = None


def init():
    global pause, cursor_image
    cursor_image = load_image('./Background/cursor.png')
    hide_cursor()
    pause = Pause()
    game_world.add_object(pause, 2)

def finish():
    game_world.remove_object(pause)
    global cursor_image
    del cursor_image

def handle_events():
    global mouse_x, mouse_y
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_MOUSEMOTION:
            mouse_manager.update_position(event.x, 400 - 1 - event.y)
            mouse_x, mouse_y = mouse_manager.get_position()
        elif event.type == SDL_MOUSEBUTTONDOWN and event.button == SDL_BUTTON_LEFT:
            mouse_manager.update_position(event.x, 400 - 1 - event.y)
            mouse_x, mouse_y = mouse_manager.get_position()

            # 시작 버튼 클릭 영역 체크 (475, 300 중심)
            # x : 235 ~ 310, y : 185 ~ 205
            if 250 <= mouse_x <= 330 and 170 <= mouse_y <= 190:
                game_framework.pop_mode()

            elif 270 <= mouse_x <= 305 and 120 <= mouse_y <= 135:
                game_framework.pop_mode()
                game_framework.change_mode(title_mode)

def draw():
    clear_canvas()
    game_world.render()
    mouse_x, mouse_y = mouse_manager.get_position()
    cursor_image.draw(mouse_x, mouse_y)
    update_canvas()

def update():
    pass