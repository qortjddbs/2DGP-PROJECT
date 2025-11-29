from pico2d import *
import game_framework
import play_mode
import setting_mode
import title_mode

background_image = None
logo_image = None

def init():
    global background_image, logo_image
    background_image = load_image('./Background/시작배경.png')
    logo_image = load_image('./Background/로고.png')

def finish():
    global hp_image_1, hp_image_2, hp_image_3, mp_image_1, mp_image_2, mp_image_3
    global background_image, logo_image, back_red_image, back_image, ok_button_image, ok_button_red_image
    del background_image
    del logo_image
    del hp_image_1
    del hp_image_2
    del hp_image_3
    del mp_image_1
    del mp_image_2
    del mp_image_3
    del back_red_image
    del back_image
    del ok_button_image
    del ok_button_red_image

def update():
    pass

def handle_events():
    global hp_set, mp_set, show_back_red, show_ok_red
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

            if 470 <= mouse_x <= 530 and 20 <= mouse_y <= 40:
                show_back_red = True
            elif 245 <= mouse_x <= 300 and 110 <= mouse_y <= 135:
                show_ok_red = True
            else:
                show_back_red = False
                show_ok_red = False
        elif event.type == SDL_MOUSEBUTTONDOWN and event.button == SDL_BUTTON_LEFT:
            if show_back_red:
                game_framework.pop_mode()
                game_framework.change_mode(title_mode)
            elif show_ok_red:
                # 설정 완료, 플레이 모드로 전환
                # play_mode.set_player_stats(hp_set, mp_set)
                game_framework.pop_mode()
                game_framework.change_mode(play_mode)
            mouse_x = event.x
            mouse_y = 400 - 1 - event.y  # 캔버스 높이가 400
            if 170 <= mouse_x <= 240 and 160 <= mouse_y <= 235:
                hp_set += 1
                if hp_set > 3:
                    hp_set = 1
            elif 300 <= mouse_x <= 370 and 160 <= mouse_y <= 235:
                mp_set += 1
                if mp_set > 3:
                    mp_set = 1


def draw():
    clear_canvas()
    background_image.draw(277, 200)
    logo_image.clip_draw(0, 0, 372, 184, 110, 350, 200, 80)
    if hp_set == 1:
        hp_image_1.draw(205, 200)
    elif hp_set == 2:
        hp_image_2.draw(205, 200)
    else:
        hp_image_3.draw(205, 200)
    if mp_set == 1:
        mp_image_1.draw(335, 200)
    elif mp_set == 2:
        mp_image_2.draw(335, 200)
    else:
        mp_image_3.draw(335, 200)
    if show_back_red:
        back_red_image.draw(500, 30)
    else:
        back_image.draw(500, 30)
    if show_ok_red:
        ok_button_red_image.draw(270, 120)
    else:
        ok_button_image.draw(270, 120)
    update_canvas()