import curses
import os
import random
import time
from dataclasses import dataclass
from typing import Literal

from ..models import Player


@dataclass
class IncomingAttack:
    x: float
    y: float
    vx: float
    vy: float
    source: Literal["north", "south", "east", "west"]
    glyph: str
    fake: bool


@dataclass
class WarriorTrainingResult:
    survival_time: float
    stamina_remaining: int
    ended_by: Literal["stamina_zero", "quit"]
    parries: int
    failures: int
    xp_gain: int
    hp_cost: int
    strength_gain: int
    defense_gain: int
    summary: str


class WarriorTrainer:
    _FPS = 60.0
    _FRAME_DT = 1.0 / _FPS
    _STAMINA_START = 24
    _GOOD_BLOCK_COST = 1
    _BAD_BLOCK_COST = 4
    _WRONG_FAKE_COST = 2
    _INPUT_BUFFER = 0.18

    def __init__(self, stdscr: curses.window, player: Player) -> None:
        self.stdscr = stdscr
        self.player = player
        self.rng = random.Random()
        self._unicode_ui = os.environ.get("TERM_REALMS_ASCII", "0") != "1"

        max_y, max_x = self.stdscr.getmaxyx()
        self.frame_y = max(0, (max_y - min(40, max_y - 2)) // 2)
        self.frame_x = max(0, (max_x - min(120, max_x - 4)) // 2)
        self.frame_h = max(18, min(40, max_y - 2))
        self.frame_w = max(44, min(120, max_x - 4))

        self.arena_y = self.frame_y + 3
        self.arena_x = self.frame_x + 3
        self.arena_h = max(10, self.frame_h - 8)
        self.arena_w = max(24, self.frame_w - 6)

        self.center_x = self.arena_w // 2
        self.center_y = self.arena_h // 2

        self.stamina = self._STAMINA_START
        self.elapsed = 0.0
        self.spawn_timer = 0.0
        self.phase = self.rng.randint(0, 999_999)

        self.parries = 0
        self.failures = 0
        self.ended_by: Literal["stamina_zero", "quit"] = "stamina_zero"
        self.quit_requested = False

        self.attacks: list[IncomingAttack] = []
        self.last_input_dir: Literal["north", "south", "east", "west"] | None = None
        self.last_input_time = 0.0
        self.flash_until = 0.0
        self.parry_flash_until = 0.0

    def run(self) -> WarriorTrainingResult:
        self.stdscr.nodelay(True)
        self.stdscr.keypad(True)
        last = time.monotonic()
        try:
            while self.stamina > 0 and not self.quit_requested:
                now = time.monotonic()
                dt = min(0.05, now - last)
                last = now
                self.handle_input(now)
                self.update(dt, now)
                self.render(now)
                spent = time.monotonic() - now
                if spent < self._FRAME_DT:
                    time.sleep(self._FRAME_DT - spent)
        finally:
            self.stdscr.nodelay(False)
        if self.quit_requested:
            self.ended_by = "quit"
        else:
            self.ended_by = "stamina_zero"
        return self._build_result()

    def handle_input(self, now: float) -> None:
        while True:
            key = self.stdscr.getch()
            if key == -1:
                return
            if key in (ord("q"), ord("Q"), 27):
                self.quit_requested = True
                return
            mapped = self._direction_from_key(key)
            if mapped is not None:
                self.last_input_dir = mapped
                self.last_input_time = now
                return

    def update(self, dt: float, now: float) -> None:
        if dt <= 0:
            return
        self.elapsed += dt
        self.phase += 1
        self.spawn_timer += dt

        spawn_interval = max(0.32, 1.0 - min(0.68, self.elapsed * 0.02))
        while self.spawn_timer >= spawn_interval:
            self.spawn_timer -= spawn_interval
            self._spawn_wave()

        for atk in self.attacks:
            atk.x += atk.vx * dt
            atk.y += atk.vy * dt

        self._resolve_attacks(now)
        self.attacks = [a for a in self.attacks if not self._out_of_bounds(a)]

    def render(self, now: float) -> None:
        self.stdscr.erase()
        self._draw_frame()
        self._draw_arena(now)
        self._draw_hud()
        self.stdscr.refresh()

    def _draw_frame(self) -> None:
        h = "─" if self._unicode_ok() else "-"
        v = "│" if self._unicode_ok() else "|"
        tl = "┌" if self._unicode_ok() else "+"
        tr = "┐" if self._unicode_ok() else "+"
        bl = "└" if self._unicode_ok() else "+"
        br = "┘" if self._unicode_ok() else "+"
        for x in range(self.frame_x + 1, self.frame_x + self.frame_w - 1):
            self._safe_addstr(self.frame_y, x, h, self._c(1))
            self._safe_addstr(self.frame_y + self.frame_h - 1, x, h, self._c(1))
        for y in range(self.frame_y + 1, self.frame_y + self.frame_h - 1):
            self._safe_addstr(y, self.frame_x, v, self._c(1))
            self._safe_addstr(y, self.frame_x + self.frame_w - 1, v, self._c(1))
        self._safe_addstr(self.frame_y, self.frame_x, tl, self._c(3))
        self._safe_addstr(self.frame_y, self.frame_x + self.frame_w - 1, tr, self._c(3))
        self._safe_addstr(self.frame_y + self.frame_h - 1, self.frame_x, bl, self._c(3))
        self._safe_addstr(self.frame_y + self.frame_h - 1, self.frame_x + self.frame_w - 1, br, self._c(3))
        title = " WARRIOR REFLEX TRAINING "
        self._safe_addstr(self.frame_y, self.frame_x + 2, title, self._c(3) | curses.A_BOLD)

    def _draw_arena(self, now: float) -> None:
        arena_h = "─" if self._unicode_ok() else "-"
        arena_v = "│" if self._unicode_ok() else "|"
        for x in range(self.arena_x, self.arena_x + self.arena_w):
            self._safe_addstr(self.arena_y, x, arena_h, self._c(1))
            self._safe_addstr(self.arena_y + self.arena_h - 1, x, arena_h, self._c(1))
        for y in range(self.arena_y + 1, self.arena_y + self.arena_h - 1):
            self._safe_addstr(y, self.arena_x, arena_v, self._c(1))
            self._safe_addstr(y, self.arena_x + self.arena_w - 1, arena_v, self._c(1))

        for i in range(24):
            nx = self.arena_x + 1 + ((self.phase + i * 7) % max(1, self.arena_w - 2))
            ny = self.arena_y + 1 + ((self.phase // 2 + i * 5) % max(1, self.arena_h - 2))
            self._safe_addstr(ny, nx, ".", self._c(5) | curses.A_DIM)

        for atk in self.attacks:
            sx = self.arena_x + int(round(atk.x))
            sy = self.arena_y + int(round(atk.y))
            if atk.fake:
                attr = self._c(3) | curses.A_DIM
            else:
                attr = self._c(4) | curses.A_BOLD
            self._safe_addstr(sy, sx, atk.glyph, attr)

        center_attr = self._c(6) | curses.A_BOLD
        if now < self.parry_flash_until:
            center_attr = self._c(2) | curses.A_BOLD
        if now < self.flash_until:
            center_attr = self._c(4) | curses.A_BOLD
        self._safe_addstr(
            self.arena_y + self.center_y,
            self.arena_x + self.center_x,
            "W",
            center_attr,
        )

    def _draw_hud(self) -> None:
        stamina_bar = self._bar(self.stamina, self._STAMINA_START, 14)
        self._safe_addstr(
            self.frame_y + 1,
            self.frame_x + 2,
            f"Stamina {stamina_bar} {max(0, self.stamina)}/{self._STAMINA_START}  Time {self.elapsed:05.1f}s",
            self._c(5) | curses.A_BOLD,
        )
        self._safe_addstr(
            self.frame_y + 2,
            self.frame_x + 2,
            f"Parries {self.parries}  Misses {self.failures}",
            self._c(2) | curses.A_BOLD,
        )
        self._safe_addstr(
            self.frame_y + self.frame_h - 2,
            self.frame_x + 2,
            "Block by source: W(up) S(down) A(left) D(right) | Q/Esc exit",
            self._c(1),
        )

    def _spawn_wave(self) -> None:
        base_speed = 6.0 + min(8.0, self.elapsed * 0.12)
        fake_chance = min(0.25, 0.08 + self.elapsed * 0.004)
        wave = 1
        if self.elapsed > 16 and self.rng.random() < 0.35:
            wave += 1
        if self.elapsed > 34 and self.rng.random() < 0.22:
            wave += 1

        dirs = ["north", "south", "east", "west"]
        self.rng.shuffle(dirs)
        for source in dirs[:wave]:
            fake = self.rng.random() < fake_chance
            self.attacks.append(self._make_attack(source, base_speed, fake))

    def _make_attack(
        self,
        source: Literal["north", "south", "east", "west"],
        speed: float,
        fake: bool,
    ) -> IncomingAttack:
        if source == "north":
            return IncomingAttack(
                x=float(self.center_x),
                y=1.0,
                vx=0.0,
                vy=speed,
                source=source,
                glyph="v",
                fake=fake,
            )
        if source == "south":
            return IncomingAttack(
                x=float(self.center_x),
                y=float(self.arena_h - 2),
                vx=0.0,
                vy=-speed,
                source=source,
                glyph="^",
                fake=fake,
            )
        if source == "east":
            return IncomingAttack(
                x=float(self.arena_w - 2),
                y=float(self.center_y),
                vx=-speed,
                vy=0.0,
                source=source,
                glyph="<",
                fake=fake,
            )
        return IncomingAttack(
            x=1.0,
            y=float(self.center_y),
            vx=speed,
            vy=0.0,
            source=source,
            glyph=">",
            fake=fake,
        )

    def _resolve_attacks(self, now: float) -> None:
        if self.last_input_dir is not None and now - self.last_input_time > self._INPUT_BUFFER:
            self.last_input_dir = None

        keep: list[IncomingAttack] = []
        for atk in self.attacks:
            dist = abs(atk.x - self.center_x) + abs(atk.y - self.center_y)
            in_window = dist <= 1.25
            at_center = dist <= 0.35

            if in_window and self.last_input_dir == atk.source:
                if atk.fake:
                    self.stamina -= self._WRONG_FAKE_COST
                    self.failures += 1
                    self.flash_until = now + 0.10
                else:
                    self.stamina -= self._GOOD_BLOCK_COST
                    self.parries += 1
                    self.parry_flash_until = now + 0.11
                self.last_input_dir = None
                continue

            if at_center:
                if not atk.fake:
                    self.stamina -= self._BAD_BLOCK_COST
                    self.failures += 1
                    self.flash_until = now + 0.18
                continue
            keep.append(atk)
        self.attacks = keep

    def _direction_from_key(self, key: int) -> Literal["north", "south", "east", "west"] | None:
        if key in (ord("w"), ord("W"), curses.KEY_UP):
            return "north"
        if key in (ord("s"), ord("S"), curses.KEY_DOWN):
            return "south"
        if key in (ord("a"), ord("A"), curses.KEY_LEFT):
            return "west"
        if key in (ord("d"), ord("D"), curses.KEY_RIGHT):
            return "east"
        return None

    def _bar(self, value: int, max_value: int, width: int) -> str:
        full = "█" if self._unicode_ok() else "#"
        empty = "░" if self._unicode_ok() else "."
        if max_value <= 0:
            return empty * width
        ratio = max(0.0, min(1.0, value / max_value))
        filled = max(0, min(width, int(round(width * ratio))))
        return (full * filled) + (empty * (width - filled))

    def _out_of_bounds(self, atk: IncomingAttack) -> bool:
        return atk.x < -2 or atk.y < -2 or atk.x > self.arena_w + 2 or atk.y > self.arena_h + 2

    def _build_result(self) -> WarriorTrainingResult:
        completion = 0.7 if self.ended_by == "quit" else 1.0
        base_xp = min(120, 20 + int(self.elapsed * 2.2) + self.parries * 2)
        xp_gain = max(1, int(base_xp * completion))
        hp_cost = max(1, int((2 + self.failures * 0.7) * completion))
        strength_gain = 1
        defense_gain = 1 if self.parries >= 8 else 0
        if self.parries >= 18:
            strength_gain += 1

        summary = (
            f"Warrior Training {self.elapsed:.1f}s | Parries {self.parries} Misses {self.failures} "
            f"| +{xp_gain} XP -{hp_cost} HP +{strength_gain} STR"
            + (f" +{defense_gain} DEF" if defense_gain else "")
        )
        return WarriorTrainingResult(
            survival_time=self.elapsed,
            stamina_remaining=max(0, self.stamina),
            ended_by=self.ended_by,
            parries=self.parries,
            failures=self.failures,
            xp_gain=xp_gain,
            hp_cost=hp_cost,
            strength_gain=strength_gain,
            defense_gain=defense_gain,
            summary=summary,
        )

    def _safe_addstr(self, y: int, x: int, text: str, attr: int = 0) -> None:
        max_y, max_x = self.stdscr.getmaxyx()
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
            self.stdscr.addstr(y, x, clipped, attr)
        except curses.error:
            pass

    def _c(self, pair_id: int) -> int:
        if not curses.has_colors():
            return 0
        return curses.color_pair(pair_id)

    def _unicode_ok(self) -> bool:
        return self._unicode_ui


def start_warrior_training(stdscr: curses.window, player: Player) -> WarriorTrainingResult:
    return WarriorTrainer(stdscr, player).run()
