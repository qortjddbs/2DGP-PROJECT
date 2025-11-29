from pico2d import *
import game_framework
import title_mode
import mouse_manager

rule_image = None
show_back_red = False
back_red_image = None
back_image = None
cursor_image = None

def init():
    global rule_image, back_red_image, back_image, show_back_red, cursor_image
    cursor_image = load_image('./Background/cursor.png')
    show_back_red = False
    rule_image = load_image('./Background/Key.png')
    back_red_image = load_image('./Background/back(red).png')
    back_image = load_image('./Background/back.png')
    import pygame
    pygame_mouse_pos = pygame.mouse.get_pos()
    mouse_manager.update_position(pygame_mouse_pos[0], 400 - 1 - pygame_mouse_pos[1])
    hide_cursor()

def finish():
    global rule_image, back_red_image, back_image, cursor_image
    del cursor_image
    del back_red_image
    del rule_image
    del back_image


def update():
    pass

def handle_events():
    global show_back_red
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.type == SDL_MOUSEMOTION:
            mouse_manager.update_position(event.x, 400 - 1 - event.y)
            mouse_x, mouse_y = mouse_manager.get_position()
            if 485 <= mouse_x <= 545 and 5 <= mouse_y <= 25:
                show_back_red = True
            else:
                show_back_red = False
        elif event.type == SDL_MOUSEBUTTONDOWN and event.button == SDL_BUTTON_LEFT:
            mouse_manager.update_position(event.x, 400 - 1 - event.y)
            mouse_x, mouse_y = mouse_manager.get_position()
            if show_back_red:
                game_framework.pop_mode()
                game_framework.change_mode(title_mode)


def draw():
    clear_canvas()
    rule_image.clip_draw(0, 10, 550, 400, 277, 200)
    if show_back_red:
        back_red_image.draw(500, 30)
    else:
        back_image.draw(500, 30)
    mouse_x, mouse_y = mouse_manager.get_position()
    cursor_image.draw(mouse_x, mouse_y)
    update_canvas()