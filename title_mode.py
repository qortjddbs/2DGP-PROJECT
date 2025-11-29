from pico2d import *
import game_framework
import rule_mode
import setting_mode

font = None
background_image = None
logo_image = None
start_button_image = None
method_button_image = None
cursor_image = None
mouse_x, mouse_y = 0, 0

def init():
    global background_image, logo_image, start_button_image, method_button_image, font, cursor_image
    background_image = load_image('./Background/시작배경.png')
    logo_image = load_image('./Background/로고.png')
    start_button_image = load_image('./Background/시작버튼.png')
    method_button_image = load_image('./Background/방법버튼.png')
    font = load_font('ENCR10B.TTF', 20)
    cursor_image = load_image('./Background/cursor.png')
    hide_cursor()

def finish():
    global background_image, logo_image, start_button_image, method_button_image, font, cursor_image
    del background_image
    del logo_image
    del start_button_image
    del method_button_image
    del font
    del cursor_image

def update():
    pass

def handle_events():
    global mouse_x, mouse_y
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.type == SDL_MOUSEMOTION:
            # 마우스 클릭 좌표 계산
            mouse_x = event.x
            mouse_y = 400 - 1 - event.y
        elif event.type == SDL_MOUSEBUTTONDOWN and event.button == SDL_BUTTON_LEFT:
            # 마우스 클릭 좌표 계산
            mouse_x = event.x
            mouse_y = 400 - 1 - event.y  # 캔버스 높이가 400

            # 시작 버튼 클릭 영역 체크 (475, 300 중심)
            if 435 <= mouse_x <= 540 and 190 <= mouse_y <= 225:
                game_framework.pop_mode()
                game_framework.change_mode(setting_mode)
            elif 440 <= mouse_x <= 540 and 140 <= mouse_y <= 175:
                game_framework.pop_mode()
                game_framework.change_mode(rule_mode)


def draw():
    clear_canvas()
    background_image.draw(277, 200)
    logo_image.draw(200, 200)
    start_button_image.draw(475, 225)
    method_button_image.draw(475, 175)
    cursor_image.draw(mouse_x, mouse_y)
    update_canvas()

