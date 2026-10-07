# Dragon Snake

A Dragon Ball themed Python snake game with a miniature Shenron, a Namek arena,
seven collectible Dragon Balls, and a golden Super Saiyan transformation.
All artwork is drawn in code. No pip packages or downloaded assets are needed.

## Play

On Windows, right-click `play.ps1` and choose **Run with PowerShell**, or run:

```powershell
powershell -ExecutionPolicy Bypass -File .\play.ps1
```

The launcher finds Python with Tkinter, including the bundled Codex runtime on
this machine. With a standard Python 3.10+ installation, you can also run:

```sh
python main.py
```

Tkinter is included in the standard Windows/macOS Python installer. On
Ubuntu/Debian, install `python3-tk` if needed and use `python3 main.py`.

## Controls

| Key | Action |
| --- | --- |
| Arrows / WASD | Move |
| Enter | Start / play again |
| Space / P | Pause / resume |
| R | Restart |
| Escape | Main menu |

Choose Training, Warrior, or Legend on the title screen. Dragon Balls grow your
dragon and award 10 points. Each set of seven unlocks 10 seconds of Super Saiyan:
wrap through arena edges and earn double points. Your own body still causes a
collision. Each completed set slightly increases movement speed. Senzu Beans
appear every five balls, last eight seconds, and award 50 points (100 during
Super Saiyan). Filling the arena wins. Timers stop while paused.

Best scores are saved in `high_score.json` beside the game. The game remains
playable if saving is unavailable. The window needs about 1100 x 790 pixels.

## Verify rules

```sh
python -m unittest discover -s tests -v
```

An unofficial fan project with original procedural artwork and no bundled
Dragon Ball media. Dragon Ball belongs to its respective rights holders.
