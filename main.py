# 게임의 진입점(entry point)
# 게임 루프 실행, 키보드 입력 처리, 상태 전환을 담당
# 실제 게임 로직은 snake_game.py, 화면 그리기는 renderer.py,
# DB 저장/조회는 leaderboard.py에 위임

import pygame
import sys
from settings import WIDTH, HEIGHT, FPS_INIT
from snake_game import reset, update
from renderer import Renderer
from leaderboard import save_score, get_top10

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")
clock    = pygame.time.Clock()
renderer = Renderer(screen)

MAX_NAME_LEN = 12  # 랭킹 표에 깔끔하게 들어가는 최대 글자 수

snake, direction, food, score = reset()
state    = "PLAY"  # 게임 상태: "PLAY"(게임 중) → "NAME"(닉네임 입력) → "RANK"(랭킹 보기)
nickname = ""      # NAME 상태에서 키 입력을 하나씩 모아두는 문자열
ranking  = []      # RANK 상태에서 보여줄 상위 10명 데이터

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

            elif state == "NAME":
                if event.key == pygame.K_RETURN:
                    # 아무것도 안 쳤으면 기본 이름을 사용
                    name = nickname.strip() or "Player"
                    save_score(name, score)          # DB에 INSERT
                    ranking = get_top10()            # 저장 후 최신 랭킹 SELECT
                    state = "RANK"
                elif event.key == pygame.K_ESCAPE:
                    # 저장은 건너뛰고 랭킹만 보기
                    ranking = get_top10()
                    state = "RANK"
                elif event.key == pygame.K_BACKSPACE:
                    nickname = nickname[:-1]         # 마지막 글자 삭제
                elif len(nickname) < MAX_NAME_LEN and event.unicode.isprintable():
                    # event.unicode는 실제로 입력된 문자(Shift 조합까지 반영됨)
                    nickname += event.unicode

            elif state == "RANK":
                # 스페이스바를 누르면 게임 재시작
                if event.key == pygame.K_SPACE:
                    snake, direction, food, score = reset()
                    nickname = ""
                    state = "PLAY"

    if state == "PLAY":
        snake, food, score, alive = update(snake, direction, food, score)
        if not alive:
            state = "NAME"

    # 상태에 따라 그릴 화면을 고름
    if state == "PLAY":
        renderer.draw(snake, food, score)
    elif state == "NAME":
        renderer.draw_name_input(score, nickname)
    else:
        renderer.draw_ranking(ranking, score)

    pygame.display.flip()  # 버퍼에 그린 내용을 실제 화면에 출력

    if state == "PLAY":
        # 점수에 따라 속도 증가: 5점마다 1 FPS씩 빨라짐
        # 예) 점수 0 → 10 FPS, 점수 10 → 12 FPS, 점수 50 → 20 FPS
        speed = FPS_INIT + score // 5
    else:
        # 입력/랭킹 화면은 뱀이 움직이지 않으므로 고정 속도면 충분
        speed = 30
    clock.tick(speed)  # 지정한 FPS를 초과하지 않도록 루프 속도 제한
