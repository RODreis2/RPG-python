import random

from ..models import Monster, Player
from .combat import battle
from .map_generator import DungeonMap, TILE_FLOOR, render_map


def explore_dungeon(
    player: Player,
    monster_data: list[dict],
    skills_by_class: dict[str, list[dict[str, float]]],
) -> bool:
    dungeon = DungeonMap()
    grid = dungeon.generate()
    player_x, player_y = dungeon.random_floor_tile()
    exit_x, exit_y = dungeon.random_floor_tile()
    while (exit_x, exit_y) == (player_x, player_y):
        exit_x, exit_y = dungeon.random_floor_tile()

    print("\n=== Dungeon ===")
    print("Move with W/A/S/D. Reach '>' to finish the run. Press Q to leave.")

    while player.is_alive():
        print()
        print(render_map(grid, (player_x, player_y), (exit_x, exit_y)))
        print(f"\n{player.name} HP: {player.hp}/{player.max_hp} | Gold: {player.gold}")
        command = input("Action: ").strip().lower()
        if command == "q":
            print("You retreat from the dungeon.")
            return True

        dx, dy = _movement_delta(command)
        if (dx, dy) == (0, 0):
            print("Invalid move. Use W/A/S/D or Q.")
            continue

        next_x = player_x + dx
        next_y = player_y + dy
        if (
            next_x < 0
            or next_y < 0
            or next_y >= len(grid)
            or next_x >= len(grid[0])
            or grid[next_y][next_x] != TILE_FLOOR
        ):
            print("A wall blocks your path.")
            continue

        player_x, player_y = next_x, next_y
        if (player_x, player_y) == (exit_x, exit_y):
            bonus_gold = random.randint(10, 22)
            player.gold += bonus_gold
            print(f"You found the dungeon exit and secured {bonus_gold} bonus gold.")
            return True

        if not _movement_event(player, monster_data, skills_by_class):
            return False

    return False


def _movement_delta(command: str) -> tuple[int, int]:
    if command == "w":
        return 0, -1
    if command == "s":
        return 0, 1
    if command == "a":
        return -1, 0
    if command == "d":
        return 1, 0
    return 0, 0


def _movement_event(
    player: Player,
    monster_data: list[dict],
    skills_by_class: dict[str, list[dict[str, float]]],
) -> bool:
    roll = random.random()
    if roll < 0.27:
        template = random.choice(monster_data)
        monster = Monster(
            name=template["name"],
            hp=template["hp"],
            strength=template["strength"],
            defense=template["defense"],
            speed=template["speed"],
            xp_reward=template["xp_reward"],
            gold_reward=template["gold_reward"],
        )
        return battle(player, monster, skills_by_class.get(player.archetype, []))

    if roll < 0.38:
        found_gold = random.randint(4, 14)
        player.gold += found_gold
        print(f"You found {found_gold} gold on the dungeon floor.")
        return True

    if roll < 0.46 and player.potions < 5:
        player.potions += 1
        print("You found a potion.")
        return True

    return True
