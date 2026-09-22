"""최고 기록(최고 도달 층수) 저장/불러오기.

프로젝트 루트의 highscore.json 파일에
{"best_floor": 0, "name": "-"} 형태로 저장한다.
"""
import json
import os

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HIGHSCORE_PATH = os.path.join(_PROJECT_ROOT, "highscore.json")

DEFAULT_HIGHSCORE = {"best_floor": 0, "name": "-"}


def load_highscore() -> dict:
    if not os.path.exists(HIGHSCORE_PATH):
        return dict(DEFAULT_HIGHSCORE)

    try:
        with open(HIGHSCORE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {
            "best_floor": int(data.get("best_floor", 0)),
            "name": str(data.get("name", "-")) or "-",
        }
    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        return dict(DEFAULT_HIGHSCORE)


def save_highscore(best_floor: int, name: str) -> dict:
    data = {"best_floor": int(best_floor), "name": name or "-"}
    with open(HIGHSCORE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data
