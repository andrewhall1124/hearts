import random
from card import Card
from typing import Self


class Deck:
    def __init__(self):
        self._suits = ["♥", "♦", "♣", "♠"]
        self._values = [
            "A",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "J",
            "Q",
            "K",
        ]
        self._cards = []
        self.reset()

    def reset(self) -> "Self":
        """Create a new deck of 52 cards"""
        self._cards = []
        for suit in self._suits:
            for value in self._values:
                self._cards.append(Card(suit, value))
        return self

    def shuffle(self) -> "Self":
        """Shuffle the deck"""
        random.shuffle(self._cards)
        return self

    def deal(self, num_cards: int = 1):
        """Deal a specified number of cards from the deck"""
        if len(self._cards) < num_cards:
            raise ValueError(
                f"Cannot deal {num_cards} cards. Only {len(self._cards)} remaining."
            )

        dealt_cards = []
        for _ in range(num_cards):
            dealt_cards.append(self._cards.pop())

        return dealt_cards

    def __len__(self):
        return len(self._cards)
    
    def __repr__(self):
        return str(self._cards)
