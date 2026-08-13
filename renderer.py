# 화면 렌더링만 전담하는 파일
# 게임 로직(snake_game.py)과 완전히 분리되어 있어
# 그리기 방식을 바꿔도 게임 로직에 영향을 주지 않음
#
# 뱀의 각 칸이 머리인지 몸통인지 코너인지는 여기서 앞뒤 칸을 비교해 알아낸다.
# 덕분에 snake_game.py는 여전히 좌표 리스트만 넘겨주면 된다.

import os
import math
import pygame
from settings import (CELL_SIZE, WIDTH, HEIGHT, BG, GREEN, WHITE,
                      FONT_BIG, FONT_SMALL,
                      BOARD, BOARD_DOT, FRAME, FRAME_LINE, VIGNETTE)

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

# 진행 방향 → 회전 각도. pygame.transform.rotate는 양수가 반시계 방향
# 원본 스프라이트는 모두 "오른쪽"을 기준으로 그려져 있음
DIR_ANGLE = {(1, 0): 0, (0, -1): 90, (-1, 0): 180, (0, 1): 270}

# 코너가 이어지는 두 방향의 조합 → 회전 각도
# 원본 코너는 왼쪽과 아래가 열려 있음
CORNER_ANGLE = {
    frozenset({(-1, 0), (0,  1)}):   0,   # 왼쪽 + 아래
    frozenset({(0,  1), (1,  0)}):  90,   # 아래 + 오른쪽
    frozenset({(1,  0), (0, -1)}): 180,   # 오른쪽 + 위
    frozenset({(0, -1), (-1, 0)}): 270,   # 위 + 왼쪽
}


def _delta(a, b):
    # b에서 a로 향하는 방향 벡터
    return (a[0] - b[0], a[1] - b[1])


