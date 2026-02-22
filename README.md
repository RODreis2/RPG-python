# Terminal Realms (Python Curses RPG)

A terminal-based RPG built with Python and `curses`.

## Requirements

- Python 3.11+
- A terminal that supports curses (Linux/macOS terminal, WSL terminal, etc.)

## Run

From the project root:

```bash
python main.py
```

## Game Flow

1. Start menu -> `Create Character`
2. Choose class (`Warrior`, `Mage`, `Archer`)
3. Enter the main loop:
   - `Dungeon`
   - `Market`
   - `Training`
   - `Status`

## Controls

### Menus

- Move selection: `W/S` or `Arrow Up/Down`
- Confirm: `Enter`

### Class selection (mouse enabled)

- Hover a class to preview its ASCII art
- Left-click to select class
- Keyboard navigation also works

### Dungeon

- Move: `W/A/S/D` or arrow keys
- Leave dungeon: `Q` or `Esc`
- Door tile: `D` (reach it to clear dungeon level)

### Combat

- Move action selector: `W/A/S/D` or arrow keys
- Confirm action: `Enter`
- Actions: `Attack`, `Skill`, `Item`, `Run`

### Typewriter text

- Animated text appears in dialogs/events/combat log
- Press `Enter` to skip current typing burst

## Progression and Difficulty

- Dungeon level starts at `1`
- Each time you clear a dungeon (reach `D`), dungeon level increases by `1`
- Every 5 dungeon levels, enemies scale up:
  - HP: +15% per tier
  - Damage: +10% per tier

## Dungeon Generation

- Procedural room/corridor generation
- Connectivity enforcement ensures all floor regions are reachable

## Data Files

- `data/stores/monsters.json` - monster templates
- `data/stores/skills.json` - class skills
- `data/stores/potions.json` - shop potions
- `data/stores/weapons.json` - weapon catalog (currently informational)
- `resources/opening_text.json` - opening lines

## Troubleshooting

- If the UI looks broken, enlarge your terminal window.
- If colors don't appear, your terminal may not support full color pairs.
- For best results, run in a local terminal (not minimal CI shell emulators).
