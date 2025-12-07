from pico2d import *

class Temple:
    def __init__(self):
        self.image1 = load_image('./Maps/황금사원.png')
        self.image2 = load_image('./Maps/황금사원_꼭대기.png')

        # 플랫폼 정의 (x1, y1, x2, y2) - 바운딩 박스 형태
        self.platforms = [
            # 바닥
            (0, 0, 550, 55),
            # 바닥 1층
            (30, 55, 515, 77),
            # 바닥 2층
            (65, 78, 468, 99),
            # 바닥 3층
            (111, 100, 419, 122),
            # 좌측 플랫폼
            (30, 150, 150, 165),
            # 우측 플랫폼
            (350, 150, 500, 165),
            # 중앙 상단 플랫폼
            (200, 250, 350, 265),
        ]

    def get_platforms(self):
        """플레이어가 참조할 수 있도록 플랫폼 목록 반환"""
        return self.platforms

    def update(self):
        pass

    def draw(self):
        self.image1.draw(550/2, 400/2)
        self.image2.draw(112, 292)
        self.image2.draw(438, 292)

        # 디버그용 플랫폼 시각화
        for x1, y1, x2, y2 in self.platforms:
            draw_rectangle(x1, y1, x2, y2)