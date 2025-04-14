import random
from card import Card


class Deck:
    def __init__(self):
        self.suits = ["♥", "♦", "♣", "♠"]
        self.values = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
        self.cards = []
        self.create_deck()

    def create_deck(self):
        """Create a new deck of 52 cards"""
        self.cards = []
        for suit in self.suits:
            for value in self.values:
                self.cards.append(Card(suit, value))
        return self

    def shuffle(self):
        """Shuffle the deck"""
        random.shuffle(self.cards)
        return self

    def deal(self, num_cards=1):
        """Deal a specified number of cards from the deck"""
        if len(self.cards) < num_cards:
            raise ValueError(
                f"Cannot deal {num_cards} cards. Only {len(self.cards)} remaining."
            )

        dealt_cards = []
        for _ in range(num_cards):
            dealt_cards.append(self.cards.pop())

        return dealt_cards

    def deal_hand(self, hand_size):
        """Deal a hand of specified size"""
        return self.deal(hand_size)

    def count(self):
        """Return the number of cards remaining in the deck"""
        return len(self.cards)

    def __repr__(self):
        return f"Deck of {self.count()} cards"
