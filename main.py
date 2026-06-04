# 게임의 진입점(entry point)
# 게임 루프 실행, 키보드 입력 처리, 상태 전환을 담당
# 실제 게임 로직은 snake_game.py, 화면 그리기는 renderer.py에 위임

import pygame
import sys
from settings import WIDTH, HEIGHT, FPS_INIT
from snake_game import reset, update
from renderer import Renderer

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")
clock    = pygame.time.Clock()
renderer = Renderer(screen)

snake, direction, food, score = reset()
state = "PLAY"  # 게임 상태: "PLAY" 또는 "DEAD"

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if state == "PLAY":
                # 반대 방향 입력은 무시 (예: 오른쪽 이동 중 왼쪽 입력 차단)
                # direction 튜플: (1,0)=오른쪽, (-1,0)=왼쪽, (0,-1)=위, (0,1)=아래
                # 주의: 한 프레임에 방향키를 두 번 빠르게 누르면 반대 방향 체크를
                #        우회해 자기 몸을 뚫을 수 있는 버그가 있음
                if event.key == pygame.K_UP    and direction != (0, 1):
                    direction = (0, -1)
                if event.key == pygame.K_DOWN  and direction != (0, -1):
                    direction = (0, 1)
                if event.key == pygame.K_LEFT  and direction != (1, 0):
                    direction = (-1, 0)
                if event.key == pygame.K_RIGHT and direction != (-1, 0):
                    direction = (1, 0)

            # DEAD 상태에서 스페이스바를 누르면 게임 재시작
            if state == "DEAD" and event.key == pygame.K_SPACE:
                snake, direction, food, score = reset()
                state = "PLAY"

    if state == "PLAY":
        snake, food, score, alive = update(snake, direction, food, score)
        if not alive:
            state = "DEAD"

    renderer.draw(snake, food, score)
    if state == "DEAD":
        renderer.draw_game_over(score)

    pygame.display.flip()  # 버퍼에 그린 내용을 실제 화면에 출력

    # 점수에 따라 속도 증가: 5점마다 1 FPS씩 빨라짐
    # 예) 점수 0 → 10 FPS, 점수 10 → 12 FPS, 점수 50 → 20 FPS
    speed = FPS_INIT + score // 5
    clock.tick(speed)  # 지정한 FPS를 초과하지 않도록 루프 속도 제한
