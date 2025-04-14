from card import Card


class Player:
    def __init__(self, name: str) -> None:
        self.name = name
        self.hand: list[Card] = []

    def __repr__(self):
        return self.name

    def set_hand(self, hand: list[Card]) -> None:
        self.hand = hand

    def play_card(self, trick: list[Card]) -> Card:
        if len(trick) > 0:
            lead_suit = trick[0].suit
            valid_cards = [
                index for index, card in enumerate(self.hand) if card.suit == lead_suit
            ]
            if len(valid_cards) > 0:
                return self.hand.pop(valid_cards[0])
            else:
                return self.hand.pop()
        else:
            return self.hand.pop()
