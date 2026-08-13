# 스프라이트 PNG를 생성하는 도구
# 게임 코드가 아니라 리소스를 뽑아내는 스크립트라 게임 실행에는 필요 없음
# 색이나 모양을 바꾸고 싶을 때만 다시 실행: python3 tools/make_sprites.py
#
# 스프라이트는 16x16이다. 게임은 이걸 그대로 640 창에 그리지 않고
# 320x320 내부 화면에 그린 뒤 2배로 확대한다.
# 그래야 그림 1픽셀이 화면에서 2x2 덩어리가 되어 픽셀이 눈에 보인다.
# 1:1로 그리면 픽셀이 너무 작아 각진 맛이 사라지고 그냥 작은 그림이 된다.

import os
import math

# 화면을 띄우지 않고 이미지만 저장하므로 더미 비디오 드라이버 사용
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame

CELL   = 16                   # 스프라이트 한 장의 크기
TUBE   = 14                   # 뱀 몸통 굵기 (위아래 1px씩 여백)
MARGIN = (CELL - TUBE) // 2   # = 1
MID    = CELL / 2.0           # = 8.0, 몸통 중심선
HALF   = TUBE / 2.0           # = 7.0, 몸통 반지름

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPRITE_DIR = os.path.join(ROOT, "assets", "sprites")

# ── 팔레트: 따뜻한 숯빛 배경 + 잎사귀 초록 ─────────────────────────
SNAKE_OUTLINE = (29,  82,  38)
SNAKE_DARK    = (46, 140,  60)
SNAKE_BODY    = (79, 194,  89)
SNAKE_LIT     = (138, 222, 124)

EYE_PUPIL = (18,  40,  30)
TONGUE    = (255,  71,  87)

APPLE_OUTLINE = (138,  26,  40)
APPLE_DARK    = (206,  44,  60)
APPLE_BODY    = (255,  71,  87)
APPLE_LIT     = (255, 138, 148)
APPLE_SHINE   = (255, 214, 218)

STEM         = (122,  78,  48)
LEAF         = (165, 224,  99)
LEAF_OUTLINE = (94,  130,  48)


def new_surface(size=CELL):
    # 알파 채널을 가진 완전 투명 서피스
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    return surf


def tube_tone(off):
    # off: 몸통 중심선에서 잰 거리 (0 = 한가운데, 7 = 가장자리)
    #
    # 가운데가 밝고 양쪽 가장자리가 어두운 좌우 대칭 배치.
    # 한쪽만 밝게 하면 스프라이트를 90도 돌렸을 때 밝은 면이 같이 돌아가서
    # 가로 몸통과 세로 몸통, 코너의 밝은 쪽이 서로 어긋난다.
    # 대칭으로 두면 어느 각도로 돌려도 같은 모양이라 이음새가 안 보인다.
    if off < 2.0:
        return SNAKE_LIT
    if off < 4.5:
        return SNAKE_BODY
    return SNAKE_DARK


def draw_outline(surf, mask, color=SNAKE_OUTLINE):
    # 마스크의 가장자리에 외곽선을 그림
    # 단, 이미지 밖으로 나가는 방향은 건너뜀 → 그 변은 여백 없이 꽉 차서
    #     옆 칸과 이음새 없이 붙음 (full bleed)
    for y in range(CELL):
        for x in range(CELL):
            if not mask[y][x]:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < CELL and 0 <= ny < CELL and not mask[ny][nx]:
                    surf.set_at((x, y), color)
                    break


def make_body():
    # 가로 몸통: 좌우 변을 끝까지 채우고 위아래에만 1px 여백
    surf = new_surface()
    mask = [[False] * CELL for _ in range(CELL)]

    for y in range(MARGIN, MARGIN + TUBE):
        tone = tube_tone(abs(y + 0.5 - MID))
        for x in range(CELL):
            mask[y][x] = True
            surf.set_at((x, y), tone)

    draw_outline(surf, mask)
    return surf


def make_corner():
    # 왼쪽에서 들어와 아래로 빠지는 곡선
    # 중심을 셀의 좌하단 모서리(0, 16)에 두고 반지름 범위로 관을 만들면
    # 왼쪽 변과 아래 변에서 정확히 몸통과 같은 자리에 떨어진다
    surf = new_surface()
    mask = [[False] * CELL for _ in range(CELL)]

    r_in  = MARGIN + 0.5              # 1.5
    r_out = CELL - MARGIN - 0.5       # 14.5
    r_mid = (r_in + r_out) / 2.0      # 8.0

    for y in range(CELL):
        for x in range(CELL):
            d = math.hypot(x + 0.5, y + 0.5 - CELL)
            if r_in <= d <= r_out:
                mask[y][x] = True
                surf.set_at((x, y), tube_tone(abs(d - r_mid)))

    draw_outline(surf, mask)
    return surf


