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

BG_A     = (22, 33, 62)     # 어두운 칸
BG_B     = (27, 40, 71)     # 밝은 칸
BG_LINE  = (36, 53,  92)    # 셀 경계선 (아주 옅게)


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
    # 오른쪽을 바라보는 머리. 왼쪽 변만 꽉 채우고 앞쪽은 타원으로 둥글게
    surf = new_surface(CELL)
    mask = [[False] * CELL for _ in range(CELL)]

    ecx, ecy = 20.0, 16.0    # 주둥이 타원 중심
    ea, eb   = 9.0, 14.0     # 가로/세로 반지름

    for y in range(CELL):
        for x in range(CELL):
            px, py = x + 0.5, y + 0.5
            flat = (x <= 20) and (MARGIN <= y < MARGIN + TUBE)
            snout = ((px - ecx) / ea) ** 2 + ((py - ecy) / eb) ** 2 <= 1.0
            if flat or snout:
                mask[y][x] = True
                surf.set_at((x, y), tube_tone(abs(py - ecy)))

    draw_outline(surf, mask, CELL)

    # 위에서 내려다보는 시점이라 눈이 위아래로 두 개
    # 눈동자는 앞쪽(오른쪽) + 중심선 쪽으로 붙여서 위아래가 서로 대칭이 되게 함
    for eye_y, pupil_dy in ((7, 1), (22, 0)):
        for yy in range(eye_y, eye_y + 3):
            for xx in range(17, 20):
                surf.set_at((xx, yy), EYE_WHITE)
        for yy in range(eye_y + pupil_dy, eye_y + pupil_dy + 2):
            for xx in range(18, 20):
                surf.set_at((xx, yy), EYE_PUPIL)

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


def make_bg_tile():
    # 2칸x2칸(64x64) 체크무늬 + 미세 노이즈 + 셀 경계선
    # 픽셀마다 독립적인 노이즈라 이어붙여도 이음새가 생기지 않음
    size = CELL * 2
    surf = pygame.Surface((size, size))
    rng = random.Random(20260813)

    for y in range(size):
        for x in range(size):
            same = (x // CELL) == (y // CELL)
            r, g, b = BG_A if same else BG_B

            # 밝기만 살짝 흔들어 질감을 만듦 (2~3단계 이내)
            n = rng.random()
            if n < 0.12:
                r, g, b = r + 5, g + 6, b + 7
            elif n < 0.24:
                r, g, b = r - 3, g - 4, b - 5

            # 셀 경계에만 옅은 선 (반복해 붙이면 격자가 됨)
            if x % CELL == 0 or y % CELL == 0:
                r, g, b = BG_LINE

            surf.set_at((x, y), (max(0, r), max(0, g), max(0, b)))

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
