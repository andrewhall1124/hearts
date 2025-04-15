import argparse
import yaml
from rich import print
from hearts import Game, Player, SimplePlayer, RandomPlayer
from dataclasses import dataclass
import random


def create_player(type: str, name: str) -> Player:
    match type:
        case "simple":
            return SimplePlayer(name)

        case "random":
            return RandomPlayer(name)
        
        case _:
            raise NotImplementedError(f"{type} player is not implemented.")
        
@dataclass
class ExperimentConfig:
    name: str
    seed: int
    players: list[dict[str, str]]
    games: int
    max_points: int


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Experiment executor")
    parser.add_argument(
        "--config", type=str, required=True, help="Path to .yaml config file."
    )
    args = parser.parse_args()

    with open(args.config, "r") as file:
        config = ExperimentConfig(**yaml.safe_load(file))

        random.seed(config.seed)

        players = [
            create_player(**player_config) for player_config in config.players
        ]

        for i in range(config.games):
            game = Game(
                players=players,
                max_points=config.max_points
            )
            game.play()
