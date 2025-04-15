from typing import Self


class Card:
    def __init__(self, suit, value):
        self._suit: str = suit
        self._value: str = value

    @property
    def suit(self) -> str:
        return self._suit

    @property
    def value(self) -> str:
        return self._value

    def __repr__(self):
        return f"{self._value}{self._suit}"

    def _get_numeric_value(self):
        """Convert card value to numeric for comparison"""
        values = {
            "2": 2,
            "3": 3,
            "4": 4,
            "5": 5,
            "6": 6,
            "7": 7,
            "8": 8,
            "9": 9,
            "10": 10,
            "J": 11,
            "Q": 12,
            "K": 13,
            "A": 14,
        }
        return values.get(self._value, 0)

    def __eq__(self, other: "Self"):
        return (
            self._get_numeric_value() == other._get_numeric_value()
            and self._suit == other._suit
        )

    def __lt__(self, other: "Self"):
        return self._get_numeric_value() < other._get_numeric_value()
    
    def __hash__(self):
        return hash((self.suit, self.value))
