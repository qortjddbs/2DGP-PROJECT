from pico2d import *

class PlayerUI:
    def __init__(self, player, player_num):
        self.player = player
        self.player_num = player_num

        # UI 이미지 로드
        self.hp_bar = load_image('./Background/Hp Setting/hp_bar.png')  # HP 바
        self.mp_bar = load_image('./Background/Mp Setting/mp_bar.png')  # MP 바
        self.label = load_image(f'./Background/player{player_num}.png')

        # 폰트 로드
        self.font = load_font('ENCR10B.TTF', 30)  # 크기 30
        self.mini_font = load_font('ENCR10B.TTF', 20)  # 크기 20

        # UI 위치 설정
        if player_num == 1:
            self.label_x = 60
            self.bar_x = 120
            self.text_x = 0  # P1 텍스트 위치
        else:
            self.label_x = 490
            self.bar_x = 430
            self.text_x = 515  # P2 텍스트 위치

        self.hp_y = 380  # 450 -> 380 (화면 높이 400이므로)
        self.mp_y = 360  # 430 -> 360
        self.text_y = 380  # 텍스트 y 위치

        # 바의 최대 너비
        self.max_bar_width = 150

    def update(self):
        pass

    def draw(self):
        # HP 비율 계산 및 그리기 (배경 위에 덮어씌우기)
        hp_ratio = self.player.hp / self.player.max_hp
        if hp_ratio > 0:
            hp_width = int(self.hp_bar.w * hp_ratio)
            # 왼쪽에서부터 hp_ratio만큼만 잘라서 그리기
            # clip_draw(소스 left, 소스 bottom, 소스 width, 소스 height, 화면 x, 화면 y)
            clip_x = self.bar_x - self.hp_bar.w // 2 + hp_width // 2
            if self.player_num == 1:
                self.hp_bar.clip_draw(0, 0, hp_width, self.hp_bar.h, clip_x + 25, self.hp_y)
            else:
                self.hp_bar.clip_draw(0, 0, hp_width, self.hp_bar.h, clip_x - 25, self.hp_y)

        # MP 비율 계산 및 그리기
        mp_ratio = self.player.mp / self.player.max_mp
        if mp_ratio > 0:
            mp_width = int(self.mp_bar.w * mp_ratio)
            clip_x = self.bar_x - self.mp_bar.w // 2 + mp_width // 2
            if self.player_num == 1:
                self.mp_bar.clip_draw(0, 0, mp_width, self.mp_bar.h, clip_x + 16, self.mp_y)
            else:
                self.mp_bar.clip_draw(0, 0, mp_width, self.mp_bar.h, clip_x - 16, self.mp_y)

        # 라벨 그리기
        if self.player_num == 1:
            self.label.draw(self.label_x + 75, 372)
        else:
            self.label.draw(self.label_x - 75, 372)

        # P1, P2 텍스트를 플레이어 위치에 그리기
        # font.draw(x, y, text, (r, g, b))
        if self.player_num == 1:
            # 화면 왼쪽 위에도 표시
            self.font.draw(self.text_x, self.text_y, 'P1', (255, 0, 0))
            # 플레이어 위치에도 표시
            self.mini_font.draw(self.player.x - 5, self.player.y + 20, 'P1', (255, 0, 0))
        else:
            # 화면 오른쪽 위에도 표시
            self.font.draw(self.text_x, self.text_y, 'P2', (0, 0, 255))
            # 플레이어 위치에도 표시
            self.mini_font.draw(self.player.x - 5, self.player.y + 20, 'P2', (0, 0, 255))
