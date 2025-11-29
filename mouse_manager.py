mouse_x = 0
mouse_y = 0

def update_position(x, y):
    global mouse_x, mouse_y
    mouse_x = x
    mouse_y = y

def get_position():
    return mouse_x, mouse_y