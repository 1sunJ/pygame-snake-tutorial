# 화면 렌더링만 전담하는 파일
# 게임 로직(snake_game.py)과 완전히 분리되어 있어
# 그리기 방식을 바꿔도 게임 로직에 영향을 주지 않음

import pygame
from settings import CELL_SIZE, WIDTH, HEIGHT, BLACK, GREEN, RED, WHITE

class Renderer:
    def __init__(self, screen):
        self.screen = screen
        # SysFont는 콤마로 구분한 이름 중 PC에 설치된 첫 폰트를 사용
        # 맑은 고딕 등이 있으면 한글 닉네임도 깨지지 않고 표시됨
        KOREAN_FONTS = "malgungothic,applegothic,notosanscjkkr,arial"
        self.font   = pygame.font.SysFont(KOREAN_FONTS, 24)
        self.small  = pygame.font.SysFont(KOREAN_FONTS, 18)

    def draw(self, snake, food, score):
        # 매 프레임 전체를 검은색으로 지우고 다시 그림 (플리커 방지)
        self.screen.fill(BLACK)

        # 뱀의 각 칸을 셀 좌표 → 픽셀 좌표로 변환해서 그림
        # 예: (3, 5) → 픽셀 (3*20, 5*20) = (60, 100)
        for x, y in snake:
            pygame.draw.rect(self.screen, GREEN,
                             (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # 음식 그리기
        pygame.draw.rect(self.screen, RED,
                         (food[0] * CELL_SIZE, food[1] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # 점수를 좌측 상단에 표시
        score_text = self.font.render(f"Score: {score}", True, WHITE)
        self.screen.blit(score_text, (5, 5))

    def _center_text(self, text, y, font=None, color=WHITE):
        # 텍스트를 가로 중앙 정렬해서 y 위치에 그리는 내부 헬퍼
        # get_rect(center=...)로 텍스트 길이에 상관없이 자동 정렬됨
        font = font or self.font
        surface = font.render(text, True, color)
        self.screen.blit(surface, surface.get_rect(center=(WIDTH // 2, y)))

    def draw_name_input(self, score, nickname):
        # 게임 오버 후 닉네임을 입력받는 화면
        # nickname은 main.py가 키 입력을 모아서 넘겨주는 문자열
        self.screen.fill(BLACK)
        self._center_text("Game Over!", HEIGHT // 2 - 70)
        self._center_text(f"Score: {score}", HEIGHT // 2 - 40)
        self._center_text("Enter your nickname:", HEIGHT // 2 - 5, self.small)
        # 커서 대신 밑줄(_)을 붙여 지금 입력 중이라는 걸 표시
        self._center_text(nickname + "_", HEIGHT // 2 + 25, self.font, GREEN)
        self._center_text("ENTER = save   ESC = skip", HEIGHT // 2 + 65, self.small)

    def draw_ranking(self, rows, score):
        # DB에서 받아온 상위 10명을 표로 표시
        # rows 예시: [{"nickname": "abc", "score": 12}, ...]
        self.screen.fill(BLACK)
        self._center_text("TOP 10", 25)
        self._center_text(f"Your score: {score}", 52, self.small, GREEN)

        if not rows:
            # DB 설정이 안 됐거나 네트워크 오류일 때
            self._center_text("(no data)", HEIGHT // 2, self.small)
        else:
            # enumerate(rows, 1)로 1등부터 순위 번호를 매김
            for i, row in enumerate(rows, 1):
                line = f"{i:2d}. {row['nickname']:<12} {row['score']}"
                text = self.small.render(line, True, WHITE)
                self.screen.blit(text, (60, 80 + (i - 1) * 26))

        self._center_text("SPACE to restart", HEIGHT - 25, self.small)
