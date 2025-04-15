from hearts.card import Card
from abc import ABC, abstractmethod
import random

class Player(ABC):
    def __init__(self, name: str) -> None:
        self.name = name
        self._hand: list[Card] = []

    def __repr__(self):
        return self.name

    @property
    def hand(self) -> list[Card]:
        return self._hand
    
    @hand.setter
    def hand(self, hand: list[Card]) -> None:
        self._hand = hand

    def get_valid_cards(self, trick: list[Card]) -> list[Card]:
        if len(trick) > 0:

            lead_suit = trick[0].suit
            valid_cards = [
                card for card in self._hand if card.suit == lead_suit
            ]

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
        return [card for card in cards if card.suit == '♥' or card == Card('♠', 'Q')]

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
                    if Card('♠', 'Q') in hearts:
                        card = Card('♠', 'Q')
                    else:
                        card = max(hearts)
                
                # No hearts
                else:
                    card = max(valid_cards)
            
            # Lead suit cards
            else:
                current_max_card = max([card for card in trick if card.suit == lead_suit])
                losing_cards = [card for card in valid_cards if card < current_max_card]

                # Losing cards
                if len(losing_cards) > 0:
                    card = max(losing_cards)
                
                # Winning cards
                else:
                    card = min(valid_cards)

        self.hand.remove(card)
        return card
