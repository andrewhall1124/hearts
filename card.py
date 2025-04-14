class Card:
    def __init__(self, suit, value):
        self.suit = suit
        self.value = value

    def __repr__(self):
        return f"{self.value}{self.suit}"

    def get_numeric_value(self):
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
        return values.get(self.value, 0)

    def __eq__(self, other):
        """Equal to comparison"""
        if not isinstance(other, Card):
            return NotImplemented
        return (
            self.get_numeric_value() == other.get_numeric_value()
            and self.suit == other.suit
        )

    def __lt__(self, other):
        """Less than comparison"""
        if not isinstance(other, Card):
            return NotImplemented
        if self.get_numeric_value() == other.get_numeric_value():
            # If values are equal, compare suits (optional, define your own suit hierarchy)
            suits_order = {"♠": 3, "♥": 2, "♦": 1, "♣": 0}
            return suits_order.get(self.suit, 0) < suits_order.get(other.suit, 0)
        return self.get_numeric_value() < other.get_numeric_value()

    def __gt__(self, other):
        """Greater than comparison"""
        if not isinstance(other, Card):
            return NotImplemented
        return other < self

    def __le__(self, other):
        """Less than or equal to comparison"""
        if not isinstance(other, Card):
            return NotImplemented
        return self < other or self == other

    def __ge__(self, other):
        """Greater than or equal to comparison"""
        if not isinstance(other, Card):
            return NotImplemented
        return self > other or self == other
