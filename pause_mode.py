from pico2d import get_events, clear_canvas, update_canvas
from sdl2 import SDL_QUIT, SDL_MOUSEBUTTONDOWN, SDL_BUTTON_LEFT

import game_framework
import game_world
import play_mode
import title_mode
from pause import Pause


def init():
    global pause
    pause = Pause()
    game_world.add_object(pause, 2)

def finish():
    game_world.remove_object(pause)

def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_MOUSEBUTTONDOWN and event.button == SDL_BUTTON_LEFT:
            # 마우스 클릭 좌표 계산
            mouse_x = event.x
            mouse_y = 400 - 1 - event.y  # 캔버스 높이가 400
            print(f"마우스 클릭: ({mouse_x}, {mouse_y})")

            # 시작 버튼 클릭 영역 체크 (475, 300 중심)
            if 235 <= mouse_x <= 310 and 185 <= mouse_y <= 205:
                game_framework.pop_mode()

            elif 255 <= mouse_x <= 290 and 135 <= mouse_y <= 150:
                game_framework.pop_mode()
                game_framework.change_mode(title_mode)

def draw():
    clear_canvas()
    game_world.render()
    update_canvas()

def update():
    game_world.update()