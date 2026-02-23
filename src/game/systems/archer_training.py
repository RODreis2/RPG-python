import curses
import os
import random
import time
from dataclasses import dataclass

from ..models import Player


@dataclass
class ArrowShot:
    x: float
    y: float
    vx: float
    vy: float
    charged: bool


@dataclass
class MovingTarget:
    x: float
    y: float
    vx: float
    base_y: float
    pattern: str  # straight | zigzag | drift
    phase: float
    amplitude: float
    fake: bool
    small: bool


@dataclass
class ArcherTrainingResult:
    score: int
    hits: int
    misses: int
    best_combo: int
    accuracy: float
    focus_remaining: int
    success: bool
    ended_by: str
    xp_gain: int
    hp_cost: int
    speed_gain: int
    summary: str


class ArcherTrainer:
    _FPS = 60.0
    _FRAME_DT = 1.0 / _FPS
    _DURATION = 48.0
    _FOCUS_START = 20
    _INPUT_RELEASE_WINDOW = 0.11

    def __init__(self, stdscr: curses.window, player: Player) -> None:
        self.stdscr = stdscr
        self.player = player
        self.rng = random.Random()
        self._unicode_ui = os.environ.get("TERM_REALMS_ASCII", "0") != "1"

        max_y, max_x = self.stdscr.getmaxyx()
        self.frame_h = max(18, min(40, max_y - 2))
        self.frame_w = max(56, min(120, max_x - 4))
        self.frame_y = max(0, (max_y - self.frame_h) // 2)
        self.frame_x = max(0, (max_x - self.frame_w) // 2)

        self.arena_y = self.frame_y + 4
        self.arena_x = self.frame_x + 2
        self.arena_h = max(10, self.frame_h - 8)
        self.arena_w = max(28, self.frame_w - 4)

        self.archer_x = 2
        self.archer_y = self.arena_h // 2

        self.elapsed = 0.0
        self.focus = self._FOCUS_START
        self.score = 0
        self.hits = 0
        self.misses = 0
        self.combo = 0
        self.best_combo = 0

        self.wind = 0.0
        self.spawn_timer = 0.0
        self.shot_cooldown = 0.0
        self.phase = self.rng.randint(0, 999_999)

        self.eagle_eye_until = 0.0
        self.flash_hit_until = 0.0
        self.flash_miss_until = 0.0

        self.charging = False
        self.charge_power = 0.0
        self.last_space_event = 0.0
        self.quit_requested = False

        self.arrows: list[ArrowShot] = []
        self.targets: list[MovingTarget] = []

    def run(self) -> ArcherTrainingResult:
        self.stdscr.nodelay(True)
        self.stdscr.keypad(True)
        last = time.monotonic()
        ended_by = "time_up"
        try:
            while True:
                now = time.monotonic()
                dt = min(0.05, now - last)
                last = now

                self.handle_input(now)
                self.update(dt, now)
                self.render(now)

                if self.quit_requested:
                    ended_by = "quit"
                    break
                if self.focus <= 0:
                    ended_by = "focus_zero"
                    break
                if self.elapsed >= self._DURATION:
                    ended_by = "time_up"
                    break

                spent = time.monotonic() - now
                if spent < self._FRAME_DT:
                    time.sleep(self._FRAME_DT - spent)
        finally:
            self.stdscr.nodelay(False)
        return self._build_result(ended_by)

    def handle_input(self, now: float) -> None:
        while True:
            key = self.stdscr.getch()
            if key == -1:
                return
            if key in (ord("q"), ord("Q"), 27):
                self.quit_requested = True
                return
            if key in (ord("w"), ord("W"), curses.KEY_UP):
                self.archer_y = max(1, self.archer_y - 1)
                continue
            if key in (ord("s"), ord("S"), curses.KEY_DOWN):
                self.archer_y = min(self.arena_h - 2, self.archer_y + 1)
                continue
            if key == ord(" "):
                self.last_space_event = now
                if not self.charging and self.shot_cooldown <= 0:
                    self.charging = True
                    self.charge_power = 0.0

    def update(self, dt: float, now: float) -> None:
        if dt <= 0:
            return
        self.elapsed += dt
        self.phase += 1
        self.shot_cooldown = max(0.0, self.shot_cooldown - dt)
        self.spawn_timer += dt

        self._update_charge(dt, now)
        self._update_difficulty(now)
        self._update_targets(dt, now)
        self._update_arrows(dt)
        self._resolve_collisions(now)
        self._clean_lists()

    def render(self, now: float) -> None:
        self.stdscr.erase()
        self._draw_frame()
        self._draw_arena(now)
        self._draw_hud(now)
        self.stdscr.refresh()

    def _update_charge(self, dt: float, now: float) -> None:
        if not self.charging:
            return
        self.charge_power = min(1.0, self.charge_power + dt * 1.4)
        # Terminal does not provide key-up, so release is inferred after key-repeat gap.
        if now - self.last_space_event > self._INPUT_RELEASE_WINDOW:
            self._fire_arrow()
            self.charging = False
            self.charge_power = 0.0

    def _update_difficulty(self, now: float) -> None:
        self.wind = 0.18 * (1 if int(now * 1.7) % 2 == 0 else -1) if self.elapsed > 18 else 0.0
        base_interval = max(0.34, 0.95 - self.elapsed * 0.012)
        while self.spawn_timer >= base_interval:
            self.spawn_timer -= base_interval
            self._spawn_target(now)

    def _spawn_target(self, now: float) -> None:
        speed = 4.8 + min(5.8, self.elapsed * 0.10)
        if now < self.eagle_eye_until:
            speed *= 0.72
        y = self.rng.uniform(2.0, self.arena_h - 3.0)
        pattern_roll = self.rng.random()
        if pattern_roll < 0.45:
            pattern = "straight"
            amp = 0.0
        elif pattern_roll < 0.80:
            pattern = "drift"
            amp = self.rng.uniform(0.6, 1.4)
        else:
            pattern = "zigzag"
            amp = self.rng.uniform(1.0, 2.2)
        fake = self.elapsed > 20 and self.rng.random() < min(0.22, 0.05 + self.elapsed * 0.003)
        small = self.elapsed > 26 and self.rng.random() < 0.25
        self.targets.append(
            MovingTarget(
                x=float(self.arena_w - 2),
                y=y,
                vx=-speed,
                base_y=y,
                pattern=pattern,
                phase=self.rng.uniform(0.0, 6.28),
                amplitude=amp,
                fake=fake,
                small=small,
            )
        )

    def _update_targets(self, dt: float, now: float) -> None:
        for t in self.targets:
            t.x += t.vx * dt
            t.phase += dt * 5.0
            if t.pattern == "zigzag":
                t.y = t.base_y + (t.amplitude * (1 if int(t.phase * 2.0) % 2 == 0 else -1))
            elif t.pattern == "drift":
                t.y += (0.35 if int(t.phase) % 2 == 0 else -0.35) * dt * 8
            if now < self.eagle_eye_until:
                t.x += abs(t.vx) * dt * 0.28
            t.y = max(1.0, min(self.arena_h - 2.0, t.y))

    def _update_arrows(self, dt: float) -> None:
        for a in self.arrows:
            a.x += a.vx * dt
            a.y += a.vy * dt

    def _resolve_collisions(self, now: float) -> None:
        target_used: set[int] = set()
        arrow_used: set[int] = set()
        for ai, arrow in enumerate(self.arrows):
            for ti, target in enumerate(self.targets):
                if ti in target_used:
                    continue
                hit_radius = 0.40 if target.small else 0.70
                if abs(arrow.x - target.x) <= hit_radius and abs(arrow.y - target.y) <= 0.65:
                    arrow_used.add(ai)
                    target_used.add(ti)
                    if target.fake:
                        self.focus -= 2
                        self.combo = 0
                        self.misses += 1
                        self.flash_miss_until = now + 0.12
                    else:
                        self.hits += 1
                        self.combo += 1
                        self.best_combo = max(self.best_combo, self.combo)
                        points = 10 + (4 if arrow.charged else 0) + min(20, self.combo * 2)
                        if target.small:
                            points += 6
                        self.score += points
                        self.flash_hit_until = now + 0.10
                        if self.combo >= 5:
                            self.eagle_eye_until = max(self.eagle_eye_until, now + 2.5)
                    break

        if target_used:
            self.targets = [t for i, t in enumerate(self.targets) if i not in target_used]
        if arrow_used:
            self.arrows = [a for i, a in enumerate(self.arrows) if i not in arrow_used]

    def _clean_lists(self) -> None:
        kept_arrows: list[ArrowShot] = []
        for a in self.arrows:
            if a.x > self.arena_w - 1 or a.y < 0 or a.y > self.arena_h - 1:
                self.misses += 1
                self.focus -= 1
                self.combo = 0
                continue
            kept_arrows.append(a)
        self.arrows = kept_arrows
        self.targets = [t for t in self.targets if t.x >= 1]

    def _fire_arrow(self) -> None:
        if self.shot_cooldown > 0:
            return
        charged = self.charge_power >= 0.55
        speed = 16.0 + self.charge_power * 10.0
        vy = self.wind * (0.55 if charged else 1.0)
        self.arrows.append(
            ArrowShot(
                x=float(self.archer_x + 1),
                y=float(self.archer_y),
                vx=speed,
                vy=vy,
                charged=charged,
            )
        )
        self.shot_cooldown = 0.12 + self.charge_power * 0.28
        if charged:
            self.focus = max(0, self.focus - 1)

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
        self._safe_addstr(
            self.frame_y,
            self.frame_x + 2,
            " ARCHER PRECISION TRAINING ",
            self._c(3) | curses.A_BOLD,
        )

    def _draw_arena(self, now: float) -> None:
        h = "─" if self._unicode_ok() else "-"
        v = "│" if self._unicode_ok() else "|"
        for x in range(self.arena_x, self.arena_x + self.arena_w):
            self._safe_addstr(self.arena_y, x, h, self._c(1))
            self._safe_addstr(self.arena_y + self.arena_h - 1, x, h, self._c(1))
        for y in range(self.arena_y + 1, self.arena_y + self.arena_h - 1):
            self._safe_addstr(y, self.arena_x, v, self._c(1))
            self._safe_addstr(y, self.arena_x + self.arena_w - 1, v, self._c(1))

        for i in range(20):
            nx = self.arena_x + 1 + ((self.phase + i * 9) % max(1, self.arena_w - 2))
            ny = self.arena_y + 1 + ((self.phase // 3 + i * 5) % max(1, self.arena_h - 2))
            self._safe_addstr(ny, nx, ".", self._c(5) | curses.A_DIM)

        archer_attr = self._c(6) | curses.A_BOLD
        if now < self.flash_hit_until:
            archer_attr = self._c(2) | curses.A_BOLD
        elif now < self.flash_miss_until:
            archer_attr = self._c(4) | curses.A_BOLD
        self._safe_addstr(self.arena_y + self.archer_y, self.arena_x + self.archer_x, "A", archer_attr)

        for arrow in self.arrows:
            sx = self.arena_x + int(round(arrow.x))
            sy = self.arena_y + int(round(arrow.y))
            glyph = ">" if arrow.vx >= 0 else "-"
            attr = self._c(3) | curses.A_BOLD if arrow.charged else self._c(5)
            self._safe_addstr(sy, sx, glyph, attr)

        for target in self.targets:
            sx = self.arena_x + int(round(target.x))
            sy = self.arena_y + int(round(target.y))
            if target.fake:
                glyph = "*" if self._unicode_ok() else "x"
                attr = self._c(3) | curses.A_DIM
            else:
                glyph = "o" if not target.small else "."
                attr = self._c(2) | curses.A_BOLD
            self._safe_addstr(sy, sx, glyph, attr)

    def _draw_hud(self, now: float) -> None:
        focus_bar = self._bar(self.focus, self._FOCUS_START, 12)
        shots = self.hits + self.misses
        accuracy = (self.hits / shots) if shots else 1.0
        eagle = "ON" if now < self.eagle_eye_until else "OFF"
        self._safe_addstr(
            self.frame_y + 1,
            self.frame_x + 2,
            (
                f"Focus {focus_bar} {max(0, self.focus)}/{self._FOCUS_START}  "
                f"Score {self.score}  Combo x{self.combo}"
            )[: self.frame_w - 4],
            self._c(5) | curses.A_BOLD,
        )
        self._safe_addstr(
            self.frame_y + 2,
            self.frame_x + 2,
            (
                f"Hits {self.hits}  Misses {self.misses}  Accuracy {accuracy*100:05.1f}%  "
                f"Eagle Eye {eagle}  Wind {self.wind:+.2f}"
            )[: self.frame_w - 4],
            self._c(2) | curses.A_BOLD,
        )
        charge_pct = int(self.charge_power * 100) if self.charging else 0
        self._safe_addstr(
            self.frame_y + self.frame_h - 2,
            self.frame_x + 2,
            (
                f"SPACE shoot/charge-release  Charge {charge_pct:3d}%  "
                f"Q/Esc end  Time {max(0.0, self._DURATION - self.elapsed):04.1f}s"
            )[: self.frame_w - 4],
            self._c(1),
        )

    def _bar(self, value: int, max_value: int, width: int) -> str:
        full = "█" if self._unicode_ok() else "#"
        empty = "░" if self._unicode_ok() else "."
        if max_value <= 0:
            return empty * width
        ratio = max(0.0, min(1.0, value / max_value))
        filled = max(0, min(width, int(round(width * ratio))))
        return (full * filled) + (empty * (width - filled))

    def _build_result(self, ended_by: str) -> ArcherTrainingResult:
        shots = self.hits + self.misses
        accuracy = (self.hits / shots) if shots else 0.0
        success = ended_by == "time_up" and self.hits >= 14 and accuracy >= 0.45
        completion = 0.70 if ended_by == "quit" else 1.0
        base_xp = min(140, 20 + self.hits * 5 + self.best_combo * 3 + int(self.elapsed * 1.1))
        xp_gain = max(1, int(base_xp * completion))
        hp_cost = max(1, int((2 + self.misses * 0.45) * completion))
        speed_gain = 1 if self.best_combo >= 7 else 0
        if success:
            xp_gain += 12
        summary = (
            f"Archer Training score {self.score} | Hits {self.hits} Misses {self.misses} "
            f"Acc {accuracy*100:.1f}% | +{xp_gain} XP -{hp_cost} HP"
            + (" +1 SPD" if speed_gain else "")
        )
        return ArcherTrainingResult(
            score=self.score,
            hits=self.hits,
            misses=self.misses,
            best_combo=self.best_combo,
            accuracy=accuracy,
            focus_remaining=max(0, self.focus),
            success=success,
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
            pass

    def _c(self, pair_id: int) -> int:
        if not curses.has_colors():
            return 0
        return curses.color_pair(pair_id)

    def _unicode_ok(self) -> bool:
        return self._unicode_ui


def start_archer_training(stdscr: curses.window, player: Player) -> ArcherTrainingResult:
    return ArcherTrainer(stdscr, player).run()
