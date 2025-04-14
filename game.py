from players import Player
from deck import Deck
from card import Card


class Game:
    def __init__(self, players: list[Player], max_points: int = 100) -> None:
        self.players = players
        self.max_points = max_points
        self.deck = Deck()
        self.lead_player_index = 0
        self.scores = [0] * 4
        self.round_scores = [0] * 4

    def game_over(self) -> bool:
        for score in self.scores:
            if score >= self.max_points:
                return True

    def play(self) -> None:
        # Play rounds
        while not self.game_over():
            # Reset round scores
            self.round_scores = [0] * 4

            # Deal cards
            self.deck.reset()
            self.deck.shuffle()
            for player in self.players:
                player.hand = self.deck.deal(13)
            # Play tricks
            for i in range(13):
                self.play_trick()
            self.scores = [score + round_score for score, round_score in zip(self.scores, self.round_scores)]
            print("-" * 5 + " Scores " + "-" * 5)
            for i, player in enumerate(self.players):
                print(f"{player}: {self.scores[i]}")
            print()
        
        winners = sorted(zip(self.players, self.scores), key=lambda x: x[1])
        print("-" * 5 + " Results " + "-" * 5)
        for i, player in enumerate(winners):
            print(f"({i + 1}) {player[0]}: {player[1]}")

    def play_trick(self) -> None:
        trick: list[Card] = []
        hearts: int = 0
        for i in range(0, 4):
            player_index = (self.lead_player_index + i) % 4
            player = self.players[player_index]

            card = player.play_card(trick)
            print(f"{player} played {card}")

            trick.append(card)

            if card._suit == "♥":
                hearts += 1
            
            if card == Card("♠", "Q"):
                hearts += 13

        lead_suit= trick[0].suit
        max_card = trick[0]
        max_card_index = 0
        for i, card in enumerate(trick):
            if card.suit == lead_suit and card > max_card:
                max_card = card
                max_card_index = i

        winning_player_index = (self.lead_player_index + max_card_index) % 4
        self.lead_player_index = winning_player_index
        
        winning_player = self.players[winning_player_index]
        print(f"{winning_player} won the trick!")

        self.round_scores[winning_player_index] += hearts
        print(f"Round Scores: {self.round_scores}\n")
