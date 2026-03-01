import curses
import math
import os
import random
import time
from dataclasses import dataclass

from .data_loader import load_monsters, load_opening_lines, load_potions, load_skills
from .models import Monster, Player
from .systems.archer_training import start_archer_training
from .systems.meditation_training import start_meditation_training
from .systems.warrior_training import start_warrior_training
from .systems.map_generator import DungeonMap, TILE_DOOR, TILE_FLOOR


CLASS_TEMPLATES = {
    "Warrior": {"hp": 120, "mp": 16, "strength": 16, "defense": 12, "speed": 8},
    "Mage": {"hp": 85, "mp": 36, "strength": 18, "defense": 7, "speed": 10},
    "Archer": {"hp": 95, "mp": 20, "strength": 14, "defense": 9, "speed": 14},
}

COMBAT_OPTIONS = ["Attack", "Skill", "Item", "Run"]
CLASS_ART: dict[str, list[str]] = {
    "Warrior": [
        "              /|                    ",
        " _______________)|..                ",
        "<'______________<(,_|)               ",
        "       .((()))| )) << YARGH! >>      ",
        "       (======)| \\                   ",
        "      ((( \"_\"()|_ \\                  ",
        "     '()))(_)/_/ ' )                 ",
        "     .--/_\\ /(  /./                  ",
        "    /'._.--\\ .-(_/                   ",
        "   / / )\\___:___)                    ",
        "  ( -.'.._  |  /                     ",
        "   \\  \\_\\ ( | )                      ",
        "    '. /\\)_(_)|                      ",
        "      '-|  XX |                      ",
        "       %%%%%%%%                      ",
        "      / %%%%%%%\\                     ",
        "     ( /.-'%%%. \\                    ",
        "    /(.'   %%\\ :|                    ",
        "   / ,|    %  ) )                    ",
        " _|___)   %  (__|_                   ",
        " )___/       )___(                   ",
        "  |x/      mrf\\ >                    ",
        "  |x)         / '.                   ",
        "  |x\\       _(____''.__              ",
        "--\\ -\\--                              ",
        " --\\__|--                             ",
    ],
    "Mage": [
        "                    ____                     ",
        "                  .'* *.'                    ",
        "               __/_*_*(_                     ",
        "              / _______ \\                    ",
        "             _\\_)/___\\(_/_                   ",
        "            / _((\\- -/))_ \\                  ",
        "            \\ \\())(-)(()/ /                  ",
        "             ' \\(((()))/ '                   ",
        "            / ' \\)).))/ ' \\                  ",
        "           / _ \\ - | - /_  \\                 ",
        "          (   ( .;''';. .'  )                ",
        "          _\"__ /    )\\ __\"/_                 ",
        "            \\/  \\   ' /  \\/                  ",
        "             .'  '...' ' )                   ",
        "              / /  |  \\ \\                    ",
        "             / .   .   . \\                   ",
        "            /   .     .   \\                  ",
        "           /   /   |   \\   \\                 ",
        "         .'   /    b    '.  '.               ",
        "     _.-'    /     Bb     '-. '-._           ",
        " _.-'       |      BBb       '-.  '-.        ",
        "(________mrf\\____.dBBBb.________)____)       ",
    ],
    "Archer": [
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢈⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣤⠎⠠⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
        "⠀⠀⠀⢀⣠⣴⣶⡶⠿⠿⠛⠛⠉⠀⠀⠀⢂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
        "⠙⠶⢤⣿⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
        "⠀⣰⣶⣮⡁⠠⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
        "⠀⣘⡻⢿⣿⣦⣄⡉⠢⢄⡀⠀⠀⠀⠀⠀⠀⠀⢠⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
        "⢰⣿⡇⠀⠙⠻⣿⣿⣷⣦⡈⠑⠤⣀⠀⠀⠀⣠⣴⣶⣦⣄⠀⠀⠀⠀⠀⠀⠀⠀",
        "⠀⢿⣧⠀⠀⠀⠀⠉⠻⣿⣿⣿⣷⣦⣍⠲⢄⣿⣿⣿⣿⣿⡆⠀⠀⠀⠀⠀⠀⠀",
        "⠀⠈⢿⣧⠀⠀⠀⠀⠀⠈⠻⢟⢿⣿⣿⣇⣿⣷⣮⡙⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀",
        "⠀⠀⠀⠻⣧⡀⠀⠀⠀⠀⠀⠀⠘⣿⣿⣿⣿⣿⣿⣿⢰⣶⣭⡳⣄⡀⠀⠀⠀⠀",
        "⠀⠀⠀⠀⠹⣧⠀⠀⠀⠀⠀⠀⠀⣬⣿⣿⣿⣿⣿⡟⣼⣿⣿⣿⣶⣿⣵⣶⣄⠀",
        "⠀⠀⠀⠀⠀⣿⠀⠀⡀⠠⠀⠀⠁⢿⣿⣿⣿⣿⠏⣼⣿⣟⠿⠿⣿⣿⣿⣿⣿⣇",
        "⠀⠀⠀⠀⡠⠗⠂⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⢸⣿⡿⠋⠀⠀⠀⠈⠉⠉⠉⠉",
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⣸⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀",
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⡏⠻⣿⣷⣟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀",
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⡿⣿⣄⠈⠙⠻⢷⣄⠀⠀⠀⠀⠀⠀⠀⠀",
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠳⡈⠙⠛⠦⢄⠀⠉⠳⣄⠀⠀⠀⠀⠀⠀",
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠀⠀⠀⠀⠀⠀⠀⠈⢂⠀⠀⠀⠀⠀",
    ],
}
ENEMY_ART: dict[str, list[str]] = {
    "goblin": [
        "   ,      ,   ",
        "  /(.-\"\"-.)\\  ",
        "  |\\  \\/  /|  ",
        "  | \\ /\\ / |  ",
        "  \\_/\\  /\\_/  ",
        "   /  \\/  \\   ",
    ],
    "slime": [
        "    ______    ",
        " .-'      '-. ",
        "/  .-\"\"\"\"-.  \\",
        "| /  .--.  \\ |",
        "| | (____) | |",
        "\\  '-.__.-'  /",
        " '-.______.-' ",
    ],
    "bone": [
        "    .-\"\"\"-.   ",
        "   /  .-.  \\  ",
        "  |  /   \\  | ",
        "  |  \\___/  | ",
        "  | .-===-. | ",
        "  | |:.:.:| | ",
        "  |_|:.:.:|_| ",
    ],
}


@dataclass
class DungeonSession:
    grid: list[list[int]]
    player_x: int
    player_y: int
    exit_x: int
    exit_y: int
    treasures: dict[tuple[int, int], str]
    boss_pos: tuple[int, int] | None = None
    boss_defeated: bool = True
    message: str = "Explore carefully."


