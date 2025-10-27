from pico2d import load_image

class Rooks:
    def __init__(self):
        self.x, self.y = 400, 90
        self.face_dir = 1
        self.ani_speed = 3  # 몇 tick마다 이미지가 바뀌는지
        self.width = 183
        self.height = 179
        self.current = 1
        self.images = {i: load_image(f'Rooks/{i}.png') for i in range(1, 41)}

        # 상태 머신 추가
        self.state_machine = StateMaching(self)
        self.state_machine.start(idle)

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