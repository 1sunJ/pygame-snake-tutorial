# pygame-snake-tutorial

pygame으로 Snake 게임을 만들며 배우는 게임 개발 입문 튜토리얼 (5단계)

---

## 대상

- Python 기초 문법을 아는 분 (변수, 반복문, 함수, 리스트)
- pygame 및 게임 개발 경험이 없는 분
- 알고리즘 기초 경험이 있는 분 (스택, 큐, 해시 등)

---

## 커리큘럼

| 스텝 | 제목 | 핵심 내용 | 산출물 |
| --- | --- | --- | --- |
| Step 1 | pygame 기본기 | 게임 루프, 이벤트, 도형 그리기 | 빈 창 + 사각형 |
| Step 2 | 그리드와 뱀 이동 | 그리드 좌표계, 리스트로 뱀 표현, 이동 | 움직이는 뱀 |
| Step 3 | 먹이와 충돌 | 먹이 생성, 벽/몸 충돌 감지 | 플레이 가능한 Snake |
| Step 4 | 게임 완성 | 점수, 속도 증가, 재시작 | Snake 완성본 |
| Step 5 | 파일 분리 리팩토링 | 역할별 파일 분리, 모듈 import | 모듈 구조 Snake |

---

## 디렉토리 구조

```
.
├── curriculum/
│   ├── step1_pygame_basics.md
│   ├── step2_grid_and_movement.md
│   ├── step3_food_and_collision.md
│   ├── step4_game_complete.md
│   └── step5_refactoring.md
└── snake_final/
    ├── main.py          # 진입점, 게임 루프
    ├── settings.py      # 상수 모음
    ├── snake_game.py    # 게임 로직
    └── renderer.py      # 화면 렌더링
```

---

## 실행 방법

**요구사항**
- Python 3.8 이상
- Windows / Mac / Linux

**설치 및 실행**

```bash
pip install pygame
cd snake_final
python main.py
```

**조작**

| 키 | 동작 |
| --- | --- |
| 방향키 | 뱀 방향 전환 |
| Space | 재시작 (게임 오버 후) |

---

## 수업 진행 방식

각 스텝은 아래 구조로 구성되어 있습니다.

1. **개념 설명** — 해당 스텝에서 다루는 핵심 개념
2. **실습 코드** — 직접 실행해볼 수 있는 예제
3. **과제** — 스스로 확장해보는 문제

Step 1 ~ Step 4 는 기능을 하나씩 추가하며 진행하고,
Step 5 에서 완성 코드를 역할별 파일로 리팩토링합니다.
