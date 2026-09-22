"""게임 전역 설정값 모음."""

# 화면
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
FPS = 60
TITLE = "Roguelike Maze"

# 미로 (홀수 권장: 벽/통로가 정확히 맞물림)
# 창(960x640)에는 TILE_SIZE=40 기준 24x16칸이 보인다(960, 640 모두 40으로
# 나누어떨어져 화면 가장자리에 남는 여백이 없다). 미로 자체는 이보다 커서,
# 플레이어를 따라다니는 카메라로 스크롤해서 본다(Game._update_camera 참고).
MAZE_COLS = 27
MAZE_ROWS = 19
TILE_SIZE = 40

# 층수에 따른 미로 크기 증가
MAZE_GROWTH_PER_FLOORS = 2  # 이 층수마다
MAZE_GROWTH_AMOUNT = 2      # 가로/세로 각각 이만큼 증가
MAX_MAZE_COLS = 83
MAX_MAZE_ROWS = 63

# 층 전환
FLOOR_MESSAGE_MS = 1000  # "N층 도착!" 안내 문구 표시 시간

# 색상
COLOR_BG = (15, 15, 20)
COLOR_WALL = (60, 60, 70)
COLOR_FLOOR = (25, 25, 32)
COLOR_PLAYER = (90, 200, 255)
COLOR_EXIT = (255, 200, 60)
COLOR_TEXT = (230, 230, 230)
COLOR_MONSTER = (220, 60, 60)
COLOR_MONSTER_STUNNED = (100, 30, 30)
COLOR_SHIELD = (240, 240, 255)

# 플레이어
PLAYER_SIZE = TILE_SIZE - 8
PLAYER_SPEED = 4  # 초당 이동 타일 기반 처리 (move_cooldown과 함께 사용)
MOVE_COOLDOWN_MS = 120
PLAYER_ANIM_FRAME_MS = 150  # 걷기 애니메이션 프레임 순환 간격

# 최고 기록
HIGHSCORE_NAME_MAX_LEN = 10

# 몬스터
MONSTER_MOVE_COOLDOWN_MS = 180
MONSTER_CHASE_RADIUS = 5          # 이 거리(칸) 이내로 들어오면 추적 시작("발견")
MONSTER_MIN_DIST_FROM_ENTRANCE = 4  # 입구에서 최소 이만큼 떨어져 스폰
MONSTER_MIN_DIST_BETWEEN = 2        # 몬스터끼리 최소 이만큼 거리 유지
MONSTER_WANDER_MOVE_CHANCE = 0.5    # 배회 중 매 이동 타이밍마다 실제로 움직일 확률

# 층별 몬스터 수 계산식에 쓰이는 값
MONSTER_BASE_COUNT = 2          # 1~3층 기본 마리 수
MONSTER_BLOCK_FLOORS = 3        # 이 층수마다 증가
MONSTER_HIGH_FLOOR_THRESHOLD = 20
MONSTER_HIGH_FLOOR_STEP = 2     # 21층 이후 블록당 증가량
MONSTER_COUNT_MULTIPLIER = 2    # 위 계산식 결과에 곱해서 전체 마리 수를 배로 늘림

# 밀치기(넉백) & 방패 이펙트
KNOCKBACK_DISTANCE = 5
MONSTER_STUN_MS = 220
SHIELD_EFFECT_MS = 150

# 몬스터 애니메이션 (프레임 순환 재생 간격)
MONSTER_ANIM_FRAME_MS = 150
