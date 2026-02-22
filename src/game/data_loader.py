import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "stores"
RESOURCE_DIR = PROJECT_ROOT / "resources"


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_monsters() -> list[dict[str, Any]]:
    return _load_json(DATA_DIR / "monsters.json")["monsters"]


def load_skills() -> dict[str, list[dict[str, Any]]]:
    return _load_json(DATA_DIR / "skills.json")


def load_potions() -> list[dict[str, Any]]:
    return _load_json(DATA_DIR / "potions.json")["potions"]


def load_opening_lines() -> list[str]:
    return _load_json(RESOURCE_DIR / "opening_text.json")["opening_lines"]
