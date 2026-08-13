# 게임 전체에서 공유하는 상수 설정 파일
# 이 값들을 바꾸면 게임 크기, 속도, 색상이 한 번에 바뀜

CELL_SIZE = 32          # 각 셀(칸) 하나의 픽셀 크기 (스프라이트 한 장의 크기와 같음)
COLS = 20               # 가로 칸 수
ROWS = 20               # 세로 칸 수
WIDTH    = COLS * CELL_SIZE   # 화면 가로 픽셀 (20 * 32 = 640)
BOARD_H  = ROWS * CELL_SIZE   # 게임 판 높이 (20 * 32 = 640)
FOOTER_H = 34                 # 판 아래 제작자 표기 영역
HEIGHT   = BOARD_H + FOOTER_H # 창 전체 높이

FPS_INIT = 10           # 시작 속도: 초당 10프레임 = 뱀이 1초에 10칸 이동

# 화면이 400 → 640으로 커졌으므로 글자와 표 간격도 같은 비율(1.6배)로 키움
FONT_BIG   = 38
FONT_SMALL = 28
FONT_TINY  = 16   # 하단 제작자 표기용

# 제작자 표기
CREDIT    = "created by 1sunj"
COPYRIGHT = "© 2026 1sunj. All rights reserved."

BG    = (26,  21,  17)  # 게임 오버/랭킹 화면 바탕
GREEN = (79, 194,  89)  # 뱀 스프라이트와 같은 초록 (강조 글자용)
WHITE = (255, 255, 255)

# 게임 판 배경. 이미지가 아니라 renderer가 시작할 때 계산해서 그린다
BOARD      = (38, 32, 26)   # 판 바탕
BOARD_DOT  = (72, 62, 50)   # 칸 모서리에 찍는 점
FRAME      = (24, 20, 16)   # 바깥 테두리
FRAME_LINE = (60, 51, 41)   # 테두리 안쪽 가는 선
VIGNETTE   = 0.42           # 가장자리를 얼마나 어둡게 할지 (0.0 ~ 1.0)

FOOTER_BG   = (18, 15, 12)  # 하단 표기 영역 바탕
FOOTER_TEXT = (110, 98, 84) # 하단 표기 글자 (조용하게)
