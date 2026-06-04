# 화면 렌더링만 전담하는 파일
# 게임 로직(snake_game.py)과 완전히 분리되어 있어
# 그리기 방식을 바꿔도 게임 로직에 영향을 주지 않음

import pygame
from settings import CELL_SIZE, WIDTH, HEIGHT, BLACK, GREEN, RED, WHITE

class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.font   = pygame.font.SysFont(None, 36)

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

    def draw_game_over(self, score):
        # Game Over 메시지를 화면 정중앙에 표시
        # get_rect(center=...)로 텍스트 크기에 상관없이 자동 중앙 정렬
        msg = self.font.render("Game Over!  SPACE to restart", True, WHITE)
        self.screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
