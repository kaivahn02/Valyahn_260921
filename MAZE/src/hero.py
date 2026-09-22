"""주인공(hero) 걷기 애니메이션 + 밀치기 방패 이펙트 스프라이트 로딩.

파일명 규칙 (assets/images/hero 안):
- "hero_<up|down|left|right>_f<프레임번호>.png"
- "shield_f<프레임번호>.png"
"""
import os
import re

import pygame

from src.settings import TILE_SIZE

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERO_SPRITE_DIR = os.path.join(_PROJECT_ROOT, "assets", "images", "hero")

_HERO_FILE_RE = re.compile(r"^hero_(up|down|left|right)_f(\d+)\.png$", re.IGNORECASE)
_SHIELD_FILE_RE = re.compile(r"^shield_f(\d+)\.png$", re.IGNORECASE)


def _scale_to_tile(surface):
    if surface.get_size() != (TILE_SIZE, TILE_SIZE):
        return pygame.transform.scale(surface, (TILE_SIZE, TILE_SIZE))
    return surface


def load_hero_sprites():
    """{"up": [Surface, ...], "down": [...], "left": [...], "right": [...]} 형태로 반환.

    폴더가 없거나 인식되는 파일이 없으면 빈 dict를 반환하고, 이 경우 렌더링 쪽에서
    기존 색상 사각형으로 자동 대체된다(에셋이 없어도 게임이 죽지 않도록).
    """
    if not os.path.isdir(HERO_SPRITE_DIR):
        return {}

    raw = {}
    for fname in os.listdir(HERO_SPRITE_DIR):
        match = _HERO_FILE_RE.match(fname)
        if not match:
            continue
        direction = match.group(1).lower()
        frame_num = int(match.group(2))
        surf = _scale_to_tile(
            pygame.image.load(os.path.join(HERO_SPRITE_DIR, fname)).convert_alpha()
        )
        raw.setdefault(direction, []).append((frame_num, surf))

    result = {}
    for direction, frames in raw.items():
        frames.sort(key=lambda pair: pair[0])
        result[direction] = [surf for _, surf in frames]
    return result


def load_shield_sprites():
    """[Surface, ...] (프레임번호 순). 없으면 빈 리스트(기존 색상 테두리로 대체)."""
    if not os.path.isdir(HERO_SPRITE_DIR):
        return []

    items = []
    for fname in os.listdir(HERO_SPRITE_DIR):
        match = _SHIELD_FILE_RE.match(fname)
        if not match:
            continue
        frame_num = int(match.group(1))
        surf = _scale_to_tile(
            pygame.image.load(os.path.join(HERO_SPRITE_DIR, fname)).convert_alpha()
        )
        items.append((frame_num, surf))

    items.sort(key=lambda pair: pair[0])
    return [surf for _, surf in items]
