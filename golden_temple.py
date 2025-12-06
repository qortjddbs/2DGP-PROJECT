from pico2d import *

class Temple:
    def __init__(self):
        self.image1 = load_image('./Maps/황금사원.png')
        self.image2 = load_image('./Maps/황금사원_꼭대기.png')



    def update(self):
        pass

    def draw(self):
        self.image1.draw(550/2, 400/2)
        self.image2.draw(112, 292)
        self.image2.draw(438, 292)