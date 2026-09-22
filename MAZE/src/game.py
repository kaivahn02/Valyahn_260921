"""게임 루프와 상태를 담당하는 메인 Game 클래스."""
import random
import sys

import pygame

from src.hero import load_hero_sprites, load_shield_sprites
from src.highscore import load_highscore, save_highscore
from src.maze_generator import MazeGenerator
from src.monster import Monster, load_monster_sprites, monster_count_for_floor
from src.player import Player
from src.tiles import load_tile_sets
from src.settings import (
    COLOR_BG,
    COLOR_EXIT,
    COLOR_FLOOR,
    COLOR_MONSTER,
    COLOR_MONSTER_STUNNED,
    COLOR_SHIELD,
    COLOR_TEXT,
    COLOR_WALL,
    FLOOR_MESSAGE_MS,
    FPS,
    HIGHSCORE_NAME_MAX_LEN,
    KNOCKBACK_DISTANCE,
    MAX_MAZE_COLS,
    MAX_MAZE_ROWS,
    MAZE_COLS,
    MAZE_GROWTH_AMOUNT,
    MAZE_GROWTH_PER_FLOORS,
    MAZE_ROWS,
    MONSTER_MIN_DIST_BETWEEN,
    MONSTER_MIN_DIST_FROM_ENTRANCE,
    MONSTER_STUN_MS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SHIELD_EFFECT_MS,
    TILE_SIZE,
    TITLE,
)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("malgungothic", 28)
        self.big_font = pygame.font.SysFont("malgungothic", 48)
        self.running = True

        self.floor = 1
        self.in_transition = False
        self.transition_end_time = 0
        self.next_floor = 1

        self.highscore = load_highscore()
        self.game_over = False
        self.is_new_record = False
        self.name_input = ""

        self.monsters = []
        self.monster_sprites = load_monster_sprites()
        self.hero_sprites = load_hero_sprites()
        self.shield_sprites = load_shield_sprites()
        self.shield_effect_started = 0
        self.shield_effect_until = 0
        self.shield_effect_dir = (0, 1)

        self.tile_sets = load_tile_sets()
        self.floor_tile_variants = []
        self.wall_tile_variants = []
        self.tile_variant_seed = []

        self._generate_floor()

    def _maze_size_for_floor(self, floor: int):
        growth_steps = (floor - 1) // MAZE_GROWTH_PER_FLOORS
        growth = growth_steps * MAZE_GROWTH_AMOUNT
        cols = min(MAZE_COLS + growth, MAX_MAZE_COLS)
        rows = min(MAZE_ROWS + growth, MAX_MAZE_ROWS)
        return cols, rows

    def _generate_floor(self):
        cols, rows = self._maze_size_for_floor(self.floor)
        self.grid = MazeGenerator(cols, rows).generate()
        self.player = Player(1, 1)
        self.exit_pos = self._find_exit_cell()
        self.in_transition = False
        self._spawn_monsters()
        self._pick_stage_tiles()

        self.camera_col = 0
        self.camera_row = 0
        self.offset_x = 0
        self.offset_y = 0
        self._update_camera()

    def _update_camera(self):
        """플레이어를 화면 중앙에 두려고 시도하되, 미로 가장자리 밖은 보여주지 않도록
        카메라 위치를 클램프한다. 미로가 화면보다 작은 축은 스크롤 없이 가운데 정렬."""
        cols, rows = len(self.grid[0]), len(self.grid)
        view_cols = SCREEN_WIDTH // TILE_SIZE
        view_rows = SCREEN_HEIGHT // TILE_SIZE

        max_camera_col = max(0, cols - view_cols)
        max_camera_row = max(0, rows - view_rows)

        self.camera_col = max(0, min(self.player.col - view_cols // 2, max_camera_col))
        self.camera_row = max(0, min(self.player.row - view_rows // 2, max_camera_row))

        margin_x = max(0, (SCREEN_WIDTH - cols * TILE_SIZE) // 2)
        margin_y = max(0, (SCREEN_HEIGHT - rows * TILE_SIZE) // 2)

        self.offset_x = margin_x - self.camera_col * TILE_SIZE
        self.offset_y = margin_y - self.camera_row * TILE_SIZE

    def _pick_stage_tiles(self):
        """이번 스테이지에서 쓸 바닥 종류 하나, 벽 종류 하나를 무작위로 고정한다.
        같은 종류 안의 변형 이미지는 칸마다 무작위로 섞어 쓰되, 매 프레임 다시 뽑으면
        타일이 깜빡이므로 칸별 변형 값을 tile_variant_seed에 한 번만 저장해둔다."""
        floor_types = list(self.tile_sets["floor"].keys())
        self.floor_tile_variants = (
            self.tile_sets["floor"][random.choice(floor_types)] if floor_types else []
        )

        wall_types = list(self.tile_sets["wall"].keys())
        self.wall_tile_variants = (
            self.tile_sets["wall"][random.choice(wall_types)] if wall_types else []
        )

        self.tile_variant_seed = [
            [random.randrange(10_000) for _ in row] for row in self.grid
        ]

    def _find_exit_cell(self):
        rows, cols = len(self.grid), len(self.grid[0])
        for row in range(rows - 1, -1, -1):
            for col in range(cols - 1, -1, -1):
                if self.grid[row][col] == 0:
                    return col, row
        return 1, 1

    @staticmethod
    def _manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def _spawn_monsters(self):
        entrance = (1, 1)
        count = monster_count_for_floor(self.floor)
        rows, cols = len(self.grid), len(self.grid[0])

        candidates = [
            (col, row)
            for row in range(rows)
            for col in range(cols)
            if self.grid[row][col] == 0
            and (col, row) != entrance
            and (col, row) != self.exit_pos
            and self._manhattan((col, row), entrance) >= MONSTER_MIN_DIST_FROM_ENTRANCE
        ]
        random.shuffle(candidates)

        monsters = []
        for pos in candidates:
            if len(monsters) >= count:
                break
            if all(
                self._manhattan(pos, (m.col, m.row)) >= MONSTER_MIN_DIST_BETWEEN
                for m in monsters
            ):
                monster = Monster(pos[0], pos[1])
                if self.monster_sprites:
                    monster.sprite_index = random.randrange(len(self.monster_sprites))
                monsters.append(monster)

        self.monsters = monsters

    def run(self):
        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue

            if self.game_over:
                self._handle_game_over_event(event)
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._enter_game_over()
                elif event.key == pygame.K_r:
                    self._generate_floor()

    def _enter_game_over(self):
        self.game_over = True
        self.is_new_record = self.floor > self.highscore["best_floor"]
        if self.is_new_record:
            self.name_input = ""
            pygame.key.start_text_input()

    def _handle_game_over_event(self, event):
        if self.is_new_record:
            if event.type == pygame.TEXTINPUT:
                if len(self.name_input) < HIGHSCORE_NAME_MAX_LEN:
                    self.name_input += event.text
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.name_input = self.name_input[:-1]
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    self._confirm_new_record()
                elif event.key == pygame.K_ESCAPE:
                    pygame.key.stop_text_input()
                    self.running = False
        else:
            if event.type == pygame.KEYDOWN:
                self.running = False

    def _confirm_new_record(self):
        name = self.name_input.strip() or "-"
        self.highscore = save_highscore(self.floor, name)
        pygame.key.stop_text_input()
        self.running = False

    def _update(self):
        if self.game_over:
            return

        now = pygame.time.get_ticks()

        if self.in_transition:
            if now >= self.transition_end_time:
                self.floor = self.next_floor
                self._generate_floor()
            return

        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1

        if dx or dy:
            self.player.try_move(dx, dy, self.grid, self.monsters, now, self._push_monster)

        self.player.update(now)

        for monster in self.monsters:
            monster.update(self.player, self.grid, self.monsters, now)

        if (self.player.col, self.player.row) == self.exit_pos:
            self.next_floor = self.floor + 1
            self.in_transition = True
            self.transition_end_time = now + FLOOR_MESSAGE_MS

    def _push_monster(self, monster, dx, dy, now):
        moved = 0
        for _ in range(KNOCKBACK_DISTANCE):
            nx, ny = monster.col + dx, monster.row + dy
            if not self._is_tile_open_for_monster(nx, ny, exclude=monster):
                break
            monster.col, monster.row = nx, ny
            moved += 1

        if moved == KNOCKBACK_DISTANCE:
            monster.state = "stunned"
            monster.stun_end_time = now + MONSTER_STUN_MS
        else:
            self.monsters.remove(monster)

        self.shield_effect_dir = (dx, dy)
        self.shield_effect_started = now
        self.shield_effect_until = now + SHIELD_EFFECT_MS

    def _is_tile_open_for_monster(self, col, row, exclude=None):
        rows, cols = len(self.grid), len(self.grid[0])
        if not (0 <= row < rows and 0 <= col < cols):
            return False
        if self.grid[row][col] == 1:
            return False
        if (col, row) == (self.player.col, self.player.row):
            return False
        for m in self.monsters:
            if m is exclude:
                continue
            if m.col == col and m.row == row:
                return False
        return True

    def _draw(self):
        self.screen.fill(COLOR_BG)

        if self.game_over:
            self._draw_game_over()
            pygame.display.flip()
            return

        self._update_camera()

        view_cols = SCREEN_WIDTH // TILE_SIZE
        view_rows = SCREEN_HEIGHT // TILE_SIZE
        row_end = min(len(self.grid), self.camera_row + view_rows)
        col_end = min(len(self.grid[0]), self.camera_col + view_cols)

        for row_idx in range(self.camera_row, row_end):
            row = self.grid[row_idx]
            for col_idx in range(self.camera_col, col_end):
                tile = row[col_idx]
                rect = pygame.Rect(
                    col_idx * TILE_SIZE + self.offset_x,
                    row_idx * TILE_SIZE + self.offset_y,
                    TILE_SIZE,
                    TILE_SIZE,
                )
                variants = self.wall_tile_variants if tile == 1 else self.floor_tile_variants
                if variants:
                    seed = self.tile_variant_seed[row_idx][col_idx]
                    sprite = variants[seed % len(variants)]
                    self.screen.blit(sprite, rect)
                else:
                    color = COLOR_WALL if tile == 1 else COLOR_FLOOR
                    pygame.draw.rect(self.screen, color, rect)

        exit_rect = pygame.Rect(
            self.exit_pos[0] * TILE_SIZE + self.offset_x,
            self.exit_pos[1] * TILE_SIZE + self.offset_y,
            TILE_SIZE,
            TILE_SIZE,
        )
        pygame.draw.rect(self.screen, COLOR_EXIT, exit_rect)

        for monster in self.monsters:
            self._draw_monster(monster)

        self._draw_player()

        now = pygame.time.get_ticks()
        if now < self.shield_effect_until:
            self._draw_shield_effect()

        floor_text = self.font.render(f"현재 층: {self.floor}", True, COLOR_TEXT)
        self.screen.blit(floor_text, (12, 12))

        best = self.highscore
        hs_text = self.font.render(
            f"최고 기록: {best['best_floor']}층 ({best['name']})", True, COLOR_TEXT
        )
        hs_rect = hs_text.get_rect(topright=(SCREEN_WIDTH - 12, 12))
        self.screen.blit(hs_text, hs_rect)

        hint = self.font.render("R: 새 미로  |  ESC: 종료", True, COLOR_TEXT)
        self.screen.blit(hint, (12, SCREEN_HEIGHT - 32))

        if self.in_transition:
            msg = self.big_font.render(f"{self.next_floor}층 도착!", True, COLOR_EXIT)
            msg_rect = msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(msg, msg_rect)

        pygame.display.flip()

    def _draw_monster(self, monster):
        rect = pygame.Rect(
            monster.col * TILE_SIZE + self.offset_x,
            monster.row * TILE_SIZE + self.offset_y,
            TILE_SIZE,
            TILE_SIZE,
        )

        if self.monster_sprites and monster.sprite_index is not None:
            frames = self.monster_sprites[monster.sprite_index]
            sprite = frames[monster.anim_frame % len(frames)]
            self.screen.blit(sprite, rect)
            if monster.state == "stunned":
                # 경직 상태를 스프라이트 위에 어두운 빨강 반투명 틴트로 표시
                overlay = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
                overlay.fill((*COLOR_MONSTER_STUNNED, 150))
                self.screen.blit(overlay, rect)
        else:
            # 에셋이 없을 때를 대비한 색상 사각형 대체 렌더링
            color = COLOR_MONSTER_STUNNED if monster.state == "stunned" else COLOR_MONSTER
            pad = 4
            inner = rect.inflate(-pad * 2, -pad * 2)
            pygame.draw.rect(self.screen, color, inner, border_radius=4)

    def _draw_player(self):
        rect = pygame.Rect(
            self.player.col * TILE_SIZE + self.offset_x,
            self.player.row * TILE_SIZE + self.offset_y,
            TILE_SIZE,
            TILE_SIZE,
        )
        frames = self.hero_sprites.get(self.player.facing_direction())
        if frames:
            sprite = frames[self.player.anim_frame % len(frames)]
            self.screen.blit(sprite, rect)
        else:
            # 에셋이 없을 때를 대비한 색상 사각형 대체 렌더링
            self.player.draw(self.screen, camera_offset=(-self.offset_x, -self.offset_y))

    def _draw_shield_effect(self):
        """밀치기 발동 시 플레이어가 바라보는 방향 앞에 표시되는 이펙트.

        shield_f1~4.png가 있으면 밀치기 지속 시간(SHIELD_EFFECT_MS) 동안
        한 번만 재생되는 임팩트 애니메이션으로 표시하고, 없으면 기존 색상
        사각형 테두리로 대체된다.
        """
        dx, dy = self.shield_effect_dir
        col = self.player.col + dx
        row = self.player.row + dy
        rect = pygame.Rect(
            col * TILE_SIZE + self.offset_x,
            row * TILE_SIZE + self.offset_y,
            TILE_SIZE,
            TILE_SIZE,
        )

        if self.shield_sprites:
            elapsed = pygame.time.get_ticks() - self.shield_effect_started
            progress = max(0.0, min(1.0, elapsed / SHIELD_EFFECT_MS))
            frame_idx = min(len(self.shield_sprites) - 1, int(progress * len(self.shield_sprites)))
            self.screen.blit(self.shield_sprites[frame_idx], rect)
        else:
            pygame.draw.rect(self.screen, COLOR_SHIELD, rect, width=4, border_radius=6)

    def _draw_game_over(self):
        title = self.big_font.render(f"도달 층수: {self.floor}층", True, COLOR_TEXT)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 90))
        self.screen.blit(title, title_rect)

        if self.is_new_record:
            record_text = self.font.render("신기록!", True, COLOR_EXIT)
            record_rect = record_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
            self.screen.blit(record_text, record_rect)

            prompt = self.font.render("이름을 입력하세요 (Enter로 확정):", True, COLOR_TEXT)
            prompt_rect = prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(prompt, prompt_rect)

            input_box = pygame.Rect(0, 0, 260, 44)
            input_box.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            pygame.draw.rect(self.screen, COLOR_FLOOR, input_box)
            pygame.draw.rect(self.screen, COLOR_EXIT, input_box, 2)

            name_surface = self.font.render(self.name_input, True, COLOR_TEXT)
            self.screen.blit(name_surface, (input_box.x + 10, input_box.y + 10))
        else:
            best = self.highscore
            info = self.font.render(
                f"최고 기록: {best['best_floor']}층 ({best['name']})", True, COLOR_TEXT
            )
            info_rect = info.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10))
            self.screen.blit(info, info_rect)

            hint = self.font.render("아무 키나 눌러 종료", True, COLOR_TEXT)
            hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
            self.screen.blit(hint, hint_rect)
