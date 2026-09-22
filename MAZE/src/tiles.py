"""바닥/벽 타일 에셋 로딩.

assets/images/tiles 안의 파일명은 "floor_dirt_1.png", "wall_hanok_tile_3.png"처럼
"<카테고리>_<종류>_<변형번호>.png" 형식이다. 같은 <종류> 안의 여러 변형 이미지는
같은 스테이지 안에서 섞어 써서 타일에 시각적 변화를 주기 위한 것이고, <종류> 자체는
스테이지(층)마다 하나만 골라 고정한다(Game._generate_floor에서 처리).
"""
import os
import re

import pygame

from src.settings import TILE_SIZE

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TILE_DIR = os.path.join(_PROJECT_ROOT, "assets", "images", "tiles")

_TILE_NAME_RE = re.compile(r"^(floor|wall)_(.+)_(\d+)\.png$", re.IGNORECASE)


def _scale_to_tile(surface):
    """원본 에셋 해상도와 무관하게 현재 TILE_SIZE에 맞춰 표시 크기를 맞춘다."""
    if surface.get_size() != (TILE_SIZE, TILE_SIZE):
        return pygame.transform.scale(surface, (TILE_SIZE, TILE_SIZE))
    return surface


def load_tile_sets():
    """{"floor": {"dirt": [Surface, ...], "mud": [...], "stone": [...]},
        "wall": {"cave": [...], "hanok_thatch": [...], "hanok_tile": [...]}} 형태로 반환.

    assets/images/tiles 폴더가 없거나 이름 규칙에 맞는 파일이 없으면 각 카테고리가
    빈 dict로 남고, 이 경우 렌더링 쪽에서 기존 색상 사각형으로 자동 대체된다
    (에셋이 없어도 게임이 죽지 않도록).
    """
    result = {"floor": {}, "wall": {}}
    if not os.path.isdir(TILE_DIR):
        return result

    raw = {"floor": {}, "wall": {}}
    for fname in sorted(os.listdir(TILE_DIR)):
        match = _TILE_NAME_RE.match(fname)
        if not match:
            continue
        category = match.group(1).lower()
        subtype = match.group(2).lower()
        variant = int(match.group(3))
        surf = _scale_to_tile(pygame.image.load(os.path.join(TILE_DIR, fname)).convert_alpha())
        raw[category].setdefault(subtype, []).append((variant, surf))

    for category, subtypes in raw.items():
        for subtype, items in subtypes.items():
            items.sort(key=lambda pair: pair[0])
            result[category][subtype] = [surf for _, surf in items]

    return result
