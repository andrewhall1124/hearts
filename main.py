from game import Game
from players import RandomPlayer, SimplePlayer

if __name__ == "__main__":
    game = Game(
        players=[RandomPlayer(f"Random {i}", seed=7) for i in range(1, 4)]
        + [SimplePlayer("Simple 1")],
        max_points=100
    )
    game.play()
