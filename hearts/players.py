from hearts.card import Card
from abc import ABC, abstractmethod
import random
from sklearn.base import BaseEstimator
import numpy as np
import joblib
import pandas as pd

SUITS = ["♣", "♦", "♠", "♥"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

CARD_TO_INDEX = {
    Card(suit, rank): i + 1 for i, (suit, rank) in enumerate(
        (s, r) for s in SUITS for r in RANKS
    )
}

INDEX_TO_CARD = {v: k for k, v in CARD_TO_INDEX.items()}


class Player(ABC):
    def __init__(self, name: str) -> None:
        self._name = name
        self._hand: list[Card] = []

    def __repr__(self):
        return self.name

    @property
    def name(self) -> str:
        return self._name

    @property
    def hand(self) -> list[Card]:
        return self._hand

    @hand.setter
    def hand(self, hand: list[Card]) -> None:
        self._hand = hand

    def get_valid_cards(self, trick: list[Card]) -> list[Card]:
        if len(trick) > 0:
            lead_suit = trick[0].suit
            valid_cards = [card for card in self._hand if card.suit == lead_suit]

            if len(valid_cards) > 0:
                return valid_cards

        return self._hand

    @abstractmethod
    def play_card(self, trick: list[Card]) -> Card:
        pass


class RandomPlayer(Player):
    def play_card(self, trick: list[Card]) -> Card:
        valid_cards = self.get_valid_cards(trick)

        random_card = random.choice(valid_cards)
        self._hand.remove(random_card)

        return random_card


class SimplePlayer(Player):
    """Play the minimum card of the lead suit. Play the max card of the non-lead suit."""

    @staticmethod
    def _get_hearts(cards: list[Card]) -> list[Card]:
        return [card for card in cards if card.suit == "♥" or card == Card("♠", "Q")]

    def play_card(self, trick: list[Card]) -> Card:
        valid_cards = self.get_valid_cards(trick)

        # If first player
        if len(trick) == 0:
            card = min(valid_cards)

        # Not first player
        else:
            lead_suit = trick[0].suit

            # If no lead suit cards
            if lead_suit != valid_cards[0].suit:
                hearts = self._get_hearts(valid_cards)

                # If there are hearts
                if len(hearts) > 0:
                    if Card("♠", "Q") in hearts:
                        card = Card("♠", "Q")
                    else:
                        card = max(hearts)

                # No hearts
                else:
                    card = max(valid_cards)

            # Lead suit cards
            else:
                current_max_card = max(
                    [card for card in trick if card.suit == lead_suit]
                )
                losing_cards = [card for card in valid_cards if card < current_max_card]

                # Losing cards
                if len(losing_cards) > 0:
                    card = max(losing_cards)

                # Winning cards
                else:
                    card = min(valid_cards)

        self.hand.remove(card)
        return card
    
class SklearnPlayer(Player):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.model: BaseEstimator = joblib.load('random_forest.pkl')
        self.played_cards_history: list[Card] = []

    def play_card(self, trick: list[Card]) -> Card:
        valid_cards = self.get_valid_cards(trick)

        # Build feature DataFrame
        x = self._build_features(trick, valid_cards)
        
        # Predict card
        probs = self.model.predict_proba(x)[0]
        card_idx = int(np.argmax(probs)) + 1  # 1-indexed

        predicted_card = INDEX_TO_CARD.get(card_idx)

        # Fallback if predicted card not valid
        if predicted_card not in valid_cards:
            predicted_card = random.choice(valid_cards)

        self._hand.remove(predicted_card)
        self.played_cards_history.extend(trick + [predicted_card])
        return predicted_card

    def _build_features(self, trick: list[Card], valid_cards: list[Card]) -> pd.DataFrame:
        feature = {}
        features = [
            f"{type_}_{i}"
            for type_ in ['played_cards', 'hand', 'trick', 'valid_cards']
            for i in range(1, 53)
        ]

        # played_cards_1 to _52
        played = set(self.played_cards_history + trick)
        for i in range(1, 53):
            feature[f"played_cards_{i}"] = int(INDEX_TO_CARD[i] in played)

        # hand_1 to _52
        for i in range(1, 53):
            feature[f"hand_{i}"] = int(INDEX_TO_CARD[i] in self._hand)

        # trick_1 to _52
        for i in range(1, 53):
            feature[f"trick_{i}"] = int(INDEX_TO_CARD[i] in trick)

        # valid_cards_1 to _52
        for i in range(1, 53):
            feature[f"valid_cards_{i}"] = int(INDEX_TO_CARD[i] in valid_cards)

        return pd.DataFrame([feature], columns=features)
