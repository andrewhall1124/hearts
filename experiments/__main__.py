import argparse
import yaml
from rich import print
from hearts.game import Game
from hearts.players import Player, SluffingPlayer, RandomPlayer, MinCardPlayer, MinMaxCardPlayer, MCTSPlayer
from dataclasses import dataclass
import random
import polars as pl
import os


def create_player(type: str, name: str) -> Player:
    match type:
        case "sluffing":
            return SluffingPlayer(name)

        case "random":
            return RandomPlayer(name)
        
        case "min":
            return MinCardPlayer(name)
        
        case "minmax":
            return MinMaxCardPlayer(name)
        
        case "mcts":
            return MCTSPlayer(name)

        case _:
            raise NotImplementedError(f"{type} player is not implemented.")


@dataclass
class ExperimentConfig:
    name: str
    seed: int
    players: list[dict[str, str]]
    games: int
    max_points: int

@dataclass
class Results:
    game_name: str
    player_scores: list[dict]

    def __repr__(self) -> str:
        results_str ="\n" +  "-"* 5 + f" {self.game_name} " + "-" * 5
        for player_score in self.player_scores:
            player = player_score['player']
            score = player_score['score']
            results_str += f"\n{player}: {score}"

        return results_str

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Experiment executor")
    parser.add_argument(
        "--config", type=str, required=True, help="Path to .yaml config file."
    )
    args = parser.parse_args()

    with open(args.config, "r") as file:
        config = ExperimentConfig(**yaml.safe_load(file))

        random.seed(config.seed)

        players = [create_player(**player_config) for player_config in config.players]

        results_list = []
        for i in range(config.games):
            game_name = f"{config.name} {i + 1}"
            game = Game(players=players, max_points=config.max_points, print_scores=True)

            results = Results(
                game_name=game_name,
                player_scores=game.play()
            )
            print(results)

            results_list.append(results)

        results_dicts = [
            {
                "game_name": results.game_name,
                **player_score
            }
            for results in results_list
            for player_score in results.player_scores
        ]
        
        df = pl.from_dicts(results_dicts)

        
        os.makedirs("results", exist_ok=True)
        df.write_parquet(f"results/{game_name.lower().replace(' ', '_')}.parquet")
            
