"""몬스터 엔티티와 층별 몬스터 수 계산."""
import os
import random
import re

import pygame

from src.settings import (
    MONSTER_ANIM_FRAME_MS,
    MONSTER_BASE_COUNT,
    MONSTER_BLOCK_FLOORS,
    MONSTER_CHASE_RADIUS,
    MONSTER_COUNT_MULTIPLIER,
    MONSTER_HIGH_FLOOR_STEP,
    MONSTER_HIGH_FLOOR_THRESHOLD,
    MONSTER_MOVE_COOLDOWN_MS,
    MONSTER_WANDER_MOVE_CHANCE,
    TILE_SIZE,
)

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MONSTER_SPRITE_DIR = os.path.join(_PROJECT_ROOT, "assets", "images", "monster")

# 예: "01_gumiho_f1.png" -> 순서=01, 이름=gumiho, 프레임=1
_MONSTER_FILE_RE = re.compile(r"^(\d+)_(.+)_f(\d+)\.png$", re.IGNORECASE)


def _scale_to_tile(surface):
    """원본 에셋 해상도와 무관하게 현재 TILE_SIZE에 맞춰 표시 크기를 맞춘다."""
    if surface.get_size() != (TILE_SIZE, TILE_SIZE):
        return pygame.transform.scale(surface, (TILE_SIZE, TILE_SIZE))
    return surface


def load_monster_sprites():
    """assets/images/monster 아래의 PNG 파일들에서 몬스터별 애니메이션 프레임을 불러온다.

    파일명 규칙: "<순서>_<이름>_f<프레임번호>.png" (예: "01_gumiho_f1.png").
    같은 <순서>_<이름>을 가진 파일들을 한 그룹으로 묶고, 프레임번호 순으로 정렬해
    순환 재생용 프레임 리스트로 반환한다. 규칙에 맞지 않는 파일(예: 원본 zip)은
    무시한다.

    폴더가 없거나 인식되는 파일이 하나도 없으면 빈 리스트를 반환하고, 이 경우
    렌더링 쪽에서 기존 색상 사각형으로 자동 대체된다(에셋이 없어도 게임이
    죽지 않도록).
    """
    if not os.path.isdir(MONSTER_SPRITE_DIR):
        return []

    groups = {}  # (순서, 이름) -> [(프레임번호, Surface), ...]
    for fname in os.listdir(MONSTER_SPRITE_DIR):
        match = _MONSTER_FILE_RE.match(fname)
        if not match:
            continue
        order = int(match.group(1))
        name = match.group(2).lower()
        frame_num = int(match.group(3))
        surf = _scale_to_tile(
            pygame.image.load(os.path.join(MONSTER_SPRITE_DIR, fname)).convert_alpha()
        )
        groups.setdefault((order, name), []).append((frame_num, surf))

    sprite_sets = []
    for key in sorted(groups.keys()):
        frames = [surf for _, surf in sorted(groups[key], key=lambda pair: pair[0])]
        if frames:
            sprite_sets.append(frames)

    return sprite_sets


def monster_count_for_floor(floor: int) -> int:
    return _base_monster_count_for_floor(floor) * MONSTER_COUNT_MULTIPLIER


def _base_monster_count_for_floor(floor: int) -> int:
    if floor <= MONSTER_HIGH_FLOOR_THRESHOLD:
        blocks = (floor - 1) // MONSTER_BLOCK_FLOORS
        return MONSTER_BASE_COUNT + blocks

    base = _base_monster_count_for_floor(MONSTER_HIGH_FLOOR_THRESHOLD)
    extra_blocks = (floor - MONSTER_HIGH_FLOOR_THRESHOLD - 1) // MONSTER_BLOCK_FLOORS + 1
    return base + extra_blocks * MONSTER_HIGH_FLOOR_STEP


class Monster:
    def __init__(self, col: int, row: int):
        self.col = col
        self.row = row
        self.state = "wandering"  # wandering | chasing | stunned
        self.stun_end_time = 0
        self.last_move_time = 0
        self.sprite_index = None  # Game이 스폰 시 배정 (assets/images/monster 중 하나)
        self.anim_frame = 0
        self.anim_last_switch = 0

    def update(self, player, grid, monsters, now):
        self._advance_animation(now)

        if self.state == "stunned":
            if now >= self.stun_end_time:
                self.state = "wandering"
            return

        dist = abs(self.col - player.col) + abs(self.row - player.row)
        self.state = "chasing" if dist <= MONSTER_CHASE_RADIUS else "wandering"

        if now - self.last_move_time < MONSTER_MOVE_COOLDOWN_MS:
            return

        if self.state == "chasing":
            step = self._choose_step(player, grid, monsters)
        else:
            step = self._choose_wander_step(grid, monsters, player)

        if step is not None:
            dx, dy = step
            self.col += dx
            self.row += dy
            self.last_move_time = now

    def _advance_animation(self, now):
        if now - self.anim_last_switch >= MONSTER_ANIM_FRAME_MS:
            self.anim_frame += 1
            self.anim_last_switch = now

    def _choose_step(self, player, grid, monsters):
        col_diff = player.col - self.col
        row_diff = player.row - self.row

        moves = []
        if abs(col_diff) >= abs(row_diff):
            if col_diff != 0:
                moves.append((1 if col_diff > 0 else -1, 0))
            if row_diff != 0:
                moves.append((0, 1 if row_diff > 0 else -1))
        else:
            if row_diff != 0:
                moves.append((0, 1 if row_diff > 0 else -1))
            if col_diff != 0:
                moves.append((1 if col_diff > 0 else -1, 0))

        for dx, dy in moves:
            nx, ny = self.col + dx, self.row + dy
            if self._is_open(nx, ny, grid, monsters, player):
                return dx, dy
        return None

    def _choose_wander_step(self, grid, monsters, player):
        """주인공이 감지 범위 밖일 때: 확률적으로 무작위 방향 한 칸을 골라 배회한다."""
        if random.random() > MONSTER_WANDER_MOVE_CHANCE:
            return None

        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = self.col + dx, self.row + dy
            if self._is_open(nx, ny, grid, monsters, player):
                return dx, dy
        return None

    @staticmethod
    def _is_open(col, row, grid, monsters, player):
        if not (0 <= row < len(grid) and 0 <= col < len(grid[0])):
            return False
        if grid[row][col] == 1:
            return False
        if (col, row) == (player.col, player.row):
            return False
        if any(m.col == col and m.row == row for m in monsters):
            return False
        return True
