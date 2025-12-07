from pico2d import *
import game_framework
import rule_mode
import setting_mode
import mouse_manager
import game_world
import sound_manager

font = None
background_image = None
logo_image = None
start_button_image = None
method_button_image = None
cursor_image = None

def init():
    # 커밋 되나?
    global background_image, logo_image, start_button_image, method_button_image, font, cursor_image
    background_image = load_image('./Background/시작배경.png')
    logo_image = load_image('./Background/로고.png')
    start_button_image = load_image('./Background/시작버튼.png')
    method_button_image = load_image('./Background/방법버튼.png')
    font = load_font('ENCR10B.TTF', 20)
    cursor_image = load_image('./Background/cursor.png')
    import pygame
    pygame_mouse_pos = pygame.mouse.get_pos()
    mouse_manager.update_position(pygame_mouse_pos[0], 400 - 1 - pygame_mouse_pos[1])
    hide_cursor()

    # 사운드 초기화 (한 번만 초기화됨)
    sound_manager.init()
    # BGM 재생 (이미 재생 중이면 다시 시작하지 않음)
    sound_manager.play_title_bgm()

def finish():
    global background_image, logo_image, start_button_image, method_button_image, font, cursor_image
    del background_image
    del logo_image
    del start_button_image
    del method_button_image
    del font
    del cursor_image

    # 사운드 정리는 게임 종료 시에만
    pass

def update():
    pass

def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.type == SDL_MOUSEMOTION:
            mouse_manager.update_position(event.x, 400 - 1 - event.y)
        elif event.type == SDL_MOUSEBUTTONDOWN and event.button == SDL_BUTTON_LEFT:
            mouse_manager.update_position(event.x, 400 - 1 - event.y)
            mouse_x, mouse_y = mouse_manager.get_position()

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
    mouse_x, mouse_y = mouse_manager.get_position()
    cursor_image.draw(mouse_x, mouse_y)
    update_canvas()
