from player import Player
from deck import Deck
from card import Card


class Game:
    def __init__(self) -> None:
        player_names = ["Player 1", "Player 2", "Player 3", "Player 4"]

        self.players = [Player(name) for name in player_names]
        self.deck = Deck()
        self.lead_player_index = 0
        self.scores = [0] * 4

    def play(self) -> None:
        # Deal cards
        self.deck.shuffle()
        for player in self.players:
            player.set_hand(self.deck.deal(13))

        # Play tricks
        for i in range(13):
            self.play_trick()

    def play_trick(self) -> None:
        trick: list[Card] = []
        hearts = 0
        for i in range(0, 4):
            player_index = (self.lead_player_index + i) % 4
            player = self.players[player_index]

            card = player.play_card(trick)
            print(f"{player} played {card}")

            trick.append(card)
            if card.suit == "♥":
                hearts += 1

        max_card = trick[0]
        max_card_index = 0
        for i, card in enumerate(trick):
            if card > max_card and card.suit == max_card.suit:
                max_card = card
                max_card_index = i

        self.lead_player_index = max_card_index
        winning_player = self.players[max_card_index]
        print(f"{winning_player} won the trick!")

        self.scores[max_card_index] += hearts
        print(f"Scores: {self.scores}\n")
