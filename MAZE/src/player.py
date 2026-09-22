"""플레이어 엔티티: 타일 기반 이동 + 벽/몬스터 충돌 처리."""
import pygame

from src.settings import (
    COLOR_PLAYER,
    MOVE_COOLDOWN_MS,
    PLAYER_ANIM_FRAME_MS,
    PLAYER_SIZE,
    TILE_SIZE,
)

_DIRECTION_BY_DELTA = {
    (0, -1): "up",
    (0, 1): "down",
    (-1, 0): "left",
    (1, 0): "right",
}


class Player:
    def __init__(self, col: int, row: int):
        self.col = col
        self.row = row
        self.last_move_time = 0
        self.facing = (0, 1)
        self.anim_frame = 0
        self.anim_last_switch = 0

    def facing_direction(self) -> str:
        return _DIRECTION_BY_DELTA.get(self.facing, "down")

    def update(self, now_ms: int):
        """걷기 애니메이션 프레임을 시간 기반으로 순환시킨다(이동 여부와 무관하게 항상)."""
        if now_ms - self.anim_last_switch >= PLAYER_ANIM_FRAME_MS:
            self.anim_frame += 1
            self.anim_last_switch = now_ms

    def try_move(self, dx: int, dy: int, grid, monsters, now_ms: int, on_push):
        if now_ms - self.last_move_time < MOVE_COOLDOWN_MS:
            return

        new_col = self.col + dx
        new_row = self.row + dy

        if not (0 <= new_row < len(grid) and 0 <= new_col < len(grid[0])):
            return
        if grid[new_row][new_col] == 1:
            return

        self.facing = (dx, dy)

        target = next(
            (m for m in monsters if m.col == new_col and m.row == new_row), None
        )
        if target is not None:
            # 몬스터가 막고 있으면 이동 대신 밀치기를 발동하고, 플레이어는 제자리를 유지한다.
            self.last_move_time = now_ms
            on_push(target, dx, dy, now_ms)
            return

        self.col = new_col
        self.row = new_row
        self.last_move_time = now_ms

    def draw(self, surface, camera_offset=(0, 0)):
        """스프라이트 에셋이 없을 때 쓰는 대체 렌더링(색상 사각형)."""
        pad = (TILE_SIZE - PLAYER_SIZE) // 2
        rect = pygame.Rect(
            self.col * TILE_SIZE + pad - camera_offset[0],
            self.row * TILE_SIZE + pad - camera_offset[1],
            PLAYER_SIZE,
            PLAYER_SIZE,
        )
        pygame.draw.rect(surface, COLOR_PLAYER, rect, border_radius=4)
