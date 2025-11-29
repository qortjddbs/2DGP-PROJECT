from pico2d import *
import game_framework
import title_mode

rule_image = None


def init():
    global rule_image
    rule_image = load_image('./Background/Key.png')


def finish():
    global rule_image
    del rule_image


def update():
    pass

def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.type == SDL_MOUSEBUTTONDOWN and event.button == SDL_BUTTON_LEFT:
            # 마우스 클릭 좌표 계산
            mouse_x = event.x
            mouse_y = 400 - 1 - event.y  # 캔버스 높이가 400
            print(f"마우스 클릭: ({mouse_x}, {mouse_y})")

            if 10 <= mouse_x <= 60 and 370 <= mouse_y <= 390:
                game_framework.change_mode(title_mode)
                print(f"Back버튼 클릭!")

def draw():
    clear_canvas()
    rule_image.draw(277, 200)
    update_canvas()

