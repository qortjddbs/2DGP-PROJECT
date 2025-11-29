from pico2d import *
import game_framework
import play_mode
import title_mode
import mouse_manager

background_image = None
logo_image = None
hp_image_1 = None
hp_image_2 = None
hp_image_3 = None
mp_image_1 = None
mp_image_2 = None
mp_image_3 = None
show_back_red = False
back_red_image = None
back_image = None
hp_set = 1
mp_set = 1
show_ok_red = False
ok_button_image = None
ok_button_red_image = None
cursor_image = None

def init():
    global background_image, logo_image, back_red_image, back_image, hp_set, mp_set, ok_button_image, ok_button_red_image
    global hp_image_1, hp_image_2, hp_image_3, mp_image_1, mp_image_2, mp_image_3, cursor_image
    background_image = load_image('./Background/시작배경.png')
    logo_image = load_image('./Background/로고.png')
    hp_image_1 = load_image('./Background/HP Setting/1.png')
    mp_image_1 = load_image('./Background/MP Setting/1.png')
    hp_image_2 = load_image('./Background/HP Setting/2.png')
    mp_image_2 = load_image('./Background/MP Setting/2.png')
    hp_image_3 = load_image('./Background/HP Setting/3.png')
    mp_image_3 = load_image('./Background/MP Setting/3.png')
    back_red_image = load_image('./Background/back(red).png')
    back_image = load_image('./Background/back.png')
    ok_button_image = load_image('./Background/ok.png')
    ok_button_red_image = load_image('./Background/ok(red).png')
    hp_set = 1
    mp_set = 1
    cursor_image = load_image('./Background/cursor.png')
    hide_cursor()

def finish():
    global hp_image_1, hp_image_2, hp_image_3, mp_image_1, mp_image_2, mp_image_3, cursor_image
    del cursor_image
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
    global hp_set, mp_set, show_back_red, show_ok_red, mouse_x, mouse_y
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.type == SDL_MOUSEMOTION:
            mouse_manager.update_position(event.x, 400 - 1 - event.y)

            if 485 <= mouse_x <= 545 and 5 <= mouse_y <= 25:
                show_back_red = True
            elif 260 <= mouse_x <= 310 and 95 <= mouse_y <= 120:
                show_ok_red = True
            else:
                show_back_red = False
                show_ok_red = False
        elif event.type == SDL_MOUSEBUTTONDOWN and event.button == SDL_BUTTON_LEFT:
            mouse_x, mouse_y = mouse_manager.get_position()
            if show_back_red:
                game_framework.pop_mode()
                game_framework.change_mode(title_mode)
            elif show_ok_red:
                # 설정 완료, 플레이 모드로 전환
                # play_mode.set_player_stats(hp_set, mp_set)
                game_framework.pop_mode()
                game_framework.change_mode(play_mode)
            if 180 <= mouse_x <= 260 and 150 <= mouse_y <= 220:
                hp_set += 1
                if hp_set > 3:
                    hp_set = 1
            elif 315 <= mouse_x <= 390 and 150 <= mouse_y <= 220:
                mp_set += 1
                if mp_set > 3:
                    mp_set = 1


def draw():
    clear_canvas()
    background_image.draw(277, 200)
    logo_image.clip_draw(0, 0, 372, 184, 110, 350, 200, 80)
    mouse_x, mouse_y = mouse_manager.get_position()
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
    cursor_image.draw(mouse_x, mouse_y)
    update_canvas()