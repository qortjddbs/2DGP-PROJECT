from pico2d import *
import game_framework

class PlayerUI:
    def __init__(self, player, player_num):
        self.player = player
        self.player_num = player_num

        # 플레이어가 어떤 캐릭터인지 확인
        self.character_type = self.player.__class__.__name__  # 'Rooks' 또는 'Murloc'

        # UI 이미지 로드
        self.hp_bar = load_image('./Background/Hp Setting/hp_bar.png')  # HP 바
        self.mp_bar = load_image('./Background/Mp Setting/mp_bar.png')  # MP 바
        self.label = load_image(f'./Background/player{player_num}.png')
        self.gray_bar = load_image('./Background/gray_bar.png')  # 회색 바 (배경)

        # 폰트 로드
        self.font = load_font('ENCR10B.TTF', 30)  # 크기 30
        self.mini_font = load_font('ENCR10B.TTF', 15)  # 크기 20

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

        # MP 회복 관련 (프레임 독립적)
        self.mp_recovery_rate = 5.0  # 초당 MP 회복량 (5 MP/초)

    def update(self):
        # MP 자동 회복 (프레임 독립적)
        if self.player.mp < self.player.max_mp:
            # frame_time만큼의 시간에 비례해서 MP 회복
            self.player.mp = min(
                self.player.mp + self.mp_recovery_rate * game_framework.frame_time,
                self.player.max_mp
            )
        else:
            self.player.mp = self.player.max_mp

    def draw(self):
        # 회색 바 그리기 (배경)
        if self.player_num == 1:
            self.gray_bar.draw(self.bar_x + 25, self.hp_y)
            self.gray_bar.draw(self.bar_x + 10, self.mp_y)
        else:
            self.gray_bar.draw(self.bar_x - 25, self.hp_y)
            self.gray_bar.draw(self.bar_x - 10, self.mp_y)
        # HP 비율 계산 및 그리기 (배경 위에 덮어씌우기)
        hp_ratio = self.player.hp / self.player.max_hp
        if hp_ratio > 0:
            hp_width = int(self.hp_bar.w * hp_ratio)
            clip_x = self.bar_x - self.hp_bar.w // 2 + hp_width // 2
            if self.player_num == 1:
                self.hp_bar.clip_draw(0, 0, hp_width, self.hp_bar.h, clip_x + 25, self.hp_y)
            else:
                self.hp_bar.clip_draw(0, 0, hp_width, self.hp_bar.h, clip_x - 25, self.hp_y)

        # MP 비율 계산 및 그리기
        mp_ratio = self.player.mp / self.player.max_mp
        if mp_ratio > 0:
            mp_width = int(self.mp_bar.w * mp_ratio)

            if self.player_num == 1:
                # P1: 왼쪽부터 차오름
                clip_x = self.bar_x - self.mp_bar.w // 2 + mp_width // 2
                self.mp_bar.clip_draw(0, 0, mp_width, self.mp_bar.h, clip_x + 16, self.mp_y)
            else:
                # P2: 오른쪽부터 차오름 (이미지의 오른쪽 끝부터 클리핑)
                clip_start_x = self.mp_bar.w - mp_width
                clip_x = self.bar_x + self.mp_bar.w // 2 - mp_width // 2
                self.mp_bar.clip_draw(clip_start_x, 0, mp_width, self.mp_bar.h, clip_x - 16, self.mp_y)

        # 라벨 그리기
        if self.player_num == 1:
            self.label.draw(self.label_x + 75, 372)
        else:
            self.label.draw(self.label_x - 75, 372)

        # P1, P2 텍스트를 플레이어 위치에 그리기
        text_x, text_y = self.player.get_text_position()

        if self.player_num == 1:
            # 화면 왼쪽 위에도 표시
            self.font.draw(self.text_x, self.text_y, 'P1', (255, 0, 0))

            # 플레이어 위치에도 표시 - 캐릭터별로 다르게 처리
            if self.character_type == 'Rooks':
                # Rooks일 때
                self.mini_font.draw(text_x - 10, text_y - 110, 'P1', (255, 0, 0))
            elif self.character_type == 'Murloc':
                # Murloc일 때
                self.mini_font.draw(text_x - 85, text_y - 20, 'P1', (255, 0, 0))
        else:
            # 화면 오른쪽 위에도 표시
            self.font.draw(self.text_x, self.text_y, 'P2', (0, 0, 255))

            # 플레이어 위치에도 표시 - 캐릭터별로 다르게 처리
            if self.character_type == 'Rooks':
                # Rooks일 때
                self.mini_font.draw(text_x - 10, text_y - 110, 'P2', (0, 0, 255))
            elif self.character_type == 'Murloc':
                # Murloc일 때
                self.mini_font.draw(text_x - 85, text_y - 20, 'P2', (0, 0, 255))