def make_head():
    # 오른쪽을 바라보는 머리. 왼쪽 변만 꽉 채우고 앞쪽은 둥글게
    # 굵기는 몸통과 같다. 16px에서는 넓힐 여유가 없고, 억지로 넓히면
    # 곡선이 아니라 목에 계단이 생겨 결함처럼 보인다
    surf = new_surface()
    mask = [[False] * CELL for _ in range(CELL)]

    snout_x, snout_a = 10.0, 4.5

    for y in range(CELL):
        for x in range(CELL):
            px, py = x + 0.5, y + 0.5
            dy = abs(py - MID)
            if px <= snout_x:
                inside = dy <= HALF
            else:
                # 주둥이는 지수 2.5의 초타원 → 타원보다 뭉툭하게 떨어짐
                u = (px - snout_x) / snout_a
                inside = u <= 1.0 and (u ** 2.5 + (dy / HALF) ** 2.5) <= 1.0
            if inside:
                mask[y][x] = True
                surf.set_at((x, y), tube_tone(dy))

    draw_outline(surf, mask)

    # 위에서 내려다보는 시점이라 눈이 위아래로 두 개.
    # 16px에서는 2x2가 한계고, 2배 확대하면 화면에서 4x4로 보인다.
    # 흰자를 넣을 자리가 없어 어두운 점만 찍는다
    for top in (3, 11):
        for yy in range(top, top + 2):
            for xx in range(9, 11):
                surf.set_at((xx, yy), EYE_PUPIL)

    # 혀. 주둥이가 x=14에서 끝나므로 그 앞 한 칸에 찍는다
    surf.set_at((15, 7), TONGUE)
    surf.set_at((15, 8), TONGUE)

    return surf


def make_tail():
    # 오른쪽이 몸통과 이어지고 왼쪽으로 갈수록 가늘어짐
    # 굵기를 직선으로 줄이면 화살촉처럼 보이므로 지수 곡선으로 완만하게
    surf = new_surface()
    mask = [[False] * CELL for _ in range(CELL)]

    tip_x = float(MARGIN)
    span  = (CELL - 1) - tip_x + 0.5

    for x in range(CELL):
        t = (x - tip_x + 0.5) / span
        if t <= 0:
            continue
        half = HALF * (t ** 0.55)
        for y in range(CELL):
            off = abs(y + 0.5 - MID)
            if off <= half:
                mask[y][x] = True
                # 굵기에 비례해 명암을 줄여야 밝은 띠도 같이 가늘어짐
                surf.set_at((x, y), tube_tone(off / half * HALF))

    draw_outline(surf, mask)
    return surf


def make_apple():
    # 사방에 여백을 두는 유일한 스프라이트
    surf = new_surface()
    mask = [[False] * CELL for _ in range(CELL)]

    bcx, bcy, ba, bb = 8.0, 9.5, 5.5, 5.3
    lx, ly = 5.5, 7.0          # 광원 (좌상단)

    for y in range(CELL):
        for x in range(CELL):
            px, py = x + 0.5, y + 0.5
            if ((px - bcx) / ba) ** 2 + ((py - bcy) / bb) ** 2 > 1.0:
                continue
            # 꼭지가 앉을 자리를 살짝 파냄
            if math.hypot(px - bcx, py - 4.3) <= 1.9:
                continue
            mask[y][x] = True
            d = math.hypot(px - lx, py - ly)
            if d < 1.6:
                c = APPLE_SHINE
            elif d < 3.6:
                c = APPLE_LIT
            elif d < 6.4:
                c = APPLE_BODY
            else:
                c = APPLE_DARK
            surf.set_at((x, y), c)

    draw_outline(surf, mask, APPLE_OUTLINE)

    # 꼭지
    for py in (1, 2, 3):
        surf.set_at((7, py), STEM)

    # 잎: 기울인 작은 타원
    theta = math.radians(-30)
    cos_t, sin_t = math.cos(theta), math.sin(theta)
    leaf_mask = [[False] * CELL for _ in range(CELL)]
    for y in range(CELL):
        for x in range(CELL):
            u = (x + 0.5) - 10.6
            v = (y + 0.5) - 2.4
            ur = u * cos_t + v * sin_t
            vr = -u * sin_t + v * cos_t
            if (ur / 2.7) ** 2 + (vr / 1.35) ** 2 <= 1.0:
                leaf_mask[y][x] = True
                surf.set_at((x, y), LEAF)
    draw_outline(surf, leaf_mask, LEAF_OUTLINE)

    return surf


def main():
    pygame.init()
    os.makedirs(SPRITE_DIR, exist_ok=True)

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

    pygame.quit()


if __name__ == "__main__":
    main()
