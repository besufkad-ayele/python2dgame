# Ball Catch Game (Python)

A simple 2D ball-catching arcade game built with Python and John Zelle's `graphics.py` library. The game includes a main menu, instructions, settings, and player customization.

## Requirements
- Python 3.10+ (Windows recommended; uses `winsound` for beeps)
- pip
- `graphics.py` (John Zelle) installed from PyPI: `pip install graphics.py`

## Setup
1) Install Python from https://www.python.org and verify: `python --version`.
2) Clone or download this repository, then open a terminal in the project root.
3) Create a virtual environment (recommended):
	- Windows PowerShell: `python -m venv .venv` then `./.venv/Scripts/Activate.ps1`
4) Install the dependency: `pip install graphics.py`
5) Run the game: `python src/main.py`

## How to Play
- Menu: press number keys (1 Play, 2 Instructions, 3 Change Player, 4 Settings, 5 Exit).
- Movement: Left and Right arrows to move.
- Pause: Space to pause/resume.
- Quit to menu during play: Q.
- Objective: catch the falling ball before it hits the ground.
- Chances: each drop consumes one chance; catching the ball adds three chances and advances the level.
- Levels and speed: every catch increases level and ball speed (larger steps on harder difficulties).
- Scoring: each catch awards `level * 10` points. Game over when chances reach zero.

## Settings and Customization
- Settings menu: toggle sound and music, cycle shirt color, cycle pants color, and change difficulty (easy, normal, hard).
- Change Player menu: cycle shirt and pants colors with keys 1 and 2; a preview updates live.
- Sound uses system beeps; if unavailable on your OS, disable sound in the Settings menu.

## File Overview
- assets/: images and sounds (if used)
- config/constant.py: game constants
- src/game.py: core game logic and UI
- src/main.py: entry point
- src/player.py, src/ball.py, src/goal.py: legacy components (the game uses src/game.py)
- utils/helper.py: utility helpers