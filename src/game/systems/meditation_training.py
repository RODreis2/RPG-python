import curses
import math
import random
import time
from dataclasses import dataclass
from typing import Literal

from ..models import Player


@dataclass
class MeditationEntity:
    x: float
    y: float
    vx: float
    vy: float
    glyph: str
    kind: Literal["enemy", "chaos", "particle"]
    damage: int = 0
    ttl: float = 0.0


@dataclass
class MeditationState:
    orb_x: float
    orb_y: float
    focus: int
    elapsed: float
    enemy_timer: float
    chaos_timer: float
    particle_timer: float
    hit_flash: float
    quit_requested: bool


@dataclass
class MeditationResult:
    survival_time: float
    focus_remaining: int
    ended_by: Literal["focus_zero", "quit"]
    xp_gain: int
    hp_cost: int
    speed_gain: int
    summary: str


class MeditationTrainer:
    _FOCUS_START = 12
    _ORB_SPEED = 12.0
    _INTENT_HOLD_SECONDS = 0.12
    _FRAME_SECONDS = 1.0 / 60.0

    def __init__(self, stdscr: curses.window, player: Player) -> None:
        self.stdscr = stdscr
        self.player = player
        self.rng = random.Random()

        max_y, max_x = self.stdscr.getmaxyx()
        self.frame_y = 1
        self.frame_x = 2
        self.frame_h = max(16, min(42, max_y - 2))
        self.frame_w = max(40, min(120, max_x - 4))
        self.frame_y = max(0, (max_y - self.frame_h) // 2)
        self.frame_x = max(0, (max_x - self.frame_w) // 2)

        self.arena_y = self.frame_y + 4
        self.arena_x = self.frame_x + 3
        self.arena_h = max(8, self.frame_h - 8)
        self.arena_w = max(18, self.frame_w - 6)

        self.state = MeditationState(
            orb_x=self.arena_w / 2.0,
            orb_y=self.arena_h / 2.0,
            focus=self._FOCUS_START,
            elapsed=0.0,
            enemy_timer=0.0,
            chaos_timer=0.0,
            particle_timer=0.0,
            hit_flash=0.0,
            quit_requested=False,
        )
        self.entities: list[MeditationEntity] = []
        self.intent_dx = 0
        self.intent_dy = 0
        self.intent_ttl = 0.0
        self.phase = self.rng.randint(0, 999_999)

    def run(self) -> MeditationResult:
        self.stdscr.nodelay(True)
        self.stdscr.keypad(True)
        last = time.monotonic()
        ended_by: Literal["focus_zero", "quit"] = "focus_zero"
        try:
            while True:
                now = time.monotonic()
                dt = min(0.05, now - last)
                last = now

                self.handle_input()
                self.update(dt)
                self.render()

                if self.state.quit_requested:
                    ended_by = "quit"
                    break
                if self.state.focus <= 0:
                    ended_by = "focus_zero"
                    break

                spent = time.monotonic() - now
                if spent < self._FRAME_SECONDS:
                    time.sleep(self._FRAME_SECONDS - spent)
        finally:
            self.stdscr.nodelay(False)

        return self._build_result(ended_by)

    def handle_input(self) -> None:
        while True:
            key = self.stdscr.getch()
            if key == -1:
                break
            if key in (ord("q"), ord("Q"), 27):
                self.state.quit_requested = True
                return
            if key in (ord("w"), ord("W"), curses.KEY_UP):
                self.intent_dx, self.intent_dy = 0, -1
                self.intent_ttl = self._INTENT_HOLD_SECONDS
            elif key in (ord("s"), ord("S"), curses.KEY_DOWN):
                self.intent_dx, self.intent_dy = 0, 1
                self.intent_ttl = self._INTENT_HOLD_SECONDS
            elif key in (ord("a"), ord("A"), curses.KEY_LEFT):
                self.intent_dx, self.intent_dy = -1, 0
                self.intent_ttl = self._INTENT_HOLD_SECONDS
            elif key in (ord("d"), ord("D"), curses.KEY_RIGHT):
                self.intent_dx, self.intent_dy = 1, 0
                self.intent_ttl = self._INTENT_HOLD_SECONDS

    def update(self, dt: float) -> None:
        if dt <= 0.0:
            return

        self.state.elapsed += dt
        self.phase += 1
        self.state.hit_flash = max(0.0, self.state.hit_flash - dt)

        if self.intent_ttl > 0.0:
            self.state.orb_x += self.intent_dx * self._ORB_SPEED * dt
            self.state.orb_y += self.intent_dy * self._ORB_SPEED * dt
            self.intent_ttl = max(0.0, self.intent_ttl - dt)

        self.state.orb_x = max(1.0, min(self.arena_w - 2.0, self.state.orb_x))
        self.state.orb_y = max(1.0, min(self.arena_h - 2.0, self.state.orb_y))

        spawn_multiplier = 1.0 + min(2.5, self.state.elapsed / 35.0)
        enemy_interval = 0.85 / spawn_multiplier
        chaos_interval = 1.10 / spawn_multiplier
        particle_interval = max(0.06, 0.30 / spawn_multiplier)

        self.state.enemy_timer += dt
        self.state.chaos_timer += dt
        self.state.particle_timer += dt

        while self.state.enemy_timer >= enemy_interval:
            self.state.enemy_timer -= enemy_interval
            self.entities.append(self._spawn_threat("enemy"))
        while self.state.chaos_timer >= chaos_interval:
            self.state.chaos_timer -= chaos_interval
            self.entities.append(self._spawn_threat("chaos"))
        while self.state.particle_timer >= particle_interval:
            self.state.particle_timer -= particle_interval
            self.entities.append(self._spawn_particle())

        updated: list[MeditationEntity] = []
        orb_cell = (int(round(self.state.orb_x)), int(round(self.state.orb_y)))
        for entity in self.entities:
            entity.x += entity.vx * dt
            entity.y += entity.vy * dt

            if entity.kind == "particle":
                entity.ttl -= dt
                if entity.ttl <= 0.0:
                    continue

            if entity.kind in ("enemy", "chaos"):
                cell = (int(round(entity.x)), int(round(entity.y)))
                if cell == orb_cell:
                    self.state.focus -= entity.damage
                    self.state.hit_flash = 0.12
                    continue

            if (
                entity.x < -2
                or entity.y < -2
                or entity.x > self.arena_w + 2
                or entity.y > self.arena_h + 2
            ):
                continue
            updated.append(entity)
        self.entities = updated

    def render(self) -> None:
        self.stdscr.erase()
        self._draw_border()
        self._draw_arena()
        self._draw_hud()
        self.stdscr.refresh()

    def _draw_border(self) -> None:
        self._safe_addstr(
            self.frame_y,
            self.frame_x + 2,
            " MEDITATION TRAINING ",
            self._c(3) | curses.A_BOLD,
        )
        for x in range(self.frame_x, self.frame_x + self.frame_w):
            self._safe_addstr(self.frame_y + 1, x, "-", self._c(1))
            self._safe_addstr(self.frame_y + self.frame_h - 1, x, "-", self._c(1))
        for y in range(self.frame_y + 1, self.frame_y + self.frame_h - 1):
            self._safe_addstr(y, self.frame_x, "|", self._c(1))
            self._safe_addstr(y, self.frame_x + self.frame_w - 1, "|", self._c(1))
        self._safe_addstr(self.frame_y + 1, self.frame_x, "+", self._c(3))
        self._safe_addstr(self.frame_y + 1, self.frame_x + self.frame_w - 1, "+", self._c(3))
        self._safe_addstr(self.frame_y + self.frame_h - 1, self.frame_x, "+", self._c(3))
        self._safe_addstr(
            self.frame_y + self.frame_h - 1,
            self.frame_x + self.frame_w - 1,
            "+",
            self._c(3),
        )

    def _draw_arena(self) -> None:
        for x in range(self.arena_x, self.arena_x + self.arena_w):
            self._safe_addstr(self.arena_y, x, "-", self._c(1))
            self._safe_addstr(self.arena_y + self.arena_h - 1, x, "-", self._c(1))
        for y in range(self.arena_y + 1, self.arena_y + self.arena_h - 1):
            self._safe_addstr(y, self.arena_x, "|", self._c(1))
            self._safe_addstr(y, self.arena_x + self.arena_w - 1, "|", self._c(1))

        noise_steps = 10 + min(80, int(self.state.elapsed * 2.3))
        for i in range(noise_steps):
            nx = self.arena_x + 1 + ((i * 11 + self.phase) % max(1, self.arena_w - 2))
            ny = self.arena_y + 1 + ((i * 7 + self.phase // 3) % max(1, self.arena_h - 2))
            glyph = "." if (i + self.phase) % 2 == 0 else "'"
            self._safe_addstr(ny, nx, glyph, self._c(2) | curses.A_DIM)

        for entity in self.entities:
            ex = self.arena_x + int(round(entity.x))
            ey = self.arena_y + int(round(entity.y))
            if entity.kind == "enemy":
                attr = self._c(4) | curses.A_BOLD
            elif entity.kind == "chaos":
                attr = self._c(3)
            else:
                attr = self._c(2) | curses.A_DIM
            self._safe_addstr(ey, ex, entity.glyph, attr)

        orb_x = self.arena_x + int(round(self.state.orb_x))
        orb_y = self.arena_y + int(round(self.state.orb_y))
        orb_attr = self._c(6) | curses.A_BOLD
        if self.state.hit_flash > 0.0:
            orb_attr = self._c(4) | curses.A_BOLD
        self._safe_addstr(orb_y, orb_x, "@", orb_attr)

    def _draw_hud(self) -> None:
        calm_index = max(0, 100 - int(self.state.elapsed * 2.2))
        self._safe_addstr(
            self.frame_y + 2,
            self.frame_x + 2,
            f"Focus: {max(0, self.state.focus)}   Time: {self.state.elapsed:05.1f}s   Calm Index: {calm_index:02d}",
            self._c(5) | curses.A_BOLD,
        )
        self._safe_addstr(
            self.frame_y + self.frame_h - 2,
            self.frame_x + 2,
            "Move: W/A/S/D or arrows | Survive chaos | Q/Esc end meditation",
            self._c(1),
        )

    def _spawn_threat(self, kind: Literal["enemy", "chaos"]) -> MeditationEntity:
        side = self.rng.randint(0, 3)
        if side == 0:
            x = 1.0
            y = self.rng.uniform(1.0, self.arena_h - 2.0)
        elif side == 1:
            x = self.arena_w - 2.0
            y = self.rng.uniform(1.0, self.arena_h - 2.0)
        elif side == 2:
            x = self.rng.uniform(1.0, self.arena_w - 2.0)
            y = 1.0
        else:
            x = self.rng.uniform(1.0, self.arena_w - 2.0)
            y = self.arena_h - 2.0

        tx = self.state.orb_x - x
        ty = self.state.orb_y - y
        if kind == "chaos":
            tx += self.rng.uniform(-4.0, 4.0)
            ty += self.rng.uniform(-4.0, 4.0)

        length = max(0.001, math.hypot(tx, ty))
        ux, uy = tx / length, ty / length

        if kind == "enemy":
            speed = 7.0 + min(7.0, self.state.elapsed * 0.08)
            glyph = "x"
            damage = 2
        else:
            speed = 5.8 + min(5.0, self.state.elapsed * 0.06)
            glyph = "o"
            damage = 1

        return MeditationEntity(x=x, y=y, vx=ux * speed, vy=uy * speed, glyph=glyph, kind=kind, damage=damage)

    def _spawn_particle(self) -> MeditationEntity:
        side = self.rng.randint(0, 3)
        if side == 0:
            x, y = 1.0, self.rng.uniform(1.0, self.arena_h - 2.0)
            vx, vy = self.rng.uniform(0.4, 1.6), self.rng.uniform(-0.5, 0.5)
        elif side == 1:
            x, y = self.arena_w - 2.0, self.rng.uniform(1.0, self.arena_h - 2.0)
            vx, vy = self.rng.uniform(-1.6, -0.4), self.rng.uniform(-0.5, 0.5)
        elif side == 2:
            x, y = self.rng.uniform(1.0, self.arena_w - 2.0), 1.0
            vx, vy = self.rng.uniform(-0.5, 0.5), self.rng.uniform(0.4, 1.4)
        else:
            x, y = self.rng.uniform(1.0, self.arena_w - 2.0), self.arena_h - 2.0
            vx, vy = self.rng.uniform(-0.5, 0.5), self.rng.uniform(-1.4, -0.4)
        return MeditationEntity(
            x=x,
            y=y,
            vx=vx,
            vy=vy,
            glyph="*",
            kind="particle",
            ttl=self.rng.uniform(1.2, 2.8),
        )

    def _build_result(self, ended_by: Literal["focus_zero", "quit"]) -> MeditationResult:
        elapsed = self.state.elapsed
        completion = 0.65 if ended_by == "quit" else 1.0
        base_xp = min(90, 18 + int(elapsed * 3.2))
        xp_gain = max(1, int(base_xp * completion))
        hp_cost = max(1, int((2.0 + elapsed * 0.15) * completion))
        speed_gain = 0
        speed_roll = 0.45 * completion
        if elapsed >= 28.0 and self.rng.random() < speed_roll:
            speed_gain = 1

        end_text = "focus shattered" if ended_by == "focus_zero" else "session ended early"
        summary = (
            f"Meditation ({end_text}) {elapsed:.1f}s | +{xp_gain} XP -{hp_cost} HP"
            + (" +1 SPD" if speed_gain else "")
        )
        return MeditationResult(
            survival_time=elapsed,
            focus_remaining=max(0, self.state.focus),
            ended_by=ended_by,
            xp_gain=xp_gain,
            hp_cost=hp_cost,
            speed_gain=speed_gain,
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
            return

    def _c(self, pair_id: int) -> int:
        if not curses.has_colors():
            return 0
        return curses.color_pair(pair_id)


def start_meditation_training(stdscr: curses.window, player: Player) -> MeditationResult:
    trainer = MeditationTrainer(stdscr, player)
    return trainer.run()
