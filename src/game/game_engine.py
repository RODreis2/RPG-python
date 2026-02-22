import curses
import random
import time
from dataclasses import dataclass

from .data_loader import load_monsters, load_opening_lines, load_potions, load_skills
from .models import Monster, Player
from .systems.map_generator import DungeonMap, TILE_DOOR, TILE_FLOOR


CLASS_TEMPLATES = {
    "Warrior": {"hp": 120, "strength": 16, "defense": 12, "speed": 8},
    "Mage": {"hp": 85, "strength": 18, "defense": 7, "speed": 10},
    "Archer": {"hp": 95, "strength": 14, "defense": 9, "speed": 14},
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
        curses.init_pair(1, curses.COLOR_CYAN, -1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        curses.init_pair(4, curses.COLOR_RED, -1)
        curses.init_pair(5, curses.COLOR_WHITE, -1)
        curses.init_pair(6, curses.COLOR_MAGENTA, -1)

    def _main_menu_loop(self, stdscr: curses.window) -> None:
        assert self.player is not None
        while self.player.is_alive():
            option = self._menu_screen(
                stdscr,
                f"{self.player.name} the {self.player.archetype}",
                ["Dungeon", "Market", "Training", "Status", "Quit"],
                subtitle="Wander, grow, survive.",
                status=self._status_line(),
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

        session = DungeonSession(grid, player_x, player_y, exit_x, exit_y)
        session.grid[exit_y][exit_x] = TILE_DOOR
        session.message = f"Dungeon Level {self.dungeon_level}"

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
            if (nx, ny) == (session.exit_x, session.exit_y):
                bonus = random.randint(10, 22)
                self.player.gold += bonus
                self.dungeon_level += 1
                self._toast(stdscr, f"Door reached. +{bonus} gold. Dungeon level {self.dungeon_level}.")
                return

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

    def _combat_mode(self, stdscr: curses.window, monster: Monster, session: DungeonSession) -> bool:
        assert self.player is not None
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
                dmg = self._roll_damage(self.player.strength, monster.defense)
                monster.hp -= dmg
                self._append_combat_log_typed(
                    stdscr, monster, session, selected, log, f"You strike for {dmg} damage."
                )
            elif action == "Skill":
                if class_skills:
                    skill = random.choice(class_skills)
                    if random.random() <= skill["accuracy"]:
                        dmg = self._roll_damage(
                            self.player.strength,
                            monster.defense,
                            skill["bonus_damage"],
                        )
                        monster.hp -= dmg
                        self._append_combat_log_typed(
                            stdscr, monster, session, selected, log, f"{skill['name']} hits for {dmg}."
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
                retaliate = self._roll_damage(monster.strength, self.player.defense)
                self.player.hp -= retaliate
                self._append_combat_log_typed(
                    stdscr, monster, session, selected, log, f"{monster.name} hits you for {retaliate}."
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
            content_h = frame_h - 4
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

            self._safe_addstr(
                stdscr,
                frame_y + frame_h - 2,
                frame_x + 2,
                "Press Q or ESC to return",
                self._c(1) | curses.A_BOLD,
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
                f"HP {stats['hp']}  STR {stats['strength']}  "
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
    ) -> int:
        idx = max(0, min(selected, len(options) - 1))
        header_animated = False
        while True:
            self._draw_background(stdscr, 7)
            frame_y, frame_x, frame_h, frame_w = self._frame_rect(stdscr)
            self._draw_panel(stdscr, frame_y, frame_x, frame_h, frame_w)
            self._draw_header_art(stdscr, frame_y, frame_x, title, subtitle, animate=not header_animated)
            header_animated = True

            start_y = frame_y + 8
            for i, option in enumerate(options):
                y = start_y + i
                if y >= frame_y + frame_h - 3:
                    break
                marker = ">" if i == idx else " "
                attr = self._c(3) | curses.A_BOLD if i == idx else self._c(5)
                self._safe_addstr(stdscr, y, frame_x + 4, f"{marker} {option}", attr)

            if status:
                self._safe_addstr(
                    stdscr,
                    frame_y + frame_h - 3,
                    frame_x + 2,
                    status[: frame_w - 4],
                    self._c(2) | curses.A_BOLD,
                )
            self._safe_addstr(
                stdscr,
                frame_y + frame_h - 2,
                frame_x + 2,
                "Arrow keys/W-S + Enter",
                self._c(1) | curses.A_BOLD,
            )
            stdscr.refresh()

            key = stdscr.getch()
            if key in (curses.KEY_UP, ord("w"), ord("W")):
                idx = (idx - 1) % len(options)
            elif key in (curses.KEY_DOWN, ord("s"), ord("S")):
                idx = (idx + 1) % len(options)
            elif key in (10, 13, curses.KEY_ENTER):
                return idx

    def _draw_dungeon(self, stdscr: curses.window, session: DungeonSession) -> None:
        assert self.player is not None
        self._draw_background(stdscr, 43)
        frame_y, frame_x, frame_h, frame_w = self._frame_rect(stdscr)
        self._draw_panel(stdscr, frame_y, frame_x, frame_h, frame_w, "DUNGEON CRAWL")

        map_h = len(session.grid)
        map_w = len(session.grid[0])
        map_x = frame_x + max(2, (frame_w - map_w) // 2)
        map_y = frame_y + 2
        max_map_y = frame_y + frame_h - 5
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
        )

        self._safe_addstr(
            stdscr,
            frame_y + frame_h - 3,
            frame_x + 2,
            self._status_line()[: frame_w - 4],
            self._c(5) | curses.A_BOLD,
        )
        self._safe_addstr(
            stdscr,
            frame_y + frame_h - 2,
            frame_x + 2,
            f"{session.message} | Move: W/A/S/D or arrows | Q leave"[: frame_w - 4],
            self._c(1),
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
        self._draw_background(stdscr, 59)
        frame_y, frame_x, frame_h, frame_w = self._frame_rect(stdscr)
        self._draw_panel(stdscr, frame_y, frame_x, frame_h, frame_w, "COMBAT")

        content_y = frame_y + 2
        content_h = frame_h - 5
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
        )

        text_x = center_x + 2
        text_w = center_w - 4
        self._safe_addstr(
            stdscr,
            content_y + 1,
            text_x,
            f"{self.player.name} HP {self.player.hp}/{self.player.max_hp}",
            self._c(5) | curses.A_BOLD,
        )
        self._safe_addstr(
            stdscr,
            content_y + 2,
            text_x,
            f"{monster.name} HP {max(0, monster.hp)}",
            self._c(3) | curses.A_BOLD,
        )

        art_lines = self._enemy_art_lines(monster.name)
        art_start_y = content_y + 4
        for i, line in enumerate(art_lines):
            y = art_start_y + i
            if y >= content_y + center_h - 7:
                break
            centered_x = text_x + max(0, (text_w - len(line)) // 2)
            self._safe_addstr(stdscr, y, centered_x, line[:text_w], self._c(2) | curses.A_BOLD)

        option_top = art_start_y + len(art_lines) + 1
        option_top = min(option_top, content_y + center_h - 8)
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
            f"Potions: {self.player.potions}",
            self._c(5),
        )

        log_y = option_top + 5
        for line in log[-5:]:
            if log_y >= content_y + center_h - 1:
                break
            self._safe_addstr(stdscr, log_y, text_x, line[:text_w], self._c(2))
            log_y += 1

        self._safe_addstr(
            stdscr,
            frame_y + frame_h - 2,
            frame_x + 2,
            "W/A/S/D or arrows move | Enter confirm"[: frame_w - 4],
            self._c(1) | curses.A_BOLD,
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
        glyphs = ".:!/^$"
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
                if ((x * 19 + y * 23 + phase + self._bg_seed) % 61) != 0:
                    continue
                ch = glyphs[(x + y + phase) % len(glyphs)]
                color = self._c(2 + ((x + y + phase) % 3))
                self._safe_addstr(stdscr, y, x, ch, color)

    def _draw_panel(self, stdscr: curses.window, y: int, x: int, h: int, w: int, title: str = "") -> None:
        max_y, max_x = stdscr.getmaxyx()
        if h < 3 or w < 4:
            return
        y2 = min(max_y - 1, y + h - 1)
        x2 = min(max_x - 1, x + w - 1)

        for yy in range(y + 1, y2):
            for xx in range(x + 1, x2):
                self._safe_addstr(stdscr, yy, xx, " ", self._c(5))

        hline = "-" * max(0, x2 - x - 1)
        self._safe_addstr(stdscr, y, x + 1, hline, self._c(1))
        self._safe_addstr(stdscr, y2, x + 1, hline, self._c(1))
        for yy in range(y + 1, y2):
            self._safe_addstr(stdscr, yy, x, "|", self._c(1))
            self._safe_addstr(stdscr, yy, x2, "|", self._c(1))
        self._safe_addstr(stdscr, y, x, "+", self._c(3))
        self._safe_addstr(stdscr, y, x2, "+", self._c(3))
        self._safe_addstr(stdscr, y2, x, "+", self._c(3))
        self._safe_addstr(stdscr, y2, x2, "+", self._c(3))

        if title:
            title_text = f" {title} "
            self._safe_addstr(stdscr, y, x + 2, title_text[: max(0, x2 - x - 3)], self._c(3) | curses.A_BOLD)

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
    ) -> None:
        player_x, player_y = player_pos
        exit_x, exit_y = exit_pos
        for y in range(min(max_h, len(grid))):
            for x in range(min(max_w, len(grid[0]))):
                tile = grid[y][x]
                ch = self._tile_char(x, y, tile)
                if tile == TILE_FLOOR:
                    color = self._c(1)
                elif tile == TILE_DOOR:
                    color = self._c(3) | curses.A_BOLD
                else:
                    color = self._c(2)
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
            f"Gold {self.player.gold} Potions {self.player.potions} "
            f"Dungeon {self.dungeon_level}"
        )

    def _tile_char(self, x: int, y: int, tile: int) -> str:
        if tile == TILE_DOOR:
            return "D"
        if tile == TILE_FLOOR:
            floors = ".:,'`"
            return floors[(x * 11 + y * 7 + self._bg_seed) % len(floors)]
        walls = "#/^W"
        return walls[(x * 13 + y * 5 + self._bg_seed) % len(walls)]

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

    def _combat_log_coords(
        self,
        stdscr: curses.window,
        monster: Monster,
        session: DungeonSession,
    ) -> tuple[int, int, int]:
        frame_y, frame_x, frame_h, frame_w = self._frame_rect(stdscr)
        content_y = frame_y + 2
        content_h = frame_h - 5
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
        art_lines = self._enemy_art_lines(monster.name)
        option_top = content_y + 4 + len(art_lines) + 1
        option_top = min(option_top, content_y + content_h - 8)
        log_y = option_top + 5
        return text_x, text_w, log_y

    def _toast(self, stdscr: curses.window, message: str) -> None:
        self._draw_background(stdscr, 73)
        frame_y, frame_x, frame_h, frame_w = self._frame_rect(stdscr)
        self._draw_panel(stdscr, frame_y, frame_x, frame_h, frame_w, "EVENT")
        y = frame_y + frame_h // 2
        x = frame_x + max(2, (frame_w - len(message)) // 2)
        self._safe_addstr(stdscr, y - 1, max(frame_x + 2, x - 4), ":: EVENT ::", self._c(3) | curses.A_BOLD)
        self._typewriter_draw(
            stdscr,
            y,
            x,
            message[: frame_w - 4],
            self._c(5) | curses.A_BOLD,
        )
        self._typewriter_draw(
            stdscr,
            y + 2,
            max(frame_x + 2, x - 2),
            "Press any key...",
            self._c(1),
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
            for i, ch in enumerate(text):
                key = stdscr.getch()
                if key in (10, 13, curses.KEY_ENTER):
                    self._typing_skip_until = time.monotonic() + 0.6
                    self._safe_addstr(stdscr, y, x, text, attr)
                    stdscr.refresh()
                    return
                if key != -1:
                    curses.ungetch(key)

                rendered += ch
                self._safe_addstr(stdscr, y, x, rendered, attr)
                stdscr.refresh()

                sleep_steps = max(1, int(self._typing_delay / 0.005))
                for _ in range(sleep_steps):
                    key = stdscr.getch()
                    if key in (10, 13, curses.KEY_ENTER):
                        self._typing_skip_until = time.monotonic() + 0.6
                        self._safe_addstr(stdscr, y, x, text, attr)
                        stdscr.refresh()
                        return
                    if key != -1:
                        curses.ungetch(key)
                    time.sleep(0.005)
        finally:
            stdscr.nodelay(False)

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
