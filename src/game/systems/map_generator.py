import random

TILE_FLOOR = 0
TILE_WALL = 1
TILE_DOOR = 9


class DungeonMap:
    def __init__(self) -> None:
        self.rooms: list[list[int]] = []
        self.corridors: list[list[int]] = []
        self.grid: list[list[int]] = []
        self.width = 0
        self.height = 0

    def generate(
        self,
        width: int = 46,
        height: int = 22,
        fail_limit: int = 110,
        corridor_percent: int = 50,
        max_rooms: int = 60,
    ) -> list[list[int]]:
        self.width = width
        self.height = height
        self.rooms = []
        self.corridors = []
        self.grid = [[TILE_WALL for _ in range(width)] for _ in range(height)]

        room_w, room_h, room_type = self._make_room()
        while not self.rooms:
            y = random.randrange(height - 1 - room_h) + 1
            x = random.randrange(width - 1 - room_w) + 1
            self._place_feature(room_h, room_w, x, y, width, height, room_type, 0)

        failed = 0
        while failed < fail_limit:
            room_index = random.randrange(len(self.rooms))
            ex, ey, ex2, ey2, exit_type = self._make_exit(room_index)
            feature_roll = random.randrange(100)
            if feature_roll < corridor_percent:
                feat_w, feat_h, feat_type = self._make_corridor()
            else:
                feat_w, feat_h, feat_type = self._make_room()

            placed = self._place_feature(
                feat_h,
                feat_w,
                ex2,
                ey2,
                width,
                height,
                feat_type,
                exit_type,
            )
            if placed == 0:
                failed += 1
            elif placed == 2:
                if self.grid[ey2][ex2] == TILE_FLOOR and random.randrange(100) < 7:
                    self._make_portal(ex, ey)
                failed += 1
            else:
                self._make_portal(ex, ey)
                failed = 0
                if feat_type < 5:
                    corridor_data = [len(self.rooms) - 1, ex2, ey2, feat_type]
                    self.corridors.append(corridor_data)
                    self._join_corridor(len(self.rooms) - 1, ex2, ey2, feat_type, 50)

            if len(self.rooms) >= max_rooms:
                break

        self._final_joins()
        self._normalize_walkable_tiles()
        self._ensure_full_connectivity()
        return self.grid

    def random_floor_tile(self) -> tuple[int, int]:
        while True:
            y = random.randrange(1, self.height - 1)
            x = random.randrange(1, self.width - 1)
            if self.grid[y][x] == TILE_FLOOR:
                return x, y

    def _make_room(self) -> tuple[int, int, int]:
        return random.randrange(8) + 3, random.randrange(8) + 3, 5

    def _make_corridor(self) -> tuple[int, int, int]:
        length = random.randrange(18) + 3
        heading = random.randrange(4)
        if heading == 0:
            return 1, -length, heading
        if heading == 1:
            return length, 1, heading
        if heading == 2:
            return 1, length, heading
        return -length, 1, heading

    def _place_feature(
        self,
        length: int,
        width: int,
        x: int,
        y: int,
        max_x: int,
        max_y: int,
        feature_type: int,
        exit_type: int,
    ) -> int:
        if length < 0:
            y += length + 1
            length = abs(length)
        if width < 0:
            x += width + 1
            width = abs(width)

        if feature_type == 5:
            if exit_type in (0, 2):
                x -= random.randrange(width)
            else:
                y -= random.randrange(length)

        if width + x + 1 > max_x - 1 or length + y + 1 > max_y or x < 1 or y < 1:
            return 0

        can_place = 1
        for j in range(length):
            for k in range(width):
                if self.grid[y + j][x + k] != TILE_WALL:
                    can_place = 2

        if can_place == 1:
            self.rooms.append([length, width, x, y])
            for j in range(length + 2):
                for k in range(width + 2):
                    self.grid[(y - 1) + j][(x - 1) + k] = 2
            for j in range(length):
                for k in range(width):
                    self.grid[y + j][x + k] = TILE_FLOOR
        return can_place

    def _make_exit(self, room_index: int) -> tuple[int, int, int, int, int]:
        room = self.rooms[room_index]
        while True:
            wall = random.randrange(4)
            if wall == 0:
                rx = random.randrange(room[1]) + room[2]
                ry = room[3] - 1
                rx2, ry2 = rx, ry - 1
            elif wall == 1:
                ry = random.randrange(room[0]) + room[3]
                rx = room[2] + room[1]
                rx2, ry2 = rx + 1, ry
            elif wall == 2:
                rx = random.randrange(room[1]) + room[2]
                ry = room[3] + room[0]
                rx2, ry2 = rx, ry + 1
            else:
                ry = random.randrange(room[0]) + room[3]
                rx = room[2] - 1
                rx2, ry2 = rx - 1, ry

            if self.grid[ry][rx] == 2:
                return rx, ry, rx2, ry2, wall

    def _make_portal(self, px: int, py: int) -> None:
        roll = random.randrange(100)
        if roll > 90:
            self.grid[py][px] = 5
        elif roll > 75:
            self.grid[py][px] = 4
        elif roll > 40:
            self.grid[py][px] = 3
        else:
            self.grid[py][px] = TILE_FLOOR

    def _join_corridor(self, corridor_index: int, x: int, y: int, direction: int, chance: int) -> None:
        corridor = self.rooms[corridor_index]
        if x != corridor[2] or y != corridor[3]:
            end_x = x - (corridor[1] - 1)
            end_y = y - (corridor[0] - 1)
        else:
            end_x = x + (corridor[1] - 1)
            end_y = y + (corridor[0] - 1)

        exits: list[list[int]] = []
        if direction == 0:
            if end_x > 1:
                exits.append([end_x - 2, end_y, end_x - 1, end_y])
            if end_y > 1:
                exits.append([end_x, end_y - 2, end_x, end_y - 1])
            if end_x < self.width - 2:
                exits.append([end_x + 2, end_y, end_x + 1, end_y])
        elif direction == 1:
            if end_y > 1:
                exits.append([end_x, end_y - 2, end_x, end_y - 1])
            if end_x < self.width - 2:
                exits.append([end_x + 2, end_y, end_x + 1, end_y])
            if end_y < self.height - 2:
                exits.append([end_x, end_y + 2, end_x, end_y + 1])
        elif direction == 2:
            if end_x < self.width - 2:
                exits.append([end_x + 2, end_y, end_x + 1, end_y])
            if end_y < self.height - 2:
                exits.append([end_x, end_y + 2, end_x, end_y + 1])
            if end_x > 1:
                exits.append([end_x - 2, end_y, end_x - 1, end_y])
        else:
            if end_x > 1:
                exits.append([end_x - 2, end_y, end_x - 1, end_y])
            if end_y > 1:
                exits.append([end_x, end_y - 2, end_x, end_y - 1])
            if end_y < self.height - 2:
                exits.append([end_x, end_y + 2, end_x, end_y + 1])

        for ex, ey, px, py in exits:
            if self.grid[ey][ex] == TILE_FLOOR and random.randrange(100) < chance:
                self._make_portal(px, py)

    def _final_joins(self) -> None:
        for corridor_index, x, y, direction in self.corridors:
            self._join_corridor(corridor_index, x, y, direction, 10)

    def _normalize_walkable_tiles(self) -> None:
        # Portal variants produced by the original algorithm are walkable for gameplay.
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] in (3, 4, 5):
                    self.grid[y][x] = TILE_FLOOR

    def _ensure_full_connectivity(self) -> None:
        components = self._floor_components()
        if len(components) <= 1:
            return

        main_component = max(components, key=len)
        for component in components:
            if component is main_component:
                continue
            a, b = self._nearest_cells(main_component, component)
            self._carve_l_corridor(a, b)
            main_component = main_component | component

    def _floor_components(self) -> list[set[tuple[int, int]]]:
        visited: set[tuple[int, int]] = set()
        components: list[set[tuple[int, int]]] = []

        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] != TILE_FLOOR or (x, y) in visited:
                    continue
                stack = [(x, y)]
                comp: set[tuple[int, int]] = set()
                visited.add((x, y))
                while stack:
                    cx, cy = stack.pop()
                    comp.add((cx, cy))
                    for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                        if not (0 <= nx < self.width and 0 <= ny < self.height):
                            continue
                        if self.grid[ny][nx] != TILE_FLOOR or (nx, ny) in visited:
                            continue
                        visited.add((nx, ny))
                        stack.append((nx, ny))
                components.append(comp)
        return components

    def _nearest_cells(
        self,
        comp_a: set[tuple[int, int]],
        comp_b: set[tuple[int, int]],
    ) -> tuple[tuple[int, int], tuple[int, int]]:
        best_a = next(iter(comp_a))
        best_b = next(iter(comp_b))
        best_dist = abs(best_a[0] - best_b[0]) + abs(best_a[1] - best_b[1])

        for ax, ay in comp_a:
            for bx, by in comp_b:
                dist = abs(ax - bx) + abs(ay - by)
                if dist < best_dist:
                    best_dist = dist
                    best_a = (ax, ay)
                    best_b = (bx, by)
        return best_a, best_b

    def _carve_l_corridor(self, start: tuple[int, int], end: tuple[int, int]) -> None:
        sx, sy = start
        ex, ey = end

        x = sx
        while x != ex:
            self.grid[sy][x] = TILE_FLOOR
            x += 1 if ex > x else -1
        self.grid[sy][ex] = TILE_FLOOR

        y = sy
        while y != ey:
            self.grid[y][ex] = TILE_FLOOR
            y += 1 if ey > y else -1
        self.grid[ey][ex] = TILE_FLOOR


def render_map(
    grid: list[list[int]],
    player_pos: tuple[int, int],
    exit_pos: tuple[int, int],
) -> str:
    player_x, player_y = player_pos
    exit_x, exit_y = exit_pos
    rows: list[str] = []
    for y, row in enumerate(grid):
        chars: list[str] = []
        for x, tile in enumerate(row):
            if (x, y) == (player_x, player_y):
                chars.append("@")
            elif (x, y) == (exit_x, exit_y):
                chars.append(">")
            elif tile == TILE_FLOOR:
                chars.append(".")
            else:
                chars.append("#")
        rows.append("".join(chars))
    return "\n".join(rows)