class Renderer:
    def __init__(self, screen):
        self.screen = screen
        # SysFont는 콤마로 구분한 이름 중 PC에 설치된 첫 폰트를 사용
        # 맑은 고딕 등이 있으면 한글 닉네임도 깨지지 않고 표시됨
        KOREAN_FONTS = "malgungothic,applegothic,notosanscjkkr,arial"
        self.font   = pygame.font.SysFont(KOREAN_FONTS, FONT_BIG)
        self.small  = pygame.font.SysFont(KOREAN_FONTS, FONT_SMALL)

        # 이미지는 시작할 때 한 번만 읽는다.
        # 매 프레임 load하면 그릴 때마다 디스크를 읽어 게임이 느려짐
        # convert_alpha()는 화면과 같은 픽셀 형식으로 바꿔 blit을 빠르게 함
        self.head   = self._load("sprites", "snake_head.png")
        self.body   = self._load("sprites", "snake_body.png")
        self.corner = self._load("sprites", "snake_corner.png")
        self.tail   = self._load("sprites", "snake_tail.png")
        self.food   = self._load("sprites", "food_apple.png")

        # 판 배경도 시작할 때 한 장으로 만들어 둔다
        self.board = self._build_board()

    def _load(self, *parts):
        return pygame.image.load(os.path.join(ASSETS, *parts)).convert_alpha()

    def _build_board(self):
        # 판 배경을 이미지 파일 대신 여기서 계산해서 그린다.
        #
        # 처음엔 칸마다 판을 깐 격자 무늬 타일을 썼는데, 400칸이 반복되면서
        # 배경이 물러나지 않고 뱀 하나 사과 하나와 시선을 다퉜다.
        # 지금은 평평한 바탕에 칸 모서리 점만 남겨 위치만 가늠할 수 있게 했다.
        #
        # 가장자리를 어둡게 하는 비네팅은 화면 중심에서의 거리에 따라 값이
        # 달라져서 반복 타일로는 만들 수 없다. 그래서 이미지 파일이 사라졌고,
        # 덕분에 격자 크기를 바꿔도 배경은 알아서 따라온다.
        board = pygame.Surface((WIDTH, HEIGHT))
        board.fill(BOARD)

        # 칸 모서리에 점 하나씩. 사과와 머리가 같은 줄인지 눈으로 재는 용도
        for y in range(0, HEIGHT, CELL_SIZE):
            for x in range(0, WIDTH, CELL_SIZE):
                board.set_at((x, y), BOARD_DOT)

        board.blit(self._vignette(), (0, 0))

        # 판이 창 끝까지 흘러넘치지 않도록 테두리를 두름
        # 배경에 그리므로 가장자리 칸을 지나는 뱀이 위에 덮인다
        pygame.draw.rect(board, FRAME, (0, 0, WIDTH, HEIGHT), 5)
        pygame.draw.rect(board, FRAME_LINE, (5, 5, WIDTH - 10, HEIGHT - 10), 1)
        return board

    def _vignette(self):
        # 640x640 픽셀을 하나씩 계산하면 40만 번이라 시작이 눈에 띄게 느려진다.
        # 작게 계산한 뒤 부드럽게 확대하면 결과는 같고 훨씬 빠름.
        # 너무 작게 잡으면(48 등) 확대할 때 중앙에 사각 얼룩이 남아 128로 둠
        small = 128
        shade = pygame.Surface((small, small), pygame.SRCALPHA)
        c = (small - 1) / 2.0
        far = math.hypot(c, c)
        for y in range(small):
            for x in range(small):
                t = (math.hypot(x - c, y - c) / far) ** 1.4
                shade.set_at((x, y), (0, 0, 0, int(VIGNETTE * min(1.0, t))))
        return pygame.transform.smoothscale(shade, (WIDTH, HEIGHT))

    def _segment(self, snake, i):
        # snake[i]가 어떤 모양이어야 하는지 판단해서 (이미지, 회전각)을 반환
        # snake[0]이 머리, 마지막이 꼬리
        cur = snake[i]

        if i == 0:
            # 머리: 바로 뒤 칸에서 머리 쪽으로 향하는 방향이 진행 방향
            return self.head, DIR_ANGLE[_delta(cur, snake[1])]

        if i == len(snake) - 1:
            # 꼬리: 몸통이 붙어 있는 방향으로 회전
            return self.tail, DIR_ANGLE[_delta(snake[i - 1], cur)]

        to_head = _delta(snake[i - 1], cur)   # 머리 쪽 이웃 방향
        to_tail = _delta(snake[i + 1], cur)   # 꼬리 쪽 이웃 방향

        if to_head[0] == -to_tail[0] and to_head[1] == -to_tail[1]:
            # 앞뒤 이웃이 정반대에 있으면 직선 몸통
            # 원본이 가로 방향이므로 세로일 때만 90도 회전
            return self.body, 0 if to_head[1] == 0 else 90

        # 정반대가 아니면 꺾이는 지점
        return self.corner, CORNER_ANGLE[frozenset({to_head, to_tail})]

    def draw(self, snake, food, score):
        # 미리 만들어 둔 배경 한 장으로 화면을 덮음 (이전 프레임도 같이 지워짐)
        self.screen.blit(self.board, (0, 0))

        self.screen.blit(self.food, (food[0] * CELL_SIZE, food[1] * CELL_SIZE))

        # 셀 좌표 → 픽셀 좌표로 변환해서 그림
        # 예: (3, 5) → 픽셀 (3*32, 5*32) = (96, 160)
        for i, (x, y) in enumerate(snake):
            image, angle = self._segment(snake, i)
            if angle:
                # 90도 단위 회전은 픽셀이 뭉개지지 않고 정확히 돌아감
                image = pygame.transform.rotate(image, angle)
            self.screen.blit(image, (x * CELL_SIZE, y * CELL_SIZE))

        # 점수를 좌측 상단에 표시
        score_text = self.font.render(f"Score: {score}", True, WHITE)
        self.screen.blit(score_text, (8, 6))

    def _center_text(self, text, y, font=None, color=WHITE):
        # 텍스트를 가로 중앙 정렬해서 y 위치에 그리는 내부 헬퍼
        # get_rect(center=...)로 텍스트 길이에 상관없이 자동 정렬됨
        font = font or self.font
        surface = font.render(text, True, color)
        self.screen.blit(surface, surface.get_rect(center=(WIDTH // 2, y)))

    def draw_name_input(self, score, nickname):
        # 게임 오버 후 닉네임을 입력받는 화면
        # nickname은 main.py가 키 입력을 모아서 넘겨주는 문자열
        self.screen.fill(BG)
        self._center_text("Game Over!", HEIGHT // 2 - 112)
        self._center_text(f"Score: {score}", HEIGHT // 2 - 64)
        self._center_text("Enter your nickname:", HEIGHT // 2 - 8, self.small)
        # 커서 대신 밑줄(_)을 붙여 지금 입력 중이라는 걸 표시
        self._center_text(nickname + "_", HEIGHT // 2 + 40, self.font, GREEN)
        self._center_text("ENTER = save   ESC = skip", HEIGHT // 2 + 104, self.small)

    def draw_ranking(self, rows, score):
        # DB에서 받아온 상위 10명을 표로 표시
        # rows 예시: [{"nickname": "abc", "score": 12}, ...]
        self.screen.fill(BG)
        self._center_text("TOP 10", 40)
        self._center_text(f"Your score: {score}", 84, self.small, GREEN)

        if not rows:
            # DB 설정이 안 됐거나 네트워크 오류일 때
            self._center_text("(no data)", HEIGHT // 2, self.small)
        else:
            # enumerate(rows, 1)로 1등부터 순위 번호를 매김
            for i, row in enumerate(rows, 1):
                line = f"{i:2d}. {row['nickname']:<12} {row['score']}"
                text = self.small.render(line, True, WHITE)
                self.screen.blit(text, (96, 128 + (i - 1) * 42))

        self._center_text("SPACE to restart", HEIGHT - 40, self.small)
