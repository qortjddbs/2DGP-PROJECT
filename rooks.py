from pico2d import load_image

class Rooks:
    def __init__(self):
        self.x, self.y = 400, 90
        self.face_dir = 1
        self.tick = 0       # 애니메이션 타이머
        self.ani_speed = 3  # 몇 tick마다 이미지가 바뀌는지
        self.width = 183
        self.height = 179
        self.current = 1
        self.images = {
            1: load_image('Rooks/1.png'),
            2: load_image('Rooks/2.png'),
            3: load_image('Rooks/3.png'),
            4: load_image('Rooks/4.png'),
            5: load_image('Rooks/5.png'),
            6: load_image('Rooks/6.png'),
            7: load_image('Rooks/7.png'),
            8: load_image('Rooks/8.png'),
            9: load_image('Rooks/9.png'),
            10: load_image('Rooks/10.png'),
            11: load_image('Rooks/11.png'),
            12: load_image('Rooks/12.png'),
            13: load_image('Rooks/13.png'),
            14: load_image('Rooks/14.png'),
            15: load_image('Rooks/15.png'),
            16: load_image('Rooks/16.png'),
            17: load_image('Rooks/17.png'),
            18: load_image('Rooks/18.png'),
            19: load_image('Rooks/19.png'),
            20: load_image('Rooks/20.png'),
            21: load_image('Rooks/21.png'),
            22: load_image('Rooks/22.png'),
            23: load_image('Rooks/23.png'),
            24: load_image('Rooks/24.png'),
            25: load_image('Rooks/25.png'),
            26: load_image('Rooks/26.png'),
            27: load_image('Rooks/27.png'),
            28: load_image('Rooks/28.png'),
            29: load_image('Rooks/29.png'),
            30: load_image('Rooks/30.png'),
            31: load_image('Rooks/31.png'),
            32: load_image('Rooks/32.png'),
            33: load_image('Rooks/33.png'),
            34: load_image('Rooks/34.png'),
            35: load_image('Rooks/35.png'),
            36: load_image('Rooks/36.png'),
            37: load_image('Rooks/37.png'),
            38: load_image('Rooks/38.png'),
            39: load_image('Rooks/39.png'),
            40: load_image('Rooks/40.png'),
        }
        self.max_index = max(self.images.keys())

    def update(self):
        # 애니메이션 타이머 증가 -> 일정 tick마다 이미지 인덱스 증가
        self.tick += 1
        if self.tick >= self.ani_speed:
            self.tick = 0
            self.current += 1
            if self.current > self.max_index:
                self.current = 1

    def set_image(self, idx):
        if idx in self.images:
            self.current = idx
            self.tick = 0

    def draw(self):
        img = self.images[self.current]
        img.clip_draw(0, 0, self.width, self.height, self.x, self.y)
        pass