from hearts.players import Player
from hearts.deck import Deck
from hearts.card import Card


class Game:
    def __init__(
        self,
        players: list[Player],
        max_points: int = 100,
        print_scores: bool = True,
    ) -> None:
        self.players = players
        self.max_points = max_points
        self.print_scores = print_scores
        self.deck = Deck()
        self.lead_player_index = 0
        self.scores = [0] * 4
        self.round_scores = [0] * 4
        self.played_cards: list[Card] = []

    @property
    def game_over(self) -> bool:
        for score in self.scores:
            if score >= self.max_points:
                return True

    def play(self) -> dict:
        # Play rounds
        while not self.game_over:
            # Reset round scores
            self.round_scores = [0] * 4

            # Deal cards
            self.deck.reset()
            self.deck.shuffle()
            self.played_cards = []
            for player in self.players:
                player.hand = self.deck.deal(13)

            # Play tricks
            for i in range(13):
                self.play_trick()
            self.scores = [
                score + round_score
                for score, round_score in zip(self.scores, self.round_scores)
            ]

        return [
            {"player": player.name, "score": score}
            for player, score in zip(self.players, self.scores)
        ]

    def play_trick(self) -> None:
        trick: list[Card] = []
        hearts: int = 0
        for i in range(0, 4):
            player_index = (self.lead_player_index + i) % 4
            player = self.players[player_index]

            card = player.play_card(trick)

            trick.append(card)
            self.played_cards.append(card)

            if card._suit == "♥":
                hearts += 1

            if card == Card("♠", "Q"):
                hearts += 13

        lead_suit = trick[0].suit
        max_card = trick[0]
        max_card_index = 0
        for i, card in enumerate(trick):
            if card.suit == lead_suit and card > max_card:
                max_card = card
                max_card_index = i

        winning_player_index = (self.lead_player_index + max_card_index) % 4
        self.lead_player_index = winning_player_index

        self.round_scores[winning_player_index] += hearts
