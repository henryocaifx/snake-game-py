from collections import deque
import random
import unittest

from game import Game


class GameRules(unittest.TestCase):
    def setUp(self):
        self.game = Game(rng=random.Random(42))

    def test_reverse_and_multiple_inputs_cannot_reverse_snake(self):
        g = self.game
        g.turn((-1, 0))
        self.assertIsNone(g.pending)
        g.turn((0, -1))
        g.turn((-1, 0))
        g.step()
        self.assertEqual(g.direction, (0, -1))
        self.assertTrue(g.alive)

    def test_food_grows_and_seventh_ball_transforms(self):
        g = self.game
        g.collected = 6
        x, y = g.snake[0]
        g.food = (x+1, y)
        self.assertEqual(g.step(), "power")
        self.assertEqual(len(g.snake), 4)
        self.assertEqual(g.wishes, 1)
        self.assertEqual(g.boost, 10)
        self.assertNotIn(g.food, g.snake)

    def test_wall_collision_and_powered_wrapping(self):
        g = self.game
        g.snake = deque([(27, 5), (26, 5), (25, 5)])
        self.assertEqual(g.step(), "crash")
        g.alive = True
        g.boost = 1
        self.assertEqual(g.step(), "move")
        self.assertEqual(g.snake[0], (0, 5))

    def test_tail_cell_is_safe_but_body_is_not(self):
        g = self.game
        g.snake = deque([(4, 4), (4, 5), (3, 5), (3, 4)])
        g.direction = (-1, 0)
        self.assertEqual(g.step(), "move")
        g.snake = deque([(4, 4), (3, 4), (3, 5), (4, 5)])
        self.assertEqual(g.step(), "crash")

    def test_powered_food_and_bean_score(self):
        g = self.game
        x, y = g.snake[0]
        g.boost = 5
        g.food = (x+1, y)
        g.step()
        self.assertEqual(g.score, 20)
        g.bean = (x+2, y)
        g.bean_time = 3
        g.step()
        self.assertEqual(g.score, 120)
        self.assertIsNone(g.bean)

    def test_bean_expires_and_spawns_without_overlap(self):
        g = self.game
        g.bean = (0, 0)
        g.bean_time = .01
        g.step()
        self.assertIsNone(g.bean)
        g.collected = 4
        x, y = g.snake[0]
        g.food = (x+1, y)
        g.step()
        self.assertIsNotNone(g.bean)
        self.assertNotIn(g.bean, g.snake)
        self.assertNotEqual(g.bean, g.food)

    def test_full_board_is_a_win(self):
        g = Game(rng=random.Random(1), cols=4, rows=2)
        g.snake = deque([(2, 0), (1, 0), (0, 0), (0, 1), (1, 1), (2, 1), (3, 1)])
        g.food = (3, 0)
        self.assertEqual(g.step(), "win")
        self.assertTrue(g.won)

    def test_bean_cannot_block_last_dragon_ball(self):
        g = Game(rng=random.Random(1), cols=4, rows=2)
        g.snake = deque([(2, 0), (1, 0), (0, 0), (0, 1), (1, 1), (2, 1)])
        g.food = (3, 0)
        g.bean = (3, 1)
        g.bean_time = 5
        g.step()
        self.assertIsNone(g.bean)
        self.assertEqual(g.food, (3, 1))


if __name__ == "__main__":
    unittest.main()
