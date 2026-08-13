# 스프라이트/타일 PNG를 생성하는 도구
# 게임 코드가 아니라 리소스를 뽑아내는 스크립트라 게임 실행에는 필요 없음
# 색이나 모양을 바꾸고 싶을 때만 다시 실행: python3 tools/make_sprites.py
#
# 좌표를 계산해서 픽셀을 하나씩 찍는 방식이라 안티에일리어싱이 전혀 없음
# → 픽셀아트의 각진 경계가 그대로 유지됨

import os
import math
import random

# 화면을 띄우지 않고 이미지만 저장하므로 더미 비디오 드라이버 사용
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

CELL = 32          # 스프라이트 한 장의 크기
TUBE = 28          # 뱀 몸통 굵기 (위아래 2px씩 여백)
MARGIN = (CELL - TUBE) // 2   # = 2

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPRITE_DIR = os.path.join(ROOT, "assets", "sprites")
TILE_DIR   = os.path.join(ROOT, "assets", "tiles")

# ── 팔레트: 비비드 모던 ────────────────────────────────────────────
SNAKE_OUTLINE = (27,  94,  58)
SNAKE_DARK    = (36, 158,  99)
SNAKE_BODY    = (61, 214, 140)
SNAKE_LIT     = (127, 245, 184)

EYE_WHITE = (245, 250, 248)
EYE_PUPIL = (18,  40,  30)
TONGUE    = (255,  71,  87)

APPLE_OUTLINE = (138,  26,  40)
APPLE_DARK    = (206,  44,  60)
APPLE_BODY    = (255,  71,  87)
APPLE_LIT     = (255, 138, 148)
APPLE_SHINE   = (255, 214, 218)

STEM      = (122,  78,  48)
STEM_DARK = (82,   50,  30)
LEAF          = (124, 214,  92)
LEAF_LIT      = (168, 240, 130)
LEAF_OUTLINE  = (58,  120,  44)

BG_GAP   = (15, 22,  42)    # 칸 사이 이음새 (가장 어두움)
BG_A     = (28, 39,  70)    # 어두운 칸
BG_B     = (34, 47,  84)    # 밝은 칸
BG_EDGE  = (41, 56,  98)    # 칸 위쪽 모서리 (살짝 도드라지게)


