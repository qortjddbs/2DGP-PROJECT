import random
from pico2d import *

import game_framework
import game_world
import pause_mode

from rooks import Rooks
from murloc import Murloc
from wilderness import Wilderness

rooks = None
murloc = None

def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.push_mode(pause_mode)
        else:
            rooks.handle_event(event)
            murloc.handle_event(event)

def init():
    global rooks
    global murloc

    rooks = Rooks()
    game_world.add_object(rooks, 1)

    murloc = Murloc()
    game_world.add_object(murloc, 1)

    wilderness = Wilderness()
    game_world.add_object(wilderness, 0)


def update():
    game_world.update()


def draw():
    clear_canvas()
    game_world.render()
    update_canvas()


def finish():
    game_world.clear()

def pause():
    pass

def resume():
    pass

