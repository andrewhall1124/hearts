from hearts.card import Card
from hearts.players import Player
from hearts.deck import Deck
import numpy as np
import polars as pl
import random
import string
import os

DECK = Deck().cards


class GameLogger:
    def __init__(self, print_logs: bool = False, game_id: str | None = None) -> None:
        self.game_id = game_id or self.generate_game_id()
        self.logs = pl.DataFrame()
        self.print_logs = print_logs

    @staticmethod
    def generate_game_id(length: int = 6) -> str:
        return "".join(random.choices(string.ascii_letters + string.digits, k=length))

    @staticmethod
    def card_encoding(cards: list[Card]) -> list[int]:
        indices = [DECK.index(card) for card in cards]

        encoding = np.zeros(52, dtype=int)
        for idx in indices:
            encoding[idx] = 1

        return encoding.tolist()

    @staticmethod
    def convert_state_to_df(state: dict) -> pl.DataFrame:
        flat_dict = {
            "player_name": state["player_name"],
            "player_index": state["player_index"],
            "game_id": state["game_id"],
        }

        keys = [key for key in state.keys() if key not in flat_dict.keys()]
        for key in keys:
            for i, val in enumerate(state[key]):
                flat_dict[f"{key}_{i + 1}"] = val

        return pl.DataFrame([flat_dict])

    def log_game_state(
        self,
        player: Player,
        player_index: int,
        hand: list[Card],
        valid_cards: list[Card],
        card: Card,
        trick: list[Card],
        played_cards: list[Card],
        score: list[int],
        round_score: list[int],
    ) -> None:
        state = {
            "game_id": self.game_id,
            "player_name": player.name,
            "player_index": player_index,
            "played_cards": self.card_encoding(played_cards),
            "trick": self.card_encoding(trick),
            "hand": self.card_encoding(hand),
            "valid_cards": self.card_encoding(valid_cards),
            "card": self.card_encoding([card]),
            "score": score,
            "round_score": round_score,
        }

        state_df = self.convert_state_to_df(state)
        self.logs = pl.concat([self.logs, state_df])

    def save_logs(self) -> None:
        os.makedirs("logs", exist_ok=True)
        self.logs.write_parquet(f"logs/{self.game_id}.parquet")
