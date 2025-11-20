from pico2d import open_canvas, delay, close_canvas
import game_framework
import title_mode
import play_mode

open_canvas(550, 400)
game_framework.run(title_mode)
close_canvas()

