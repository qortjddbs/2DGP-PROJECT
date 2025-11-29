from pico2d import *
import game_framework
import title_mode

rule_image = None
show_back_red = False
back_red_image = None
back_image = None
cursor_image = None
mouse_x, mouse_y = 0, 0

def init():
    global rule_image, back_red_image, back_image, show_back_red, cursor_image
    cursor_image = load_image('./Background/cursor.png')
    show_back_red = False
    rule_image = load_image('./Background/Key.png')
    back_red_image = load_image('./Background/back(red).png')
    back_image = load_image('./Background/back.png')
    hide_cursor()

def finish():
    global rule_image, back_red_image, back_image, cursor_image
    del cursor_image
    del back_red_image
    del rule_image
    del back_image
    show_cursor()


def update():
    pass

def handle_events():
    global show_back_red, mouse_x, mouse_y
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.type == SDL_MOUSEMOTION:
            # 마우스 클릭 좌표 계산
            mouse_x = event.x
            mouse_y = 400 - 1 - event.y  # 캔버스 높이가 400
            if 485 <= mouse_x <= 545 and 5 <= mouse_y <= 25:
                show_back_red = True
            else:
                show_back_red = False
        elif event.type == SDL_MOUSEBUTTONDOWN and event.button == SDL_BUTTON_LEFT:
            if show_back_red:
                game_framework.change_mode(title_mode)


def draw():
    clear_canvas()
    rule_image.clip_draw(0, 10, 550, 400, 277, 200)
    if show_back_red:
        back_red_image.draw(500, 30)
    else:
        back_image.draw(500, 30)
    cursor_image.draw(mouse_x, mouse_y)
    update_canvas()