def new_surface(w, h=None):
    # 알파 채널을 가진 완전 투명 서피스
    surf = pygame.Surface((w, h or w), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    return surf


def tube_tone(off):
    # off: 몸통 중심선에서 잰 거리 (0 = 한가운데, 14 = 가장자리)
    #
    # 가운데가 밝고 양쪽 가장자리가 어두운 좌우 대칭 배치.
    # 한쪽만 밝게 하면 스프라이트를 90도 돌렸을 때 밝은 면이 같이 돌아가서
    # 가로 몸통과 세로 몸통, 코너의 밝은 쪽이 서로 어긋난다.
    # 대칭으로 두면 어느 각도로 돌려도 같은 모양이라 이음새가 안 보인다.
    if off < 4.0:
        return SNAKE_LIT
    if off < 9.0:
        return SNAKE_BODY
    return SNAKE_DARK


def draw_outline(surf, mask, size, color=SNAKE_OUTLINE):
    # 마스크의 가장자리에 외곽선을 그림
    # 단, 이미지 밖으로 나가는 방향은 건너뜀 → 그 변은 여백 없이 꽉 차서
    #     옆 타일과 이음새 없이 붙음 (full bleed)
    for y in range(size):
        for x in range(size):
            if not mask[y][x]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < size and 0 <= ny < size and not mask[ny][nx]:
                    surf.set_at((x, y), color)
                    break


def make_body():
    # 가로 몸통: 좌우 변을 끝까지 채우고 위아래에만 2px 여백
    surf = new_surface(CELL)
    mask = [[False] * CELL for _ in range(CELL)]

    for y in range(MARGIN, MARGIN + TUBE):
        off = abs(y + 0.5 - CELL / 2.0)
        for x in range(CELL):
            mask[y][x] = True
            surf.set_at((x, y), tube_tone(off))

    draw_outline(surf, mask, CELL)
    return surf


def make_corner():
    # 왼쪽에서 들어와 아래로 빠지는 곡선
    # 중심을 셀의 좌하단 모서리(0, 32)에 두고 반지름 범위로 관을 만들면
    # 왼쪽 변과 아래 변에서 정확히 y=2~29 / x=2~29 로 떨어져 몸통과 맞물림
    surf = new_surface(CELL)
    mask = [[False] * CELL for _ in range(CELL)]

    cx, cy = 0.0, float(CELL)
    r_in  = MARGIN + 0.5              # 2.5
    r_out = CELL - MARGIN - 0.5       # 29.5

    for y in range(CELL):
        for x in range(CELL):
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            if r_in <= d <= r_out:
                mask[y][x] = True
                # 관의 중심선은 안쪽/바깥쪽 반지름의 중간값
                surf.set_at((x, y), tube_tone(abs(d - (r_in + r_out) / 2.0)))

    draw_outline(surf, mask, CELL)
    return surf


def make_head():
    # 오른쪽을 바라보는 머리. 왼쪽 변만 꽉 채우고 앞쪽은 둥글게
    #
    # 목(왼쪽 끝)은 몸통과 같은 28px이지만 눈 부근에서 30px까지 부풀린다.
    # 머리가 몸통과 굵기가 같으면 어디가 앞인지 한눈에 안 들어옴
    surf = new_surface(CELL)
    mask = [[False] * CELL for _ in range(CELL)]

    center   = CELL / 2.0
    half     = TUBE / 2.0     # 14.0, 몸통과 똑같은 굵기
    snout_x  = 20.0           # 여기서부터 앞쪽으로 좁아짐
    snout_a  = 9.0

    # 머리를 몸통보다 굵게 만들어 봤지만 32px에서는 1px밖에 못 넓힌다.
    # 그 1px이 부드러운 곡선이 아니라 단차로 보여서 오히려 결함처럼 읽혔다.
    # 굵기는 몸통에 맞추고 눈과 주둥이 모양으로만 머리를 구분한다.
    for y in range(CELL):
        for x in range(CELL):
            px, py = x + 0.5, y + 0.5
            dy = abs(py - center)

            if px <= snout_x:
                inside = dy <= half
            else:
                # 주둥이는 지수 2.5의 초타원 → 타원보다 뭉툭하게 떨어짐
                u = (px - snout_x) / snout_a
                inside = u <= 1.0 and (u ** 2.5 + (dy / half) ** 2.5) <= 1.0

            if inside:
                mask[y][x] = True
                surf.set_at((x, y), tube_tone(dy))

    draw_outline(surf, mask, CELL)

    # 위에서 내려다보는 시점이라 눈이 위아래로 두 개.
    # 흰자에 검은 눈동자를 넣으면 32px에서는 흰 사각형 두 개로만 보인다.
    # 어두운 눈에 반사광 점을 찍는 쪽이 훨씬 눈처럼 읽힘.
    # 위/아래 눈은 중심선(y=16) 기준으로 정확히 대칭인 자리에 놓는다
    for top, glint_y in ((7, 8), (21, 23)):
        for dy_ in range(4):
            for dx_ in range(4):
                # 네 모서리를 비워 둥글게
                if dx_ in (0, 3) and dy_ in (0, 3):
                    continue
                surf.set_at((19 + dx_, top + dy_), EYE_PUPIL)
        # 반사광은 1픽셀이면 충분하다. 2픽셀만 돼도 과녁처럼 보임
        surf.set_at((20, glint_y), EYE_WHITE)

    # 갈라진 혀
    for px, py in ((29, 15), (29, 16), (30, 15), (30, 16), (31, 14), (31, 17)):
        surf.set_at((px, py), TONGUE)

    return surf


def make_tail():
    # 오른쪽이 몸통과 이어지고 왼쪽으로 갈수록 가늘어짐
    # 굵기를 직선으로 줄이면 화살촉처럼 보이므로 지수 곡선으로 완만하게 줄임
    # (x=31에서 정확히 14 → 몸통 28px와 딱 맞물림, 왼쪽 2px는 여백)
    surf = new_surface(CELL)
    mask = [[False] * CELL for _ in range(CELL)]

    half_max = TUBE / 2.0     # 14.0
    center   = CELL / 2.0
    tip_x    = float(MARGIN)  # 꼬리 끝이 시작하는 x

    for x in range(CELL):
        t = (x - tip_x + 0.5) / (CELL - 1 - tip_x + 0.5)
        if t <= 0:
            continue
        half = half_max * (t ** 0.55)
        for y in range(CELL):
            off = abs(y + 0.5 - center)
            if off <= half:
                mask[y][x] = True
                # 굵기에 비례해 명암을 줄여야 밝은 띠도 같이 가늘어짐
                # (x=31에서는 half=14라 몸통과 정확히 같은 배치가 됨)
                surf.set_at((x, y), tube_tone(off / half * half_max))

    draw_outline(surf, mask, CELL)
    return surf


def make_apple():
    # 사방에 여백을 두는 유일한 스프라이트
    surf = new_surface(CELL)
    mask = [[False] * CELL for _ in range(CELL)]

    bcx, bcy = 16.0, 18.0
    ba, bb   = 11.0, 10.5
    lx, ly   = 11.0, 13.0    # 광원 위치 (좌상단)

    for y in range(CELL):
        for x in range(CELL):
            px, py = x + 0.5, y + 0.5
            if ((px - bcx) / ba) ** 2 + ((py - bcy) / bb) ** 2 > 1.0:
                continue
            # 꼭지가 앉을 자리를 살짝 파냄
            if math.hypot(px - 16.0, py - 7.5) <= 3.2:
                continue
            mask[y][x] = True
            d = math.hypot(px - lx, py - ly)
            if d < 3.0:
                c = APPLE_SHINE
            elif d < 8.0:
                c = APPLE_LIT
            elif d < 15.0:
                c = APPLE_BODY
            else:
                c = APPLE_DARK
            surf.set_at((x, y), c)

    draw_outline(surf, mask, CELL, APPLE_OUTLINE)

    # 꼭지
    for px, py in ((15, 9), (15, 8), (16, 7), (16, 6), (17, 5), (17, 4)):
        surf.set_at((px, py), STEM)
        surf.set_at((px + 1, py), STEM_DARK)

    # 잎: 타원을 기울여서 배치
    theta = math.radians(-35)
    cos_t, sin_t = math.cos(theta), math.sin(theta)
    leaf_mask = [[False] * CELL for _ in range(CELL)]
    for y in range(CELL):
        for x in range(CELL):
            u = (x + 0.5) - 21.5
            v = (y + 0.5) - 6.0
            ur = u * cos_t + v * sin_t
            vr = -u * sin_t + v * cos_t
            if (ur / 5.0) ** 2 + (vr / 2.4) ** 2 <= 1.0:
                leaf_mask[y][x] = True
                surf.set_at((x, y), LEAF_LIT if vr < 0 else LEAF)
    draw_outline(surf, leaf_mask, CELL, LEAF_OUTLINE)

    return surf


def in_round_rect(px, py, x0, y0, x1, y1, r):
    # 모서리가 둥근 사각형 안에 있는지 검사
    # 사각형을 안쪽으로 r만큼 줄인 영역에서 가장 가까운 점을 찾고
    # 그 점까지의 거리가 r 이하이면 안쪽
    cx = min(max(px, x0 + r), x1 - r)
    cy = min(max(py, y0 + r), y1 - r)
    return (px - cx) ** 2 + (py - cy) ** 2 <= r * r


def make_bg_tile():
    # 2칸x2칸(64x64) 배경 타일
    #
    # 처음엔 평평한 체크무늬에 노이즈를 뿌렸는데, 노이즈가 질감이 아니라
    # 얼룩처럼 보이고 경계선이 칸의 두 변에만 있어 모눈종이처럼 어긋나 보였다.
    # 칸마다 모서리가 둥근 판을 깔고 사이를 어둡게 비우는 방식으로 바꿈.
    # 격자가 "의도된 무늬"로 읽히고 이음새도 사방이 균일해진다.
    size = CELL * 2
    surf = pygame.Surface((size, size))
    surf.fill(BG_GAP)
    rng = random.Random(20260813)

    for y in range(size):
        for x in range(size):
            # 각 칸의 내부 좌표 (0~31)
            lx, ly = x % CELL + 0.5, y % CELL + 0.5
            if not in_round_rect(lx, ly, 1.0, 1.0, CELL - 1.0, CELL - 1.0, 5.0):
                continue

            same = (x // CELL) == (y // CELL)
            r, g, b = BG_A if same else BG_B

            # 위쪽 모서리를 한 단계 밝게 해서 살짝 튀어나와 보이게 함
            if not in_round_rect(lx, ly + 1.5, 1.0, 1.0, CELL - 1.0, CELL - 1.0, 5.0):
                r, g, b = BG_EDGE

            # 아주 옅은 질감. 판 안에서만 흔들어야 얼룩으로 안 보임
            elif rng.random() < 0.10:
                r, g, b = r + 3, g + 4, b + 5

            surf.set_at((x, y), (r, g, b))

    return surf


def main():
    pygame.init()
    os.makedirs(SPRITE_DIR, exist_ok=True)
    os.makedirs(TILE_DIR, exist_ok=True)

    sprites = {
        "snake_head.png":   make_head(),
        "snake_body.png":   make_body(),
        "snake_corner.png": make_corner(),
        "snake_tail.png":   make_tail(),
        "food_apple.png":   make_apple(),
    }
    for name, surf in sprites.items():
        pygame.image.save(surf, os.path.join(SPRITE_DIR, name))
        print("saved", os.path.join("assets/sprites", name))

    pygame.image.save(make_bg_tile(), os.path.join(TILE_DIR, "bg_tile.png"))
    print("saved", os.path.join("assets/tiles", "bg_tile.png"))

    pygame.quit()


if __name__ == "__main__":
    main()
