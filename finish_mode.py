from pico2d import *
import game_framework
import play_mode
import title_mode
import mouse_manager

background_image = None
show_back_red = False
back_red_image = None
back_image = None
cursor_image = None
player1_name_image = None
player2_name_image = None
rooks_pick_image = None
murloc_pick_image = None
font = None

winner = None
p1 = None
p2 = None

def set_game_result(winner_player, player1, player2):
    global winner, p1, p2
    p1 = player1
    p2 = player2
    winner = winner_player

def init():
    global background_image, back_red_image, back_image, show_back_red, cursor_image
    global player1_name_image, player2_name_image
    global rooks_pick_image, murloc_pick_image
    global p1, p2, font

    player1_name_image = load_image('./Character/p1.png')
    player2_name_image = load_image('./Character/p2.png')
    cursor_image = load_image('./Background/cursor.png')
    background_image = load_image('./Background/시작배경.png')
    back_red_image = load_image('./Background/back(red).png')
    back_image = load_image('./Background/back.png')
    rooks_pick_image = load_image('./Character/Rooks/rooks_pick.png')
    murloc_pick_image = load_image('./Character/Murloc/murloc_pick.png')
    show_back_red = False

    # 폰트 로드
    font = load_font('ENCR10B.TTF', 30)

def finish():
    global background_image, back_red_image, back_image, cursor_image, rooks_pick_image, murloc_pick_image
    global player1_name_image, player2_name_image, font
    del player1_name_image
    del player2_name_image
    del cursor_image
    del back_red_image
    del back_image
    del background_image
    del rooks_pick_image
    del murloc_pick_image

    if font:
        del font


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
            if 260 <= mouse_x <= 320 and 0 <= mouse_y <= 20:
                show_back_red = True
            else:
                show_back_red = False
        elif event.type == SDL_MOUSEBUTTONDOWN and event.button == SDL_BUTTON_LEFT:
            mouse_manager.update_position(event.x, 400 - 1 - event.y)
            if show_back_red:
                game_framework.pop_mode()
                game_framework.change_mode(title_mode)


def draw():
    clear_canvas()
    background_image.draw(277, 200)
    if show_back_red:
        back_red_image.draw(275, 20) # type : ignore

    if not show_back_red:
        back_image.draw(275, 20)  # type : ignore

    if p1:
        if p1 == 'Rooks':
            rooks_pick_image.draw(120, 270)
        else:
            murloc_pick_image.draw(120, 270)

    if p2:
        if p2 == 'Rooks':
            rooks_pick_image.draw(430, 270)
        else:
            murloc_pick_image.draw(430, 270)

    player1_name_image.draw(120, 200)
    player2_name_image.draw(430, 200)

    # P1, P2 텍스트 출력 (P1은 빨간색, P2는 파란색)
    if font:
        font.draw(177, 198, "1P", (255, 0, 0))  # 빨간색
        font.draw(335, 198, "2P", (0, 0, 255))  # 파란색

    mouse_x, mouse_y = mouse_manager.get_position()
    cursor_image.draw(mouse_x, mouse_y)
    update_canvas()

def pause():
    pass

def resume():
    pass