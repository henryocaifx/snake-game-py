"""Dragon Snake rules, independent of the graphical interface."""
from collections import deque
import random

DIFFICULTIES = {"TRAINING": 0.16, "WARRIOR": 0.12, "LEGEND": 0.085}
DIRECTIONS = {"Up": (0, -1), "Down": (0, 1), "Left": (-1, 0), "Right": (1, 0)}


class Game:
    def __init__(self, difficulty="WARRIOR", rng=None, cols=28, rows=24):
        self.rng = rng or random.Random()
        self.cols, self.rows = cols, rows
        self.difficulty = difficulty
        x, y = cols // 2, rows // 2
        self.snake = deque([(x, y), (x - 1, y), (x - 2, y)])
        self.direction = (1, 0)
        self.pending = None
        self.score = self.collected = self.wishes = 0
        self.boost = 0.0
        self.bean = None
        self.bean_time = 0.0
        self.alive = True
        self.won = False
        self.food = self.empty_cell()
        self.message = "Collect all seven Dragon Balls!"

    @property
    def interval(self):
        return max(0.055, DIFFICULTIES[self.difficulty] - self.wishes * 0.008)

    @property
    def ball_number(self):
        return self.collected % 7 + 1

    def empty_cell(self):
        occupied = set(self.snake)
        occupied.update(p for p in (getattr(self, "food", None), self.bean) if p is not None)
        free = [(x, y) for y in range(self.rows) for x in range(self.cols)
                if (x, y) not in occupied]
        return self.rng.choice(free) if free else None

    def turn(self, direction):
        if self.pending is None and direction != (-self.direction[0], -self.direction[1]):
            self.pending = direction

    def step(self):
        if not self.alive or self.won:
            return "idle"
        powered = self.boost > 0
        self.boost = max(0.0, self.boost - self.interval)
        if powered and self.boost == 0:
            self.message = "Transformation ended. Gather the next seven balls!"
        self.bean_time = max(0.0, self.bean_time - self.interval)
        if self.bean_time == 0:
            self.bean = None
        if self.pending is not None:
            self.direction, self.pending = self.pending, None
        x, y = self.snake[0]
        dx, dy = self.direction
        head = (x + dx, y + dy)
        if powered:
            head = (head[0] % self.cols, head[1] % self.rows)
        elif not (0 <= head[0] < self.cols and 0 <= head[1] < self.rows):
            self.alive = False
            self.message = "You hit the arena boundary."
            return "crash"
        eating = head == self.food
        # The tail vacates its cell on moves that do not grow the snake.
        body = list(self.snake) if eating else list(self.snake)[:-1]
        if head in body:
            self.alive = False
            self.message = "Your dragon crossed its own path."
            return "crash"
        self.snake.appendleft(head)
        if not eating:
            self.snake.pop()
        event = "move"
        if head == self.bean:
            bonus = 50 * (2 if powered else 1)
            self.score += bonus
            self.bean = None
            self.message = f"Senzu Bean! Bonus energy +{bonus}"
            event = "bean"
        if eating:
            self.score += 10 * (2 if powered else 1)
            self.collected += 1
            self.food = None
            event = "food"
            if self.collected % 7 == 0:
                self.wishes += 1
                self.boost = 10.0
                self.message = "SUPER SAIYAN! Wrap through walls. Score x2."
                event = "power"
            else:
                self.message = f"Dragon Ball {self.collected % 7}/7 collected!"
            if len(self.snake) == self.cols * self.rows:
                self.won = True
                self.message = "The arena is yours. Legendary victory!"
                return "win"
            self.food = self.empty_cell()
            # Dragon Balls take priority when a bean occupies the last free cell.
            if self.food is None and self.bean is not None:
                self.bean = None
                self.bean_time = 0
                self.food = self.empty_cell()
            if self.collected % 5 == 0 and self.bean is None:
                self.bean = self.empty_cell()
                self.bean_time = 8.0
        return event
