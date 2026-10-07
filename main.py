"""Run with python main.py. All artwork is drawn with Tkinter."""
import json
import ctypes
import math
from pathlib import Path
import random
import sys
import time
import tkinter as tk

from game import Game, DIRECTIONS, DIFFICULTIES

WIDTH, HEIGHT = 1100, 790
CELL, COLS, ROWS = 24, 28, 24
BX, BY = 44, 152
BG, PANEL, INK = "#07151d", "#102630", "#e4f6ee"
MUTED, GOLD, ORANGE = "#8aa9ad", "#ffd166", "#ff963b"
SAVE = Path(__file__).resolve().with_name("high_score.json")


class DragonSnake:
    def __init__(self, root):
        self.root = root
        root.title("Dragon Snake • A Dragon Ball fan game")
        root.resizable(False, False)
        root.configure(bg=BG)
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=BG,
                                highlightthickness=0)
        self.canvas.pack()
        self.best = self.load_best()
        self.difficulty = "WARRIOR"
        self.game = Game(self.difficulty)
        self.state = "menu"
        self.buttons = []
        self.accumulator = 0.0
        self.previous = time.monotonic()
        self.flash = 0
        self.save_error = False
        self.stars = [(random.Random(i).randrange(WIDTH),
                       random.Random(i + 600).randrange(HEIGHT), i % 3 + 1)
                      for i in range(70)]
        root.bind("<KeyPress>", self.key)
        self.canvas.bind("<Button-1>", self.click)
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.loop()

    def load_best(self):
        try:
            value = json.loads(SAVE.read_text(encoding="utf-8")).get("best", 0)
            return max(0, value) if isinstance(value, int) else 0
        except (OSError, ValueError, AttributeError):
            return 0

    def save_best(self):
        if self.game.score > self.best:
            self.best = self.game.score
            try:
                temporary = SAVE.with_suffix(".tmp")
                temporary.write_text(json.dumps({"best": self.best}), encoding="utf-8")
                temporary.replace(SAVE)
            except OSError:
                self.save_error = True

    def close(self):
        self.save_best()
        self.root.destroy()

    def start(self):
        self.save_best()
        self.game = Game(self.difficulty)
        self.state = "playing"
        self.accumulator = 0
        self.previous = time.monotonic()

    def key(self, event):
        key = event.keysym.lower()
        direction = {"w": "Up", "s": "Down", "a": "Left", "d": "Right",
                     "up": "Up", "down": "Down", "left": "Left", "right": "Right"}
        if key in direction and self.state == "playing":
            self.game.turn(DIRECTIONS[direction[key]])
        elif key in ("return", "space") and self.state in ("menu", "over"):
            self.start()
        elif key in ("space", "p") and self.state in ("playing", "paused"):
            self.state = "paused" if self.state == "playing" else "playing"
            self.accumulator = 0
        elif key == "r":
            self.start()
        elif key == "escape":
            self.menu()

    def click(self, event):
        for x1, y1, x2, y2, callback in self.buttons:
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                callback()
                break

    def text(self, x, y, text, size=12, color=INK, weight="normal", anchor="nw"):
        return self.canvas.create_text(x, y, text=text, fill=color, anchor=anchor,
                                       font=("Segoe UI", -round(size * 4 / 3), weight))

    def box(self, x1, y1, x2, y2, fill=PANEL, outline="", width=1):
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill,
                                     outline=outline, width=width)

    def button(self, x, y, w, label, callback, selected=False):
        self.box(x, y, x + w, y + 42, GOLD if selected else "#183843",
                 GOLD if selected else "#31535a")
        self.text(x + w / 2, y + 21, label, 10, BG if selected else INK,
                  "bold", "center")
        self.buttons.append((x, y, x + w, y + 42, callback))

    def ball(self, x, y, number, radius=10, dim=False):
        c = self.canvas
        c.create_oval(x-radius-3, y-radius-3, x+radius+3, y+radius+3,
                      fill="#3c3824" if dim else "#644524", outline="")
        c.create_oval(x-radius, y-radius, x+radius, y+radius,
                      fill="#454531" if dim else ORANGE,
                      outline="#697153" if dim else GOLD, width=1)
        if not dim:
            c.create_oval(x-radius*.6, y-radius*.65, x-radius*.1, y-radius*.25,
                          fill="#ffe4a3", outline="")
        positions = {1: [(0, 0)], 2: [(-.3, 0), (.3, 0)],
                     3: [(0, -.3), (-.3, .22), (.3, .22)],
                     4: [(-.3, -.3), (.3, -.3), (-.3, .3), (.3, .3)],
                     5: [(-.4, -.4), (.4, -.4), (0, 0), (-.4, .4), (.4, .4)],
                     6: [(-.4, -.4), (0, -.4), (.4, -.4), (-.4, .4), (0, .4), (.4, .4)],
                     7: [(-.4, -.4), (0, -.4), (.4, -.4), (0, 0), (-.4, .4), (0, .4), (.4, .4)]}
        for ox, oy in positions[number]:
            sx, sy = x + ox*radius, y + oy*radius
            points = []
            for i in range(10):
                angle = -math.pi/2 + i*math.pi/5
                r = radius * (.19 if i % 2 == 0 else .08)
                points.extend((sx + math.cos(angle)*r, sy + math.sin(angle)*r))
            c.create_polygon(points, fill="#62583d" if dim else "#b73425", outline="")

    def background(self):
        c = self.canvas
        for x, y, r in self.stars:
            c.create_oval(x, y, x+r, y+r, fill="#20404a", outline="")
        c.create_oval(938, -75, 1205, 190, fill="#173c3e", outline="#295454", width=2)
        c.create_oval(979, -28, 1138, 132, fill="#1c4844", outline="")
        self.text(44, 24, "DRAGON", 30, INK, "bold")
        self.text(228, 24, "SNAKE", 30, GOLD, "bold")
        self.text(46, 76, "NAMEK ARENA  /  THE SEVEN-BALL CHALLENGE", 10, MUTED, "bold")
        self.box(44, 117, 62, 120, ORANGE)
        self.text(72, 108, "FAN-MADE ARCADE", 9, MUTED, "bold")
        self.text(1058, 44, "龍", 30, GOLD, "bold", "ne")
        self.text(1058, 90, "TRAIN. COLLECT. TRANSFORM.", 9, MUTED, anchor="ne")

    def arena(self):
        c = self.canvas
        powered = self.game.boost > 0
        self.box(BX-3, BY-3, BX+COLS*CELL+3, BY+ROWS*CELL+3,
                 "#17322c", GOLD if powered else "#355c55", 2)
        self.box(BX, BY, BX+COLS*CELL, BY+ROWS*CELL, "#0c2427")
        c.create_oval(BX+465, BY+48, BX+540, BY+123, fill="#173a36", outline="")
        c.create_polygon(BX, BY+440, BX+90, BY+360, BX+174, BY+422,
                         BX+268, BY+341, BX+400, BY+470, BX+540, BY+374,
                         BX+672, BY+440, BX+672, BY+576, BX, BY+576,
                         fill="#103033", outline="")
        for x in range(COLS+1):
            c.create_line(BX+x*CELL, BY, BX+x*CELL, BY+ROWS*CELL, fill="#153335")
        for y in range(ROWS+1):
            c.create_line(BX, BY+y*CELL, BX+COLS*CELL, BY+y*CELL, fill="#153335")
        if self.game.food:
            x, y = self.game.food
            self.ball(BX+x*CELL+12, BY+y*CELL+12, self.game.ball_number)
        if self.game.bean:
            x, y = self.game.bean
            px, py = BX+x*CELL+12, BY+y*CELL+12
            c.create_oval(px-9, py-7, px+9, py+7, fill="#9de67d", outline="#ddffc5", width=2)
            c.create_line(px-2, py-5, px-4, py, px+1, py+4, fill="#46845a", smooth=True, width=2)
        for i, (x, y) in reversed(list(enumerate(self.game.snake))):
            px, py = BX+x*CELL, BY+y*CELL
            color = ("#f5c752" if i % 2 else "#ffe187") if powered else ("#45b98d" if i % 2 else "#64d9a3")
            if powered:
                c.create_oval(px-3, py-3, px+27, py+27, outline="#7a713b", width=2)
            c.create_rectangle(px+3, py+3, px+21, py+21, fill=color, outline="")
            if i:
                c.create_line(px+8, py+8, px+15, py+8, fill="#baf5c6" if not powered else "#fff2ba", width=2)
        hx, hy = self.game.snake[0]
        px, py = BX+hx*CELL+12, BY+hy*CELL+12
        dx, dy = self.game.direction
        for sign in (-1, 1):
            ex, ey = px+dx*4-dy*sign*5, py+dy*4+dx*sign*5
            c.create_oval(ex-2, ey-2, ex+2, ey+2, fill="#122c2b", outline="")
        for sign in (-1, 1):
            ox, oy = px-dx*7-dy*sign*7, py-dy*7+dx*sign*7
            c.create_line(ox, oy, ox-dx*5-dy*sign*3, oy-dy*5+dx*sign*3, fill=GOLD, width=3)

    def sidebar(self):
        g = self.game
        x = 748
        self.box(x, 152, 1058, 261)
        self.text(x+20, 170, "POWER LEVEL", 10, MUTED, "bold")
        self.text(x+20, 190, f"{g.score:05d}", 32, GOLD, "bold")
        self.text(1038, 177, "BEST", 9, MUTED, anchor="ne")
        self.text(1038, 198, f"{max(self.best, g.score):05d}", 15, INK, "bold", "ne")
        self.box(x, 277, 1058, 396)
        self.text(x+20, 294, "SUMMON SHENRON", 11, INK, "bold")
        count = g.collected % 7
        for i in range(7):
            self.ball(x+28+i*42, 342, i+1, 13, i >= count)
        self.text(x+20, 373, f"{count} / 7 collected     •     Wishes: {g.wishes}", 10, MUTED)
        self.box(x, 412, 1058, 524)
        self.text(x+20, 429, "SUPER SAIYAN" if g.boost else "KI RESERVE", 11,
                  GOLD if g.boost else INK, "bold")
        self.text(x+20, 456, f"{g.boost:.1f}s  •  SCORE x2" if g.boost else "Gather seven balls to transform", 11, MUTED)
        self.box(x+20, 489, 1038, 496, "#203e43")
        fraction = g.boost/10 if g.boost else count/7
        if fraction:
            self.box(x+20, 489, x+20+270*fraction, 496, GOLD if g.boost else "#58c79b")
        self.box(x, 540, 1058, 728)
        self.text(x+20, 557, "CAPSULE CORP. FIELD GUIDE", 10, INK, "bold")
        self.text(x+20, 586, "ARROWS / WASD     Move\nSPACE / P                 Pause\nR                                 Restart\nESC                            Main menu", 11, MUTED)
        self.text(x+20, 689, "Senzu: +50  •  Walls wrap in SSJ", 10, GOLD)
        self.text(44, 754, g.message, 11, GOLD if g.boost else MUTED)
        self.text(1058, 754, "BEST NOT SAVED" if self.save_error else self.difficulty,
                  10, MUTED, "bold", "ne")

    def overlay(self):
        x, y, w, h = 112, 268, 536, 336
        self.box(x-5, y-5, x+w+5, y+h+5, "#07151d", "#345953", 2)
        self.box(x, y, x+w, y+h, "#102a30")
        cx = x+w/2
        if self.state == "menu":
            self.text(cx, y+27, "AWAKEN YOUR DRAGON", 23, GOLD, "bold", "n")
            self.text(cx, y+74, "Guide Shenron through the skies of Namek.", 12, INK, anchor="n")
            self.text(cx, y+104, "Collect 7 Dragon Balls to unlock 10 seconds of\nSuper Saiyan: golden aura, wall wrapping & double points.", 11, MUTED, anchor="n")
            for i, name in enumerate(DIFFICULTIES):
                self.button(x+26+i*164, y+170, 156, name,
                            lambda n=name: setattr(self, "difficulty", n), self.difficulty == name)
            self.button(x+100, y+235, 336, "START TRAINING   →", self.start, True)
            self.text(cx, y+299, "ENTER TO START  •  ARROWS OR WASD TO MOVE", 9, MUTED, anchor="n")
        elif self.state == "paused":
            self.text(cx, y+51, "MEDITATION BREAK", 25, GOLD, "bold", "n")
            self.text(cx, y+111, "Your training will be here when you're ready.", 12, MUTED, anchor="n")
            self.button(x+100, y+184, 336, "RESUME   /   SPACE", lambda: setattr(self, "state", "playing"), True)
            self.button(x+100, y+240, 336, "MAIN MENU", self.menu)
        else:
            self.text(cx, y+34, "LEGENDARY VICTORY" if self.game.won else "TRAINING COMPLETE", 24, GOLD, "bold", "n")
            self.text(cx, y+85, self.game.message, 12, MUTED, anchor="n")
            self.text(cx, y+123, f"POWER LEVEL  {self.game.score:05d}", 24, INK, "bold", "n")
            self.button(x+100, y+194, 336, "TRAIN AGAIN   /   ENTER", self.start, True)
            self.button(x+100, y+250, 336, "MAIN MENU", self.menu)

    def menu(self):
        self.save_best()
        self.state = "menu"

    def loop(self):
        now = time.monotonic()
        dt, self.previous = min(now-self.previous, .25), now
        if self.state == "playing":
            self.accumulator += dt
            while self.accumulator >= self.game.interval:
                self.accumulator -= self.game.interval
                event = self.game.step()
                if event in ("food", "power", "bean"):
                    self.flash = 0.25
                if event in ("crash", "win"):
                    self.save_best()
                    self.state = "over"
                    break
        self.flash = max(0, self.flash-dt)
        self.canvas.delete("all")
        self.buttons = []
        self.background()
        self.arena()
        self.sidebar()
        if self.flash:
            self.canvas.create_rectangle(BX-5, BY-5, BX+COLS*CELL+5,
                                         BY+ROWS*CELL+5, outline=GOLD, width=3)
        if self.state != "playing":
            self.overlay()
        self.root.after(33, self.loop)


def configure_display():
    """Keep the arena sharp and fully visible on scaled Windows displays."""
    if sys.platform == "win32":
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except (AttributeError, OSError):
            pass


if __name__ == "__main__":
    configure_display()
    root = tk.Tk()
    DragonSnake(root)
    root.mainloop()
