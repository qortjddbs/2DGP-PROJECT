from pico2d import *

class PlayerUI:
    def __init__(self, player, player_num):
        self.player = player
        self.player_num = player_num

        # UI 이미지 로드
        self.hp_bar = load_image('./Background/Hp Setting/hp_bar.png')  # HP 바
        self.mp_bar = load_image('./Background/Mp Setting/mp_bar.png')  # MP 바
        self.label = load_image(f'./Background/player{player_num}.png')

        # UI 위치 설정
        if player_num == 1:
            self.label_x = 60
            self.bar_x = 120
        else:
            self.label_x = 490
            self.bar_x = 430

        self.hp_y = 380  # 450 -> 380 (화면 높이 400이므로)
        self.mp_y = 360  # 430 -> 360

        # 바의 최대 너비
        self.max_bar_width = 150

    def update(self):
        pass

    def draw(self):
        # 라벨 그리기
        self.label.draw(self.label_x, self.hp_y)

        # HP 비율 계산 및 그리기 (배경 위에 덮어씌우기)
        hp_ratio = self.player.hp / self.player.max_hp
        if hp_ratio > 0:
            hp_width = int(self.hp_bar.w * hp_ratio)
            # 왼쪽에서부터 hp_ratio만큼만 잘라서 그리기
            # clip_draw(소스 left, 소스 bottom, 소스 width, 소스 height, 화면 x, 화면 y)
            clip_x = self.bar_x - self.hp_bar.w // 2 + hp_width // 2
            self.hp_bar.clip_draw(0, 0, hp_width, self.hp_bar.h, clip_x, self.hp_y)

        # MP 비율 계산 및 그리기
        mp_ratio = self.player.mp / self.player.max_mp
        if mp_ratio > 0:
            mp_width = int(self.mp_bar.w * mp_ratio)
            clip_x = self.bar_x - self.mp_bar.w // 2 + mp_width // 2
            self.mp_bar.clip_draw(0, 0, mp_width, self.mp_bar.h, clip_x, self.mp_y)
