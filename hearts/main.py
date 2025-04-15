from game import Game
from players import RandomPlayer, SimplePlayer
import random

random.seed(42)

if __name__ == "__main__":
    game = Game(
        # players=[RandomPlayer(f"Random {i}") for i in range(1, 4)]
        # + [SimplePlayer("Simple 1")],
        players=[SimplePlayer(f"Simple {i + 1}") for i in range(4)],
        max_points=100,
    )
    game.play()