class GameEngine:
    def __init__(self) -> None:
        self.player: Player | None = None
        self.monsters = load_monsters()
        self.skills = load_skills()
        self.potions = load_potions()
        self.opening_lines = load_opening_lines()
        self._bg_seed = random.randint(0, 999_999)
        self._typing_enabled = True
        self._typing_delay = 0.02
        self._typing_skip_until = 0.0
        self.dungeon_level = 1
        self._unicode_ui = os.environ.get("TERM_REALMS_ASCII", "0") != "1"
        self._monster_hit_flash_until = 0.0

    def run(self) -> None:
        curses.wrapper(self._run_curses)

    def _run_curses(self, stdscr: curses.window) -> None:
        curses.curs_set(0)
        stdscr.nodelay(False)
        stdscr.keypad(True)
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
        curses.mouseinterval(0)
        self._init_colors()

        while True:
            choice = self._menu_screen(
                stdscr,
                "TERMINAL REALMS",
                ["Create Character", "Exit"],
                subtitle="ASCII Edition",
            )
            if choice == 1:
                return

            archetype = self._choose_class(stdscr)
            name = self._input_name(stdscr)
            stats = CLASS_TEMPLATES[archetype]
            self.player = Player(
                name=name,
                archetype=archetype,
                max_hp=stats["hp"],
                hp=stats["hp"],
                max_mp=stats["mp"],
                mp=stats["mp"],
                strength=stats["strength"],
                defense=stats["defense"],
                speed=stats["speed"],
            )
            self._main_menu_loop(stdscr)
            if not self._ask_play_again(stdscr):
                return

    def _init_colors(self) -> None:
        if not curses.has_colors():
            return
        curses.start_color()
        curses.use_default_colors()
        # Warm, muted handheld-inspired palette.
        curses.init_pair(1, curses.COLOR_BLUE, -1)      # border/navy
        curses.init_pair(2, curses.COLOR_GREEN, -1)     # positive/accent
        curses.init_pair(3, curses.COLOR_YELLOW, -1)    # highlight/select
        curses.init_pair(4, curses.COLOR_RED, -1)
        curses.init_pair(5, curses.COLOR_WHITE, -1)     # primary text
        curses.init_pair(6, curses.COLOR_MAGENTA, -1)   # flavor text
        curses.init_pair(7, curses.COLOR_WHITE, -1)     # muted text (with A_DIM)
        curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(9, curses.COLOR_BLACK, curses.COLOR_YELLOW)
        curses.init_pair(10, curses.COLOR_BLACK, curses.COLOR_RED)
        curses.init_pair(11, curses.COLOR_WHITE, curses.COLOR_BLUE)

    def _main_menu_loop(self, stdscr: curses.window) -> None:
        assert self.player is not None
        menu_info = {
            "Dungeon": "Risk combat, clear floors, and earn gold by reaching the door.",
            "Market": "Spend gold on potions to sustain longer dungeon runs.",
            "Training": "Class drills: Warrior reflex, Mage meditation, Archer conditioning.",
            "Status": "Review stats, progression, and your class portrait.",
            "Quit": "Leave this run and return to the start menu.",
        }
        while self.player.is_alive():
            option = self._menu_screen(
                stdscr,
                f"{self.player.name} the {self.player.archetype}",
                ["Dungeon", "Market", "Training", "Status", "Quit"],
                subtitle="Wander, grow, survive.",
                status=self._status_line(),
                info_map=menu_info,
                context_tag="main",
            )

            if option == 0:
                self._dungeon_mode(stdscr)
            elif option == 1:
                self._market_mode(stdscr)
            elif option == 2:
                self._training_mode(stdscr)
            elif option == 3:
                self._status_mode(stdscr)
            else:
                return

    def _dungeon_mode(self, stdscr: curses.window) -> None:
        assert self.player is not None
        frame_y, frame_x, frame_h, frame_w = self._frame_rect(stdscr)

        map_w = max(24, min(56, frame_w - 8))
        map_h = max(10, min(24, frame_h - 10))

        dungeon = DungeonMap()
        grid = dungeon.generate(width=map_w, height=map_h)

        player_x, player_y = dungeon.random_floor_tile()
        exit_x, exit_y = dungeon.random_floor_tile()
        while (exit_x, exit_y) == (player_x, player_y):
            exit_x, exit_y = dungeon.random_floor_tile()

        occupied: set[tuple[int, int]] = {(player_x, player_y), (exit_x, exit_y)}
        boss_pos: tuple[int, int] | None = None
        if self.dungeon_level % 5 == 0:
            boss_pos = self._generate_dungeon_boss_pos(dungeon, occupied)
            if boss_pos is not None:
                occupied.add(boss_pos)

        treasures = self._generate_dungeon_treasures(
            dungeon,
            occupied=occupied,
        )
        session = DungeonSession(
            grid,
            player_x,
            player_y,
            exit_x,
            exit_y,
            treasures,
            boss_pos=boss_pos,
            boss_defeated=boss_pos is None,
        )
        session.grid[exit_y][exit_x] = TILE_DOOR
        session.message = f"Dungeon Level {self.dungeon_level} | Treasures: {len(session.treasures)}"
        if session.boss_pos is not None and not session.boss_defeated:
            session.message += " | Boss: Hunt B before the door."

        while self.player.is_alive():
            self._draw_dungeon(stdscr, session)
            key = stdscr.getch()
            if key in (ord("q"), ord("Q"), 27):
                return

            dx, dy = self._delta_from_key(key)
            if (dx, dy) == (0, 0):
                session.message = "Use W/A/S/D or arrow keys."
                continue

            nx = session.player_x + dx
            ny = session.player_y + dy
            if (
                nx < 0
                or ny < 0
                or ny >= len(session.grid)
                or nx >= len(session.grid[0])
                or not self._is_walkable_tile(session.grid[ny][nx])
            ):
                session.message = "A wall blocks your way."
                continue

            session.player_x, session.player_y = nx, ny
            if (
                (nx, ny) == (session.exit_x, session.exit_y)
                and session.boss_pos is not None
                and not session.boss_defeated
            ):
                session.message = "A dark seal blocks the door. Defeat the boss first."
                continue

            if (nx, ny) == session.boss_pos and not session.boss_defeated:
                boss = self._create_dungeon_boss()
                if not self._combat_mode(stdscr, boss, session):
                    return
                session.boss_defeated = True
                bounty = random.randint(25, 45)
                self.player.gold += bounty
                session.message = f"Boss defeated: {boss.name}. +{bounty} gold."
                continue

            if (nx, ny) == (session.exit_x, session.exit_y):
                bonus = random.randint(10, 22)
                self.player.gold += bonus
                self.dungeon_level += 1
                self._toast(stdscr, f"Door reached. +{bonus} gold. Dungeon level {self.dungeon_level}.")
                return

            if (nx, ny) in session.treasures:
                session.message = self._collect_dungeon_treasure(session, (nx, ny))
                continue

            if not self._dungeon_event(stdscr, session):
                return

    def _dungeon_event(self, stdscr: curses.window, session: DungeonSession) -> bool:
        assert self.player is not None
        roll = random.random()
        if roll < 0.10:
            template = self._pick_monster_template()
            tier = self._difficulty_tier()
            scaled_hp = max(1, int(round(template["hp"] * 0.75 * (1 + 0.15 * tier))))
            scaled_strength = max(1, int(round(template["strength"] * (1 + 0.10 * tier))))
            monster = Monster(
                name=template["name"],
                hp=scaled_hp,
                strength=scaled_strength,
                defense=template["defense"],
                speed=template["speed"],
                xp_reward=template["xp_reward"],
                gold_reward=template["gold_reward"],
            )
            return self._combat_mode(stdscr, monster, session)

        if roll < 0.35:
            found = random.randint(4, 12)
            self.player.gold += found
            session.message = f"You found {found} gold."
            return True

        if roll < 0.50 and self.player.potions < 9:
            self.player.potions += 1
            session.message = "You found a potion."
            return True

        session.message = "The corridor is quiet..."
        return True

    def _difficulty_tier(self) -> int:
        return max(0, (self.dungeon_level - 1) // 5)

    def _pick_monster_template(self) -> dict:
        weighted: list[dict] = []
        for monster in self.monsters:
            name = monster.get("name", "").lower()
            copies = 1 if "slime" in name else 3
            weighted.extend([monster] * copies)
        return random.choice(weighted) if weighted else random.choice(self.monsters)

    def _generate_dungeon_treasures(
        self,
        dungeon: DungeonMap,
        occupied: set[tuple[int, int]],
    ) -> dict[tuple[int, int], str]:
        loot_pool = [
            "Iron Sword",
            "Hunter Bow",
            "Arcane Tome",
            "Guardian Charm",
            "Potion Cache",
            "Gold Satchel",
        ]
        count = random.randint(2, 4)
        treasures: dict[tuple[int, int], str] = {}
        attempts = 0
        while len(treasures) < count and attempts < 220:
            attempts += 1
            tx, ty = dungeon.random_floor_tile()
            if (tx, ty) in occupied or (tx, ty) in treasures:
                continue
            treasures[(tx, ty)] = random.choice(loot_pool)
        return treasures

    def _generate_dungeon_boss_pos(
        self,
        dungeon: DungeonMap,
        occupied: set[tuple[int, int]],
    ) -> tuple[int, int] | None:
        attempts = 0
        while attempts < 200:
            attempts += 1
            bx, by = dungeon.random_floor_tile()
            if (bx, by) in occupied:
                continue
            return bx, by
        return None

    def _create_dungeon_boss(self) -> Monster:
        template = max(
            self.monsters,
            key=lambda m: int(m.get("hp", 1)) + int(m.get("strength", 1)) * 3,
        )
        tier = self._difficulty_tier()
        hp = max(1, int(round(template["hp"] * 1.8 * (1 + 0.18 * tier))))
        strength = max(1, int(round(template["strength"] * (1 + 0.20 * tier))))
        defense = max(1, int(round(template["defense"] * (1 + 0.15 * tier))))
        speed = max(1, int(round(template["speed"] * (1 + 0.08 * tier))))
        return Monster(
            name=f"Boss {template['name']}",
            hp=hp,
            strength=strength,
            defense=defense,
            speed=speed,
            xp_reward=max(1, int(round(template["xp_reward"] * 2.0))),
            gold_reward=max(1, int(round(template["gold_reward"] * 2.0))),
        )

    def _collect_dungeon_treasure(self, session: DungeonSession, pos: tuple[int, int]) -> str:
        assert self.player is not None
        loot = session.treasures.pop(pos, "Mysterious Cache")
        if loot == "Iron Sword":
            gain = 3 if self.player.archetype == "Warrior" else 2
            self.player.strength += gain
            return f"Treasure found: Iron Sword. +{gain} STR."
        if loot == "Hunter Bow":
            self.player.speed += 2
            if self.player.archetype == "Archer":
                self.player.strength += 1
                return "Treasure found: Hunter Bow. +2 SPD, +1 STR."
            return "Treasure found: Hunter Bow. +2 SPD."
        if loot == "Arcane Tome":
            self.player.max_mp += 4
            restored = self.player.restore_mp(8)
            return f"Treasure found: Arcane Tome. +4 MAX MP, +{restored} MP."
        if loot == "Guardian Charm":
            self.player.defense += 2
            return "Treasure found: Guardian Charm. +2 DEF."
        if loot == "Potion Cache":
            add = random.randint(1, 2)
            self.player.potions += add
            healed = self.player.heal(12)
            return f"Treasure found: Potion Cache. +{add} potion(s), +{healed} HP."

        gold = random.randint(12, 28)
        self.player.gold += gold
        return f"Treasure found: Gold Satchel. +{gold} gold."

    def _combat_mode(self, stdscr: curses.window, monster: Monster, session: DungeonSession) -> bool:
        assert self.player is not None
        self._monster_hit_flash_until = 0.0
        log: list[str] = []
        class_skills = self.skills.get(self.player.archetype, [])
        selected = 0
        self._append_combat_log_typed(
            stdscr, monster, session, selected, log, f"A wild {monster.name} appears."
        )

        while self.player.is_alive() and monster.is_alive():
            self._draw_combat(stdscr, monster, log, session, selected)
            key = stdscr.getch()

            moved, selected = self._move_combat_selection(selected, key)
            if moved:
                continue
            if key not in (10, 13, curses.KEY_ENTER):
                continue

            action = COMBAT_OPTIONS[selected]
            if action == "Attack":
                dmg, attack_note = self._roll_player_damage(self.player.strength, monster.defense)
                monster.hp -= dmg
                self._monster_hit_flash_until = time.monotonic() + 0.28
                self._animate_monster_hit_flash(stdscr, monster, log, session, selected)
                self._append_combat_log_typed(
                    stdscr, monster, session, selected, log, f"You strike for {dmg} damage. {attack_note}".strip()
                )
            elif action == "Skill":
                if class_skills:
                    skill = random.choice(class_skills)
                    mp_cost = int(skill.get("mp_cost", 0))
                    is_mage = self.player.archetype == "Mage"
                    if is_mage and not self.player.spend_mp(mp_cost):
                        self._append_combat_log_typed(
                            stdscr,
                            monster,
                            session,
                            selected,
                            log,
                            f"Not enough MP for {skill['name']} ({mp_cost} MP).",
                        )
                    elif random.random() <= skill["accuracy"]:
                        dmg, attack_note = self._roll_player_damage(
                            self.player.strength,
                            monster.defense,
                            skill["bonus_damage"],
                        )
                        monster.hp -= dmg
                        self._monster_hit_flash_until = time.monotonic() + 0.28
                        self._animate_monster_hit_flash(stdscr, monster, log, session, selected)
                        self._append_combat_log_typed(
                            stdscr,
                            monster,
                            session,
                            selected,
                            log,
                            f"{skill['name']} hits for {dmg}. {attack_note}".strip(),
                        )
                    else:
                        self._append_combat_log_typed(
                            stdscr, monster, session, selected, log, f"{skill['name']} missed."
                        )
                else:
                    self._append_combat_log_typed(
                        stdscr, monster, session, selected, log, "No class skills available."
                    )
            elif action == "Item":
                if self.player.potions > 0:
                    self.player.potions -= 1
                    healed = self.player.heal(25)
                    self._append_combat_log_typed(
                        stdscr, monster, session, selected, log, f"Potion used. +{healed} HP."
                    )
                else:
                    self._append_combat_log_typed(
                        stdscr, monster, session, selected, log, "No potions left."
                    )
            elif action == "Run":
                if random.random() < 0.35:
                    self._toast(stdscr, "You escaped the battle.")
                    return True
                self._append_combat_log_typed(
                    stdscr, monster, session, selected, log, "Escape failed."
                )

            if monster.is_alive():
                retaliate, enemy_note = self._roll_enemy_damage(monster.strength, self.player.defense)
                self.player.hp -= retaliate
                self._append_combat_log_typed(
                    stdscr,
                    monster,
                    session,
                    selected,
                    log,
                    f"{monster.name} hits you for {retaliate}. {enemy_note}".strip(),
                )

        if self.player.is_alive():
            leveled = self.player.gain_xp(monster.xp_reward)
            self.player.gold += monster.gold_reward
            msg = f"Victory: +{monster.xp_reward} XP, +{monster.gold_reward} gold"
            if leveled:
                msg += " | LEVEL UP"
            self._toast(stdscr, msg)
            return True

        self._toast(stdscr, "You were defeated.")
        return False

    def _market_mode(self, stdscr: curses.window) -> None:
        assert self.player is not None
        index = 0
        while True:
            options = [
                f"{item['name']} ({item['price']}g) +{item['stock_amount']} potion(s)"
                for item in self.potions
            ]
            title = f"Market | Gold: {self.player.gold}"
            choice = self._menu_screen(
                stdscr,
                title,
                options + ["Back"],
                subtitle="Buy supplies before the next run.",
                selected=index,
                status=self._status_line(),
            )
            index = choice
            if choice == len(options):
                return

            potion = self.potions[choice]
            if self.player.gold < potion["price"]:
                self._toast(stdscr, "Not enough gold.")
                continue
            self.player.gold -= potion["price"]
            self.player.potions += potion["stock_amount"]
            self._toast(stdscr, f"Bought {potion['name']}.")

    def _training_mode(self, stdscr: curses.window) -> None:
        assert self.player is not None
        if self.player.archetype == "Mage":
            self._toast(
                stdscr,
                "Mage Training: move @ with W/A/S/D, avoid x/o, preserve Focus, Q to exit.",
            )
            result = start_meditation_training(stdscr, self.player)
            self.player.hp = max(1, self.player.hp - result.hp_cost)
            self.player.speed += result.speed_gain
            leveled = self.player.gain_xp(result.xp_gain)
            msg = result.summary
            if leveled:
                msg += " | LEVEL UP"
            self._toast(stdscr, msg)
            return
        if self.player.archetype == "Warrior":
            self._toast(
                stdscr,
                "Warrior Training: W(up) S(down) A(left) D(right) to parry incoming strikes.",
            )
            result = start_warrior_training(stdscr, self.player)
            self.player.hp = max(1, self.player.hp - result.hp_cost)
            self.player.strength += result.strength_gain
            self.player.defense += result.defense_gain
            leveled = self.player.gain_xp(result.xp_gain)
            msg = result.summary
            if leveled:
                msg += " | LEVEL UP"
            self._toast(stdscr, msg)
            return
        if self.player.archetype == "Archer":
            self._toast(
                stdscr,
                "Archer Training: W/S move, hold/release SPACE to shoot right, hit moving o targets.",
            )
            result = start_archer_training(stdscr, self.player)
            self.player.hp = max(1, self.player.hp - result.hp_cost)
            self.player.speed += result.speed_gain
            leveled = self.player.gain_xp(result.xp_gain)
            msg = result.summary
            if leveled:
                msg += " | LEVEL UP"
            self._toast(stdscr, msg)
            return

        hp_cost = random.randint(4, 10)
        xp_gain = random.randint(20, 40)
        speed_gain = 1 if random.random() < 0.3 else 0

        self.player.hp = max(1, self.player.hp - hp_cost)
        self.player.strength += 1
        self.player.defense += 1
        self.player.speed += speed_gain
        leveled = self.player.gain_xp(xp_gain)

        msg = f"Training: +1 STR +1 DEF +{xp_gain} XP -{hp_cost} HP"
        if speed_gain:
            msg += " +1 SPD"
        if leveled:
            msg += " | LEVEL UP"
        self._toast(stdscr, msg)

    def _status_mode(self, stdscr: curses.window) -> None:
        assert self.player is not None
        animated = False
        while True:
            self._draw_background(stdscr, 31)
            frame_y, frame_x, frame_h, frame_w = self._frame_rect(stdscr)
            self._draw_panel(stdscr, frame_y, frame_x, frame_h, frame_w, "CHARACTER STATUS")

            content_y = frame_y + 2
            content_h = frame_h - 8
            left_w = max(26, frame_w // 2)
            left_w = min(left_w, frame_w - 24)
            left_x = frame_x + 2
            right_x = left_x + left_w + 2
            right_w = max(20, frame_x + frame_w - 2 - right_x)

            self._draw_panel(stdscr, content_y, left_x, content_h, left_w, "STATS")
            self._draw_panel(stdscr, content_y, right_x, content_h, right_w, "PORTRAIT")

            lines = self.player.stats_block().split("\n")
            stats_start_y = content_y + 2
            for i, line in enumerate(lines, start=stats_start_y):
                if i >= content_y + content_h - 2:
                    break
                if not animated:
                    self._typewriter_draw(stdscr, i, left_x + 2, line[: left_w - 4], self._c(5) | curses.A_BOLD)
                else:
                    self._safe_addstr(stdscr, i, left_x + 2, line[: left_w - 4], self._c(5) | curses.A_BOLD)

            class_art = self._class_art_lines(self.player.archetype)
            art_start_y = content_y + 2
            for i, line in enumerate(class_art):
                y = art_start_y + i
                if y >= content_y + content_h - 2:
                    break
                centered_x = right_x + max(2, (right_w - len(line)) // 2)
                self._safe_addstr(stdscr, y, centered_x, line[: right_w - 4], self._c(2) | curses.A_BOLD)
            self._draw_dialog_box(
                stdscr,
                frame_y,
                frame_x,
                frame_h,
                frame_w,
                "Character status overview.",
                "Press Q, ESC, or Enter to return.",
            )
            stdscr.refresh()
            animated = True
            key = stdscr.getch()
            if key in (ord("q"), ord("Q"), 27, curses.KEY_ENTER, 10, 13):
                return

    def _choose_class(self, stdscr: curses.window) -> str:
        return self._choose_class_screen(stdscr)

    def _choose_class_screen(self, stdscr: curses.window) -> str:
        options = list(CLASS_TEMPLATES.keys())
        idx = 0
        header_animated = False

        while True:
            self._draw_background(stdscr, 11)
            frame_y, frame_x, frame_h, frame_w = self._frame_rect(stdscr)
            self._draw_panel(stdscr, frame_y, frame_x, frame_h, frame_w, "CHOOSE CLASS")
            self._draw_header_art(
                stdscr,
                frame_y,
                frame_x,
                "Choose Class",
                "Hover classes to preview their style.",
                animate=not header_animated,
            )
            header_animated = True

            content_y = frame_y + 8
            content_h = frame_h - 11
            left_w = max(24, frame_w // 3)
            left_w = min(left_w, frame_w - 28)
            left_x = frame_x + 2

            right_x = left_x + left_w + 2
            right_w = frame_x + frame_w - 2 - right_x
            right_w = max(20, right_w)

            self._draw_panel(stdscr, content_y, left_x, content_h, left_w, "CLASSES")
            self._draw_panel(stdscr, content_y, right_x, content_h, right_w, "PREVIEW")

            option_hitboxes: list[tuple[int, int, int]] = []
            start_y = content_y + 2
            for i, option in enumerate(options):
                row_y = start_y + i * 2
                if row_y >= content_y + content_h - 2:
                    break
                marker = "> " if i == idx else "  "
                attr = self._c(3) | curses.A_BOLD if i == idx else self._c(5)
                label = f"{marker}{option}"
                label_x = left_x + 2
                self._safe_addstr(stdscr, row_y, label_x, label[: left_w - 4], attr)
                option_hitboxes.append((row_y, label_x, label_x + min(len(label), left_w - 4)))

            art = self._class_art_lines(options[idx])
            art_start_y = content_y + 2
            for i, line in enumerate(art):
                y = art_start_y + i
                if y >= content_y + content_h - 3:
                    break
                centered_x = right_x + max(2, (right_w - len(line)) // 2)
                self._safe_addstr(stdscr, y, centered_x, line[: right_w - 4], self._c(2) | curses.A_BOLD)

            stats = CLASS_TEMPLATES[options[idx]]
            stats_line = (
                f"HP {stats['hp']}  MP {stats['mp']}  STR {stats['strength']}  "
                f"DEF {stats['defense']}  SPD {stats['speed']}"
            )
            self._safe_addstr(
                stdscr,
                content_y + content_h - 2,
                right_x + 2,
                stats_line[: right_w - 4],
                self._c(5),
            )

            self._safe_addstr(
                stdscr,
                frame_y + frame_h - 2,
                frame_x + 2,
                "W/S or arrows move | Hover to preview | Left click or Enter to select"[: frame_w - 4],
                self._c(1) | curses.A_BOLD,
            )
            stdscr.refresh()

            key = stdscr.getch()
            if key in (curses.KEY_UP, ord("w"), ord("W")):
                idx = (idx - 1) % len(options)
            elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
                idx = (idx + 1) % len(options)
            elif key in (10, 13, curses.KEY_ENTER):
                return options[idx]
            elif key == curses.KEY_MOUSE:
                try:
                    _, mx, my, _, state = curses.getmouse()
                except curses.error:
                    continue
                hovered = self._hit_test_option(my, mx, option_hitboxes)
                if hovered is not None:
                    idx = hovered
                    if state & curses.BUTTON1_CLICKED:
                        return options[idx]

    def _hit_test_option(
        self,
        mouse_y: int,
        mouse_x: int,
        hitboxes: list[tuple[int, int, int]],
    ) -> int | None:
        for i, (y, x1, x2) in enumerate(hitboxes):
            if mouse_y == y and x1 <= mouse_x <= x2:
                return i
        return None

    def _class_art_lines(self, class_name: str) -> list[str]:
        return CLASS_ART.get(
            class_name,
            [
                "             /\\                    ",
                "            /??\\                   ",
                "           /____\\                  ",
                "          | .--. |                 ",
                "       ___| |  | |___              ",
                "      /   / /||\\ \\   \\             ",
                "     /___/ / || \\ \\___\\            ",
                "         / /  ||  \\ \\              ",
                "        /_/___||___\\_\\             ",
                "           |  ||  |                ",
                "           |__||__|                ",
                "            _/  \\_                 ",
                "           /_/  \\_\\                ",
                "                                   ",
                "          unknown class            ",
                "                                   ",
            ],
        )

    def _input_name(self, stdscr: curses.window) -> str:
        name = ""
        while True:
            self._draw_background(stdscr, 19)
            frame_y, frame_x, frame_h, frame_w = self._frame_rect(stdscr)
            self._draw_panel(stdscr, frame_y, frame_x, frame_h, frame_w, "NAME YOUR CHARACTER")
            self._safe_addstr(
                stdscr,
                frame_y + 3,
                frame_x + 4,
                "Type name and press ENTER:",
                self._c(1) | curses.A_BOLD,
            )
            shown = name if name else "_"
            self._safe_addstr(stdscr, frame_y + 5, frame_x + 6, shown[: frame_w - 10], self._c(5) | curses.A_BOLD)
            self._safe_addstr(stdscr, frame_y + frame_h - 2, frame_x + 2, "Backspace to delete", self._c(2))
            stdscr.refresh()

            key = stdscr.getch()
            if key in (10, 13, curses.KEY_ENTER) and name.strip():
                return name.strip()
            if key in (curses.KEY_BACKSPACE, 127, 8):
                name = name[:-1]
                continue
            if 32 <= key <= 126 and len(name) < 20:
                name += chr(key)

    def _ask_play_again(self, stdscr: curses.window) -> bool:
        choice = self._menu_screen(
            stdscr,
            "Run Ended",
            ["Back to Start Menu", "Exit Game"],
            subtitle="Choose next action.",
        )
        return choice == 0

    def _menu_screen(
        self,
        stdscr: curses.window,
        title: str,
        options: list[str],
        subtitle: str = "",
        selected: int = 0,
        status: str = "",
        info_map: dict[str, str] | None = None,
        animate: bool = True,
        context_tag: str = "",
    ) -> int:
        idx = max(0, min(selected, len(options) - 1))
        header_animated = False
        stdscr.timeout(40 if animate else -1)
        try:
            while True:
                phase = int(time.monotonic() * 8)
                self._draw_background(stdscr, 7 + (phase % 5 if animate else 0))
                frame_y, frame_x, frame_h, frame_w = self._frame_rect(stdscr)
                self._draw_panel(stdscr, frame_y, frame_x, frame_h, frame_w)
                self._draw_header_art(stdscr, frame_y, frame_x, title, subtitle, animate=not header_animated)
                header_animated = True

                content_y = frame_y + 8
                content_h = frame_h - 15
                is_split = frame_w >= 70 and content_h >= 8

                if is_split:
                    left_w = max(22, min(34, frame_w // 3))
                    left_x = frame_x + 2
                    right_x = left_x + left_w + 2
                    right_w = max(20, frame_x + frame_w - 2 - right_x)

                    self._draw_panel(stdscr, content_y, left_x, content_h, left_w, "OPTIONS")
                    self._draw_panel(stdscr, content_y, right_x, content_h, right_w, "DETAILS")

                    start_y = content_y + 2
                    for i, option in enumerate(options):
                        y = start_y + i * 2
                        if y >= content_y + content_h - 2:
                            break
                        pulse_on = animate and i == idx and (phase % 2 == 0)
                        marker = ">" if i == idx else " "
                        attr = (self._c(1) | curses.A_BOLD) if pulse_on else (
                            self._c(3) | curses.A_BOLD if i == idx else self._c(5)
                        )
                        self._safe_addstr(stdscr, y, left_x + 2, f"{marker} {option}"[: left_w - 4], attr)
                        if i == idx and animate:
                            trail = ".:" if (phase % 3 == 0) else ":."
                            self._safe_addstr(stdscr, y, left_x + left_w - 4, trail, self._c(2))

                    selected_option = options[idx]
                    details = (
                        info_map.get(selected_option, self._menu_option_info(selected_option, context_tag))
                        if info_map
                        else self._menu_option_info(selected_option, context_tag)
                    )
                    self._safe_addstr(
                        stdscr,
                        content_y + 2,
                        right_x + 2,
                        f"Selected: {selected_option}"[: right_w - 4],
                        self._c(3) | curses.A_BOLD,
                    )
                    self._safe_addstr(
                        stdscr,
                        content_y + 4,
                        right_x + 2,
                        details[: right_w - 4],
                        self._c(5),
                    )
                    hint = self._menu_context_hint(selected_option, context_tag)
                    if hint:
                        self._safe_addstr(
                            stdscr,
                            content_y + 6,
                            right_x + 2,
                            hint[: right_w - 4],
                            self._c(2) | curses.A_BOLD,
                        )

                    if animate:
                        shimmer_y = content_y + content_h - 3
                        shimmer_w = max(0, right_w - 4)
                        shimmer = "".join(
                            ":" if ((phase + i) % 7 == 0) else ("." if ((phase + i) % 3 == 0) else " ")
                            for i in range(shimmer_w)
                        )
                        self._safe_addstr(stdscr, shimmer_y, right_x + 2, shimmer, self._c(1))
                else:
                    start_y = frame_y + 8
                    for i, option in enumerate(options):
                        y = start_y + i
                        if y >= frame_y + frame_h - 8:
                            break
                        pulse_on = animate and i == idx and (phase % 2 == 0)
                        marker = ">" if i == idx else " "
                        attr = (self._c(1) | curses.A_BOLD) if pulse_on else (
                            self._c(3) | curses.A_BOLD if i == idx else self._c(5)
                        )
                        self._safe_addstr(stdscr, y, frame_x + 4, f"{marker} {option}", attr)

                    selected_option = options[idx]
                    details = (
                        info_map.get(selected_option, self._menu_option_info(selected_option, context_tag))
                        if info_map
                        else self._menu_option_info(selected_option, context_tag)
                    )
                    self._safe_addstr(
                        stdscr,
                        frame_y + frame_h - 4,
                        frame_x + 2,
                        details[: frame_w - 4],
                        self._c(2),
                    )

                if status:
                    self._safe_addstr(
                        stdscr,
                        frame_y + frame_h - 8,
                        frame_x + 2,
                        status[: frame_w - 4],
                        self._c(2) | curses.A_BOLD,
                    )
                dialog_text = (
                    f"{selected_option}: {details}"
                    if 'selected_option' in locals()
                    else "Choose an option."
                )
                self._draw_dialog_box(
                    stdscr,
                    frame_y,
                    frame_x,
                    frame_h,
                    frame_w,
                    dialog_text,
                    "Arrow keys/W/S to move | Enter to confirm",
                )
                stdscr.refresh()

                key = stdscr.getch()
                if key in (curses.KEY_UP, ord("w"), ord("W")):
                    idx = (idx - 1) % len(options)
                elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
                    idx = (idx + 1) % len(options)
                elif key in (10, 13, curses.KEY_ENTER):
                    return idx
        finally:
            stdscr.timeout(-1)

    def _menu_option_info(self, option: str, context_tag: str = "") -> str:
        if context_tag == "main":
            info = {
                "Dungeon": "Risk combat, clear floors, and earn gold by reaching the door.",
                "Market": "Spend gold on potions to sustain longer dungeon runs.",
                "Training": "Class drills: Warrior reflex, Mage meditation, Archer conditioning.",
                "Status": "Review stats, progression, and your class portrait.",
                "Quit": "Leave this run and return to the start menu.",
            }
        else:
            info = {
                "Back to Start Menu": "Return to the title flow and begin a new character run.",
                "Exit Game": "Close the game session now.",
                "Back": "Return to the previous menu.",
            }
        return info.get(option, "No details available.")

    def _menu_context_hint(self, option: str, context_tag: str = "") -> str:
        if context_tag != "main" or self.player is None:
            return ""
        if option == "Market" and self.player.gold < 15:
            return "Tip: Clear a dungeon floor first to build buying power."
        if option == "Training" and self.player.archetype == "Mage":
            return "Tip: Longer focus survival improves meditation rewards."
        if option == "Status":
            return "Tip: Check XP progress before choosing your next move."
        if option == "Dungeon" and self.player.hp <= max(20, self.player.max_hp // 3):
            return "Tip: Low HP increases risk; consider Market or Training first."
        return ""

    def _draw_dungeon(self, stdscr: curses.window, session: DungeonSession) -> None:
        assert self.player is not None
        self._draw_background(stdscr, 43)
        frame_y, frame_x, frame_h, frame_w = self._frame_rect(stdscr)
        self._draw_panel(stdscr, frame_y, frame_x, frame_h, frame_w, "DUNGEON CRAWL")

        map_h = len(session.grid)
        map_w = len(session.grid[0])
        map_x = frame_x + max(2, (frame_w - map_w) // 2)
        map_y = frame_y + 2
        max_map_y = frame_y + frame_h - 9
        if map_y + map_h > max_map_y:
            map_y = max(frame_y + 2, max_map_y - map_h)

        self._draw_map(
            stdscr,
            session.grid,
            map_y,
            map_x,
            map_h,
            map_w,
            (session.player_x, session.player_y),
            (session.exit_x, session.exit_y),
            set(session.treasures.keys()),
            session.boss_pos,
            session.boss_defeated,
        )

        self._safe_addstr(
            stdscr,
            frame_y + 1,
            frame_x + 2,
            self._status_line()[: frame_w - 4],
            self._c(5) | curses.A_BOLD,
        )
        self._draw_dialog_box(
            stdscr,
            frame_y,
            frame_x,
            frame_h,
            frame_w,
            f"{session.message} | Treasures left: {len(session.treasures)}",
            "Move W/A/S/D or arrows | Q to leave dungeon.",
        )
        stdscr.refresh()

    def _draw_combat(
        self,
        stdscr: curses.window,
        monster: Monster,
        log: list[str],
        session: DungeonSession,
        selected: int,
    ) -> None:
        assert self.player is not None
        if monster.name.lower().startswith("boss "):
            self._draw_boss_combat(stdscr, monster, log, selected)
            return

        blink_phase = int(time.monotonic() * 18) % 2 == 0
        monster_flash = time.monotonic() < self._monster_hit_flash_until and blink_phase
        self._draw_background(stdscr, 59)
        frame_y, frame_x, frame_h, frame_w = self._frame_rect(stdscr)
        self._draw_panel(stdscr, frame_y, frame_x, frame_h, frame_w, "COMBAT")

        content_y = frame_y + 2
        content_h = frame_h - 9
        left_w = min(len(session.grid[0]) + 2, max(26, frame_w // 2))
        left_w = min(left_w, frame_w - 8)
        left_x = frame_x + 2

        center_w = min(36, frame_w - 6)
        center_x = frame_x + (frame_w - center_w) // 2
        min_center_x = left_x + left_w + 1
        if frame_w >= 90:
            center_x = max(center_x, min_center_x)
        if center_x + center_w > frame_x + frame_w - 2:
            center_x = frame_x + frame_w - 2 - center_w
        center_x = max(center_x, frame_x + 2)

        left_h = content_h
        center_h = content_h

        self._draw_panel(stdscr, content_y, left_x, left_h, left_w, "DUNGEON")
        self._draw_panel(stdscr, content_y, center_x, center_h, center_w, "BATTLE")

        map_y = content_y + 1
        map_x = left_x + 1
        map_h = max(4, left_h - 2)
        map_w = max(10, left_w - 2)
        self._draw_map(
            stdscr,
            session.grid,
            map_y,
            map_x,
            map_h,
            map_w,
            (session.player_x, session.player_y),
            (session.exit_x, session.exit_y),
            set(session.treasures.keys()),
            session.boss_pos,
            session.boss_defeated,
        )

        text_x = center_x + 2
        text_w = center_w - 4
        status_h = 5
        status_w = max(18, min(text_w, 28))
        self._draw_status_box(
            stdscr,
            content_y + 1,
            text_x,
            status_w,
            self.player.hp,
            self.player.max_hp,
            self.player.mp,
            self.player.max_mp,
            "STATUS",
        )
        monster_name_attr = self._c(4) | curses.A_BOLD if monster_flash else self._c(3) | curses.A_BOLD
        self._safe_addstr(
            stdscr,
            content_y + 1,
            text_x + status_w + 1,
            monster.name[: max(0, text_w - status_w - 1)],
            monster_name_attr,
        )
        self._safe_addstr(
            stdscr,
            content_y + 2,
            text_x + status_w + 1,
            f"Enemy HP {max(0, monster.hp)}"[: max(0, text_w - status_w - 1)],
            self._c(4) | curses.A_BOLD,
        )

        info_h = 5
        info_y = content_y + status_h + 1
        if info_y + info_h < content_y + center_h - 10:
            self._draw_panel(stdscr, info_y, text_x, info_h, text_w, "INFO")
            self._safe_addstr(
                stdscr,
                info_y + 1,
                text_x + 2,
                "Player ATK: Precise rhythm | Crit chance 15%"[: text_w - 4],
                self._c(5),
            )
            self._safe_addstr(
                stdscr,
                info_y + 2,
                text_x + 2,
                f"{monster.name} ATK: Brutal swings | High variance"[: text_w - 4],
                self._c(7),
            )
        else:
            info_h = 0

        art_lines = self._enemy_art_lines(monster.name)
        art_start_y = content_y + 2 + status_h + (info_h + 1 if info_h else 0)
        for i, line in enumerate(art_lines):
            y = art_start_y + i
            if y >= content_y + center_h - 10:
                break
            centered_x = text_x + max(0, (text_w - len(line)) // 2)
            art_attr = self._c(4) | curses.A_BOLD if monster_flash else self._c(2) | curses.A_BOLD
            self._safe_addstr(stdscr, y, centered_x, line[:text_w], art_attr)

        option_top = art_start_y + len(art_lines) + 1
        option_top = min(option_top, content_y + center_h - 9)
        for idx, label in enumerate(COMBAT_OPTIONS):
            ox = text_x + (idx % 2) * (text_w // 2)
            oy = option_top + (idx // 2) * 2
            marker = "> " if idx == selected else "  "
            attr = self._c(3) | curses.A_BOLD if idx == selected else self._c(5)
            self._safe_addstr(stdscr, oy, ox, f"{marker}{label}", attr)

        self._safe_addstr(
            stdscr,
            option_top + 4,
            text_x,
            f"Potions: {self.player.potions}  MP: {self.player.mp}/{self.player.max_mp}",
            self._c(5),
        )

        log_y = option_top + 5
        for line in log[-5:]:
            if log_y >= content_y + center_h - 1:
                break
            self._safe_addstr(stdscr, log_y, text_x, line[:text_w], self._c(2))
            log_y += 1

        latest = log[-1] if log else "Choose your action."
        self._draw_dialog_box(
            stdscr,
            frame_y,
            frame_x,
            frame_h,
            frame_w,
            latest,
            "W/A/S/D or arrows move | Enter confirm",
        )
        stdscr.refresh()

    def _draw_boss_combat(
        self,
        stdscr: curses.window,
        monster: Monster,
        log: list[str],
        selected: int,
    ) -> None:
        assert self.player is not None
        blink_phase = int(time.monotonic() * 18) % 2 == 0
        monster_flash = time.monotonic() < self._monster_hit_flash_until and blink_phase
        self._draw_background(stdscr, 77)
        frame_y, frame_x, frame_h, frame_w = self._frame_rect(stdscr)
        self._draw_panel(stdscr, frame_y, frame_x, frame_h, frame_w, "BOSS ENCOUNTER")

        battle_h = max(10, min(24, frame_h - 9))
        battle_w = max(28, min(80, frame_w - 6))
        battle_y = frame_y + 2 + max(0, (frame_h - 9 - battle_h) // 2)
        battle_x = frame_x + max(2, (frame_w - battle_w) // 2)
        self._draw_panel(stdscr, battle_y, battle_x, battle_h, battle_w, "FINAL BATTLE")

        top_y = battle_y + 1
        text_x = battle_x + 2
        text_w = battle_w - 4
        self._safe_addstr(
            stdscr,
            top_y,
            text_x,
            f"{self.player.name}  LV {self.player.level}  HP {self.player.hp}/{self.player.max_hp}  MP {self.player.mp}/{self.player.max_mp}"[
                :text_w
            ],
            self._c(5) | curses.A_BOLD,
        )
        self._safe_addstr(
            stdscr,
            top_y + 1,
            text_x,
            f"* {monster.name}  HP {max(0, monster.hp)}"[:text_w],
            (self._c(4) | curses.A_BOLD) if monster_flash else (self._c(3) | curses.A_BOLD),
        )

        art_lines = self._enemy_art_lines(monster.name)
        art_y = top_y + 3
        for i, line in enumerate(art_lines):
            y = art_y + i
            if y >= battle_y + battle_h - 10:
                break
            centered_x = battle_x + max(2, (battle_w - len(line)) // 2)
            art_attr = self._c(4) | curses.A_BOLD if monster_flash else self._c(2) | curses.A_BOLD
            self._safe_addstr(stdscr, y, centered_x, line[: battle_w - 4], art_attr)

        arena_h = min(7, max(5, battle_h - 7))
        arena_w = max(18, min(46, battle_w - 8))
        arena_x = battle_x + (battle_w - arena_w) // 2
        arena_y = min(battle_y + battle_h - 12, art_y + len(art_lines) + 1)
        arena_y = max(arena_y, top_y + 5)
        self._draw_panel(stdscr, arena_y, arena_x, arena_h, arena_w, "ARENA")

        # Undertale-inspired soul indicator drifting inside the battle box.
        inner_w = max(1, arena_w - 2)
        inner_h = max(1, arena_h - 2)
        t = time.monotonic()
        soul_x = arena_x + 1 + int((inner_w - 1) * (0.5 + 0.45 * math.sin(t * 2.1)))
        soul_y = arena_y + 1 + int((inner_h - 1) * (0.5 + 0.45 * math.cos(t * 2.6)))
        soul_glyph = "♥" if self._unicode_ui else "*"
        self._safe_addstr(stdscr, soul_y, soul_x, soul_glyph, self._c(4) | curses.A_BOLD)

        action_y = battle_y + battle_h - 4
        action_labels = ["FIGHT", "SKILL", "ITEM", "MERCY"]
        slot_w = max(6, (battle_w - 4) // 4)
        for idx, label in enumerate(action_labels):
            ox = battle_x + 2 + idx * slot_w
            marker = ">" if idx == selected else " "
            text = f"{marker}{label}"
            attr = self._c(3) | curses.A_BOLD if idx == selected else self._c(5)
            self._safe_addstr(stdscr, action_y, ox, text[: max(0, slot_w - 1)], attr)

        log_y = action_y - 2
        for line in log[-2:]:
            self._safe_addstr(stdscr, log_y, text_x, line[:text_w], self._c(2))
            log_y += 1

        latest = log[-1] if log else "Stay determined."
        self._draw_dialog_box(
            stdscr,
            frame_y,
            frame_x,
            frame_h,
            frame_w,
            latest,
            "W/A/S/D or arrows move | Enter confirm",
        )
        stdscr.refresh()

    def _draw_header_art(
        self,
        stdscr: curses.window,
        frame_y: int,
        frame_x: int,
        title: str,
        subtitle: str,
        animate: bool = False,
    ) -> None:
        self._safe_addstr(
            stdscr,
            frame_y + 1,
            frame_x + 2,
            " /\\^ /\\^  /$\\  /\\^ .: .: .:  /\\^ /\\^ ",
            self._c(2) | curses.A_BOLD,
        )
        self._safe_addstr(
            stdscr,
            frame_y + 2,
            frame_x + 2,
            " :: .:. ::  ::  ::  ::  ::  ::   :: .:. :: ",
            self._c(1) | curses.A_BOLD,
        )
        if animate:
            self._typewriter_draw(stdscr, frame_y + 3, frame_x + 2, f"== {title} ==", self._c(3) | curses.A_BOLD)
        else:
            self._safe_addstr(stdscr, frame_y + 3, frame_x + 2, f"== {title} ==", self._c(3) | curses.A_BOLD)
        if subtitle:
            if animate:
                self._typewriter_draw(stdscr, frame_y + 4, frame_x + 4, subtitle, self._c(5))
            else:
                self._safe_addstr(stdscr, frame_y + 4, frame_x + 4, subtitle, self._c(5))
        for i, line in enumerate(self.opening_lines[:2], start=frame_y + 5):
            if animate:
                self._typewriter_draw(stdscr, i, frame_x + 4, line, self._c(6))
            else:
                self._safe_addstr(stdscr, i, frame_x + 4, line, self._c(6))

    def _draw_background(self, stdscr: curses.window, phase: int) -> None:
        stdscr.erase()
        max_y, max_x = stdscr.getmaxyx()
        glyphs = ".:."
        border_attr = self._c(1)
        for x in range(max_x):
            top = glyphs[(x * 5 + phase + self._bg_seed) % len(glyphs)]
            bot = glyphs[(x * 7 + phase + self._bg_seed) % len(glyphs)]
            self._safe_addstr(stdscr, 0, x, top, border_attr)
            self._safe_addstr(stdscr, max_y - 1, x, bot, border_attr)
        for y in range(max_y):
            left = glyphs[(y * 3 + phase + self._bg_seed) % len(glyphs)]
            right = glyphs[(y * 11 + phase + self._bg_seed) % len(glyphs)]
            self._safe_addstr(stdscr, y, 0, left, border_attr)
            self._safe_addstr(stdscr, y, max_x - 1, right, border_attr)

        for y in range(max_y):
            for x in range(max_x):
                if x in (0, max_x - 1) or y in (0, max_y - 1):
                    continue
                if ((x * 19 + y * 23 + phase + self._bg_seed) % 113) != 0:
                    continue
                ch = glyphs[(x + y + phase) % len(glyphs)]
                color = self._c(7) | curses.A_DIM
                self._safe_addstr(stdscr, y, x, ch, color)

    def _draw_panel(self, stdscr: curses.window, y: int, x: int, h: int, w: int, title: str = "") -> None:
        max_y, max_x = stdscr.getmaxyx()
        if h < 3 or w < 4:
            return
        y2 = min(max_y - 1, y + h - 1)
        x2 = min(max_x - 1, x + w - 1)

        for yy in range(y + 1, y2):
            for xx in range(x + 1, x2):
                self._safe_addstr(stdscr, yy, xx, " ", self._ui_fill())

        hline = self._g("h") * max(0, x2 - x - 1)
        self._safe_addstr(stdscr, y, x + 1, hline, self._c(1))
        self._safe_addstr(stdscr, y2, x + 1, hline, self._c(1))
        for yy in range(y + 1, y2):
            self._safe_addstr(stdscr, yy, x, self._g("v"), self._c(1))
            self._safe_addstr(stdscr, yy, x2, self._g("v"), self._c(1))
        self._safe_addstr(stdscr, y, x, self._g("tl"), self._c(3))
        self._safe_addstr(stdscr, y, x2, self._g("tr"), self._c(3))
        self._safe_addstr(stdscr, y2, x, self._g("bl"), self._c(3))
        self._safe_addstr(stdscr, y2, x2, self._g("br"), self._c(3))

        if title:
            title_text = f" {title} "
            self._safe_addstr(stdscr, y, x + 2, title_text[: max(0, x2 - x - 3)], self._c(3) | curses.A_BOLD)

    def _draw_dialog_box(
        self,
        stdscr: curses.window,
        frame_y: int,
        frame_x: int,
        frame_h: int,
        frame_w: int,
        text: str,
        hint: str = "",
    ) -> None:
        box_h = 4
        box_w = max(24, frame_w - 4)
        box_x = frame_x + 2
        box_y = frame_y + frame_h - box_h - 2
        self._draw_panel(stdscr, box_y, box_x, box_h, box_w, "MESSAGE")
        self._safe_addstr(
            stdscr,
            box_y + 1,
            box_x + 2,
            text[: box_w - 4],
            self._ui_text(),
        )
        if hint:
            self._safe_addstr(
                stdscr,
                box_y + 2,
                box_x + 2,
                hint[: box_w - 4],
                self._ui_muted(),
            )

    def _draw_map(
        self,
        stdscr: curses.window,
        grid: list[list[int]],
        draw_y: int,
        draw_x: int,
        max_h: int,
        max_w: int,
        player_pos: tuple[int, int],
        exit_pos: tuple[int, int],
        treasure_positions: set[tuple[int, int]] | None = None,
        boss_pos: tuple[int, int] | None = None,
        boss_defeated: bool = True,
    ) -> None:
        player_x, player_y = player_pos
        exit_x, exit_y = exit_pos
        treasure_positions = treasure_positions or set()
        for y in range(min(max_h, len(grid))):
            for x in range(min(max_w, len(grid[0]))):
                tile = grid[y][x]
                ch = self._tile_char(grid, x, y, tile)
                if tile == TILE_FLOOR:
                    color = self._c(5) | curses.A_DIM
                elif tile == TILE_DOOR:
                    color = self._c(3) | curses.A_BOLD
                else:
                    color = self._c(1) | curses.A_BOLD
                if (x, y) in treasure_positions:
                    ch = "T" if not self._unicode_ui else "✦"
                    color = self._c(3) | curses.A_BOLD
                if (x, y) == boss_pos and not boss_defeated:
                    ch = "B"
                    color = self._c(4) | curses.A_BOLD
                if (x, y) == (exit_x, exit_y):
                    ch = "D"
                    color = self._c(3) | curses.A_BOLD
                if (x, y) == (player_x, player_y):
                    ch = "@"
                    color = self._c(4) | curses.A_BOLD
                self._safe_addstr(stdscr, draw_y + y, draw_x + x, ch, color)

    def _frame_rect(self, stdscr: curses.window) -> tuple[int, int, int, int]:
        max_y, max_x = stdscr.getmaxyx()
        frame_w = min(120, max_x - 4)
        frame_h = min(40, max_y - 2)
        frame_w = max(40, frame_w)
        frame_h = max(18, frame_h)
        frame_x = max(0, (max_x - frame_w) // 2)
        frame_y = max(0, (max_y - frame_h) // 2)
        return frame_y, frame_x, frame_h, frame_w

    def _move_combat_selection(self, selected: int, key: int) -> tuple[bool, int]:
        row = selected // 2
        col = selected % 2
        if key in (ord("w"), ord("W"), curses.KEY_UP):
            row = max(0, row - 1)
            return True, row * 2 + col
        if key in (ord("s"), ord("S"), curses.KEY_DOWN):
            row = min(1, row + 1)
            return True, row * 2 + col
        if key in (ord("a"), ord("A"), curses.KEY_LEFT):
            col = max(0, col - 1)
            return True, row * 2 + col
        if key in (ord("d"), ord("D"), curses.KEY_RIGHT):
            col = min(1, col + 1)
            return True, row * 2 + col
        return False, selected

    def _enemy_art_lines(self, monster_name: str) -> list[str]:
        name = monster_name.lower()
        if "slime" in name:
            return ENEMY_ART["slime"]
        if "goblin" in name:
            return ENEMY_ART["goblin"]
        if "bone" in name or "skeleton" in name:
            return ENEMY_ART["bone"]
        return [
            "    .-\"\"\"\"-.   ",
            "   / 0  0  \\  ",
            "  |   __   |  ",
            "   \\______ /  ",
        ]

    def _status_line(self) -> str:
        assert self.player is not None
        return (
            f"{self.player.name} [{self.player.archetype}] "
            f"Lv{self.player.level} HP {self.player.hp}/{self.player.max_hp} "
            f"MP {self.player.mp}/{self.player.max_mp} "
            f"Gold {self.player.gold} Potions {self.player.potions} "
            f"Dungeon {self.dungeon_level}"
        )

    def _tile_char(self, grid: list[list[int]], x: int, y: int, tile: int) -> str:
        if tile == TILE_DOOR:
            return "D"
        if tile == TILE_FLOOR:
            if not self._unicode_ui:
                return "." if ((x * 5 + y * 3 + self._bg_seed) % 9) else ","
            if ((x * 7 + y * 11 + self._bg_seed) % 31) == 0:
                return "✧"
            if ((x * 3 + y * 5 + self._bg_seed) % 17) == 0:
                return "⋅"
            return "·"
        if not self._unicode_ui:
            return "#"
        return self._wall_glyph(grid, x, y)

    def _wall_glyph(self, grid: list[list[int]], x: int, y: int) -> str:
        h = len(grid)
        w = len(grid[0]) if h else 0

        def is_wall(nx: int, ny: int) -> bool:
            if nx < 0 or ny < 0 or nx >= w or ny >= h:
                return True
            return grid[ny][nx] != TILE_FLOOR

        n = is_wall(x, y - 1)
        s = is_wall(x, y + 1)
        e = is_wall(x + 1, y)
        wv = is_wall(x - 1, y)

        if n and s and e and wv:
            return "█"
        if n and s and not e and not wv:
            return "│"
        if not n and not s and e and wv:
            return "─"
        if n and e and not s and not wv:
            return "└"
        if n and wv and not s and not e:
            return "┘"
        if s and e and not n and not wv:
            return "┌"
        if s and wv and not n and not e:
            return "┐"
        if n and s and e and not wv:
            return "├"
        if n and s and wv and not e:
            return "┤"
        if n and e and wv and not s:
            return "┴"
        if s and e and wv and not n:
            return "┬"
        return "▓"

    def _is_walkable_tile(self, tile: int) -> bool:
        return tile in (TILE_FLOOR, TILE_DOOR)

    def _delta_from_key(self, key: int) -> tuple[int, int]:
        if key in (ord("w"), ord("W"), curses.KEY_UP):
            return 0, -1
        if key in (ord("s"), ord("S"), curses.KEY_DOWN):
            return 0, 1
        if key in (ord("a"), ord("A"), curses.KEY_LEFT):
            return -1, 0
        if key in (ord("d"), ord("D"), curses.KEY_RIGHT):
            return 1, 0
        return 0, 0

    def _roll_damage(self, attacker_strength: int, defender_defense: int, bonus: int = 0) -> int:
        variance = random.randint(-2, 3)
        raw = attacker_strength + bonus + variance
        mitigation = defender_defense // 2
        return max(1, raw - mitigation)

    def _roll_player_damage(
        self,
        attacker_strength: int,
        defender_defense: int,
        bonus: int = 0,
    ) -> tuple[int, str]:
        crit = random.random() < 0.15
        variance = random.randint(-1, 4)
        raw = attacker_strength + bonus + variance + (4 if crit else 0)
        mitigation = defender_defense // 2
        damage = max(1, raw - mitigation)
        return damage, ("Critical strike!" if crit else "")

    def _roll_enemy_damage(
        self,
        attacker_strength: int,
        defender_defense: int,
    ) -> tuple[int, str]:
        wild = random.randint(-4, 6)
        raw = attacker_strength + wild
        mitigation = defender_defense // 3
        damage = max(1, raw - mitigation)
        if wild >= 5:
            return damage, "Heavy blow!"
        if wild <= -3:
            return damage, "Glancing hit."
        return damage, ""

    def _draw_status_box(
        self,
        stdscr: curses.window,
        y: int,
        x: int,
        width: int,
        hp: int,
        max_hp: int,
        mp: int,
        max_mp: int,
        title: str,
    ) -> None:
        if width < 18:
            return
        inner = max(6, width - 4)
        head = f" {title} "
        h = self._g("h")
        top_fill = max(0, width - 2 - len(head))
        self._safe_addstr(stdscr, y, x, self._g("tl") + head + (h * top_fill) + self._g("tr"), self._c(1))

        bar_w = max(6, min(12, inner - 7))
        hp_bar = self._bar_blocks(hp, max_hp, bar_w)
        mp_bar = self._bar_blocks(mp, max_mp, bar_w)
        hp_attr = self._hp_bar_attr(hp, max_hp)
        mp_attr = self._c(11) | curses.A_BOLD
        hp_row = f"HP {hp_bar} {max(0, hp):>3}/{max(1, max_hp):<3}"
        mp_row = f"MP {mp_bar} {max(0, mp):>3}/{max(1, max_mp):<3}"
        self._safe_addstr(stdscr, y + 1, x, self._g("v"), self._c(1))
        self._safe_addstr(stdscr, y + 1, x + 1, hp_row[: width - 2].ljust(width - 2), hp_attr)
        self._safe_addstr(stdscr, y + 1, x + width - 1, self._g("v"), self._c(1))

        self._safe_addstr(stdscr, y + 2, x, self._g("v"), self._c(1))
        self._safe_addstr(stdscr, y + 2, x + 1, mp_row[: width - 2].ljust(width - 2), mp_attr)
        self._safe_addstr(stdscr, y + 2, x + width - 1, self._g("v"), self._c(1))

        self._safe_addstr(stdscr, y + 3, x, self._g("bl") + (h * (width - 2)) + self._g("br"), self._c(1))

    def _hp_bar_attr(self, hp: int, max_hp: int) -> int:
        if max_hp <= 0:
            return self._c(10) | curses.A_BOLD
        ratio = hp / max_hp
        if ratio > 0.60:
            return self._c(8) | curses.A_BOLD
        if ratio > 0.30:
            return self._c(9) | curses.A_BOLD
        return self._c(10) | curses.A_BOLD

    def _bar_blocks(self, value: int, max_value: int, width: int) -> str:
        full = self._g("full")
        empty = self._g("empty")
        if max_value <= 0:
            return empty * width
        ratio = max(0.0, min(1.0, value / max_value))
        filled = int(round(width * ratio))
        filled = max(0, min(width, filled))
        return (full * filled) + (empty * (width - filled))

    def _g(self, name: str) -> str:
        ascii_set = {
            "tl": "+",
            "tr": "+",
            "bl": "+",
            "br": "+",
            "h": "-",
            "v": "|",
            "full": "#",
            "empty": ".",
        }
        unicode_set = {
            "tl": "┌",
            "tr": "┐",
            "bl": "└",
            "br": "┘",
            "h": "─",
            "v": "│",
            "full": "█",
            "empty": "░",
        }
        if not self._unicode_ui:
            return ascii_set.get(name, "?")
        return unicode_set.get(name, ascii_set.get(name, "?"))

    def _append_combat_log_typed(
        self,
        stdscr: curses.window,
        monster: Monster,
        session: DungeonSession,
        selected: int,
        log: list[str],
        message: str,
    ) -> None:
        log.append(message)
        if len(log) > 8:
            del log[:-8]
        self._draw_combat(stdscr, monster, log, session, selected)
        text_x, text_w, log_y = self._combat_log_coords(stdscr, monster, session)
        visible = log[-5:]
        y = log_y + max(0, len(visible) - 1)
        self._typewriter_draw(stdscr, y, text_x, visible[-1][:text_w], self._c(2))

    def _animate_monster_hit_flash(
        self,
        stdscr: curses.window,
        monster: Monster,
        log: list[str],
        session: DungeonSession,
        selected: int,
        duration: float = 0.24,
    ) -> None:
        end = time.monotonic() + max(0.08, duration)
        while time.monotonic() < end:
            self._draw_combat(stdscr, monster, log, session, selected)
            time.sleep(0.04)

    def _combat_log_coords(
        self,
        stdscr: curses.window,
        monster: Monster,
        session: DungeonSession,
    ) -> tuple[int, int, int]:
        if monster.name.lower().startswith("boss "):
            frame_y, frame_x, frame_h, frame_w = self._frame_rect(stdscr)
            battle_h = max(10, min(24, frame_h - 9))
            battle_w = max(28, min(80, frame_w - 6))
            battle_y = frame_y + 2 + max(0, (frame_h - 9 - battle_h) // 2)
            battle_x = frame_x + max(2, (frame_w - battle_w) // 2)
            text_x = battle_x + 2
            text_w = battle_w - 4
            action_y = battle_y + battle_h - 4
            log_y = action_y - 2
            return text_x, text_w, log_y

        frame_y, frame_x, frame_h, frame_w = self._frame_rect(stdscr)
        content_y = frame_y + 2
        content_h = frame_h - 9
        left_w = min(len(session.grid[0]) + 2, max(26, frame_w // 2))
        left_w = min(left_w, frame_w - 8)
        left_x = frame_x + 2

        center_w = min(36, frame_w - 6)
        center_x = frame_x + (frame_w - center_w) // 2
        min_center_x = left_x + left_w + 1
        if frame_w >= 90:
            center_x = max(center_x, min_center_x)
        if center_x + center_w > frame_x + frame_w - 2:
            center_x = frame_x + frame_w - 2 - center_w
        center_x = max(center_x, frame_x + 2)

        text_x = center_x + 2
        text_w = center_w - 4
        status_h = 5
        info_h = 5
        art_lines = self._enemy_art_lines(monster.name)
        option_top = content_y + 2 + status_h + info_h + 1 + len(art_lines) + 1
        option_top = min(option_top, content_y + content_h - 9)
        log_y = option_top + 5
        return text_x, text_w, log_y

    def _toast(self, stdscr: curses.window, message: str) -> None:
        self._draw_background(stdscr, 73)
        frame_y, frame_x, frame_h, frame_w = self._frame_rect(stdscr)
        self._draw_panel(stdscr, frame_y, frame_x, frame_h, frame_w, "EVENT")
        card_w = max(30, min(frame_w - 8, 72))
        card_h = 7
        card_x = frame_x + (frame_w - card_w) // 2
        card_y = frame_y + (frame_h - card_h) // 2
        self._draw_panel(stdscr, card_y, card_x, card_h, card_w, "EVENT")
        self._typewriter_draw(
            stdscr,
            card_y + 2,
            card_x + 2,
            message[: card_w - 4],
            self._c(5) | curses.A_BOLD,
        )
        self._typewriter_draw(
            stdscr,
            card_y + 4,
            card_x + 2,
            "Press any key to continue."[: card_w - 4],
            self._c(3) | curses.A_BOLD,
        )
        stdscr.refresh()
        stdscr.getch()

    def _typewriter_draw(
        self,
        stdscr: curses.window,
        y: int,
        x: int,
        text: str,
        attr: int = 0,
    ) -> None:
        if not text:
            return
        if not self._typing_enabled:
            self._safe_addstr(stdscr, y, x, text, attr)
            stdscr.refresh()
            return
        if time.monotonic() < self._typing_skip_until:
            self._safe_addstr(stdscr, y, x, text, attr)
            stdscr.refresh()
            return

        stdscr.nodelay(True)
        try:
            rendered = ""
            for ch in text:
                if self._is_skip_pressed(stdscr):
                    self._typing_skip_until = time.monotonic() + 0.6
                    self._safe_addstr(stdscr, y, x, text, attr)
                    stdscr.refresh()
                    return

                rendered += ch
                self._safe_addstr(stdscr, y, x, rendered, attr)
                stdscr.refresh()

                sleep_steps = max(1, int(self._typing_delay / 0.005))
                for _ in range(sleep_steps):
                    if self._is_skip_pressed(stdscr):
                        self._typing_skip_until = time.monotonic() + 0.6
                        self._safe_addstr(stdscr, y, x, text, attr)
                        stdscr.refresh()
                        return
                    time.sleep(0.005)
        finally:
            stdscr.nodelay(False)

    def _is_skip_pressed(self, stdscr: curses.window) -> bool:
        while True:
            key = stdscr.getch()
            if key == -1:
                return False
            if key in (10, 13, curses.KEY_ENTER):
                return True

    def _safe_addstr(self, stdscr: curses.window, y: int, x: int, text: str, attr: int = 0) -> None:
        max_y, max_x = stdscr.getmaxyx()
        if y < 0 or y >= max_y or x >= max_x:
            return
        if x < 0:
            text = text[-x:]
            x = 0
        if not text:
            return
        clipped = text[: max_x - x]
        if not clipped:
            return
        try:
            stdscr.addstr(y, x, clipped, attr)
        except curses.error:
            pass

    def _c(self, pair_id: int) -> int:
        if not curses.has_colors():
            return 0
        return curses.color_pair(pair_id)

    def _ui_text(self) -> int:
        return self._c(5) | curses.A_BOLD

    def _ui_muted(self) -> int:
        return self._c(7) | curses.A_DIM

    def _ui_fill(self) -> int:
        return self._c(7) | curses.A_DIM
