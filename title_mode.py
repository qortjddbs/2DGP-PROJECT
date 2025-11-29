from pico2d import *
import game_framework
import play_mode
import rule_mode

font = None
background_image = None
logo_image = None
start_button_image = None
method_button_image = None


def init():
    global background_image, logo_image, start_button_image, method_button_image, font
    background_image = load_image('./Background/시작배경.png')
    logo_image = load_image('./Background/로고.png')
    start_button_image = load_image('./Background/시작버튼.png')
    method_button_image = load_image('./Background/방법버튼.png')
    font = load_font('ENCR10B.TTF', 20)


def finish():
    global background_image, logo_image, start_button_image, method_button_image, font
    del background_image
    del logo_image
    del start_button_image
    del method_button_image
    del font


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

            # 시작 버튼 클릭 영역 체크 (475, 300 중심)
            if 425 <= mouse_x <= 525 and 210 <= mouse_y <= 240:
                print("시작 버튼 클릭!")
                game_framework.change_mode(play_mode)
            elif 425 <= mouse_x <= 525 and 160 <= mouse_y <= 190:
                print("방법 버튼 클릭!")
                game_framework.change_mode(rule_mode)


def draw():
    clear_canvas()
    background_image.draw(277, 200)
    logo_image.draw(200, 200)
    start_button_image.draw(475, 225)
    method_button_image.draw(475, 175)
    update_canvas()

