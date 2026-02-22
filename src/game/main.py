from pathlib import Path
import sys

if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from src.game.game_engine import GameEngine
else:
    from .game_engine import GameEngine


def main() -> None:
    engine = GameEngine()
    engine.run()


if __name__ == "__main__":
    main()
