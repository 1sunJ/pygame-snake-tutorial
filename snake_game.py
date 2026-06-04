# 스네이크 게임의 핵심 로직을 담당하는 파일
# 모든 함수가 상태를 직접 변경하지 않고 새 값을 반환하는 순수 함수로 구성됨
# → 게임 상태가 예측 가능하고 테스트하기 쉬움

import random
from settings import COLS, ROWS

def spawn_food(snake):
    # 뱀이 없는 빈 칸에 음식을 무작위로 배치
    # 주의: 뱀이 맵을 가득 채우면 빈 칸이 없어 무한 루프에 빠질 수 있음
    while True:
        pos = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
        if pos not in snake:
            return pos

def reset():
    # 게임을 초기 상태로 되돌림
    # 뱀: 3칸 길이로 가로 중앙 근처에서 시작, 오른쪽 방향
    snake     = [(10, 10), (9, 10), (8, 10)]
    direction = (1, 0)
    food      = spawn_food(snake)
    score     = 0
    return snake, direction, food, score

def update(snake, direction, food, score):
    # 매 프레임마다 호출되어 뱀의 상태를 한 칸 전진시킴
    # 반환값: (새 뱀, 새 음식 위치, 새 점수, 생존 여부)

    head_x, head_y = snake[0]
    new_head = (head_x + direction[0], head_y + direction[1])

    # 벽 충돌 검사: 새 머리가 맵 범위를 벗어나면 사망
    if not (0 <= new_head[0] < COLS and 0 <= new_head[1] < ROWS):
        return snake, food, score, False

    # 자기 몸 충돌 검사: 새 머리가 몸통과 겹치면 사망
    # 참고: in 연산은 리스트를 순차 탐색(O(n))하므로 뱀이 길어질수록 느려짐
    if new_head in snake:
        return snake, food, score, False

    # 머리를 앞에 추가해서 뱀을 한 칸 전진
    snake = [new_head] + snake

    if new_head == food:
        # 음식을 먹었으면 꼬리를 제거하지 않아 뱀 길이가 1 증가
        score += 1
        food = spawn_food(snake)
    else:
        # 음식을 못 먹었으면 꼬리를 제거해 길이 유지 (슬라이딩 효과)
        snake = snake[:-1]

    return snake, food, score, True
