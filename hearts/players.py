from hearts.card import Card
from abc import ABC, abstractmethod
import random
import math


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


class MinCardPlayer(Player):
    """Always play the minimum card in the hand."""

    def play_card(self, trick: list[Card]) -> Card:
        valid_cards = self.get_valid_cards(trick)

        card = min(valid_cards)

        self.hand.remove(card)
        return card


class MinMaxCardPlayer(Player):
    """Player that plays the min lead suit card or the max non-lead suit card."""

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
                card = max(valid_cards)

            # Lead suit cards
            else:
                card = min(valid_cards)

        self.hand.remove(card)
        return card


class SluffingPlayer(Player):
    """Player that sluffs cards rationally.

    ----- Decision Tree -----
    Leading: play min card.
    Following:
        Void Suit:
            Hearts: play max heart
            Void Hearts: play max card
        Non-Void Suit:
            Losing Cards: play max losing card
            Winning Cards: play min winning card
    """

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
    

class MCTSNode:
    def __init__(self, parent=None, action=None):
        self.parent = parent
        self.action = action  # Action that led to this state
        self.children = []
        self.visits = 0
        self.score = 0
        self.untried_actions = []  # Will be populated during expansion
        
    def add_child(self, child):
        """Add a child node"""
        self.children.append(child)
        
    def is_expandable(self):
        """Check if node has untried actions"""
        return len(self.untried_actions) > 0
        
    def is_terminal(self, game_state):
        """Check if node is terminal (game over)"""
        return (len(game_state['player_hand']) == 0 and 
                all(len(hand) == 0 for hand in game_state['other_hands']))
    
    def get_untried_actions(self, game_state):
        """Get actions not tried from this node"""
        if not self.untried_actions:
            # First time getting untried actions for this node
            all_actions = self.get_all_possible_actions(game_state)
            tried_actions = [child.action for child in self.children]
            self.untried_actions = [a for a in all_actions if not any(
                a['card'] == ta['card'] and a['player'] == ta['player'] for ta in tried_actions)]
        return self.untried_actions
    
    def get_all_possible_actions(self, game_state):
        """Get all possible actions from this game state"""
        current_player = (game_state['current_position'] + len(game_state['current_trick'])) % 4
        
        # If current player is the MCTS agent
        if current_player == 0:
            hand = game_state['player_hand']
        else:
            # Adjust index since other_hands doesn't include the agent's hand
            hand = game_state['other_hands'][current_player - 1]
        
        # Get valid cards based on trick
        if not game_state['current_trick']:
            valid_cards = hand.copy()
        else:
            lead_suit = game_state['current_trick'][0].suit
            valid_cards = [card for card in hand if card.suit == lead_suit]
            if not valid_cards:
                valid_cards = hand.copy()
        
        # Convert valid cards to actions
        return [{'card': card, 'player': current_player} for card in valid_cards]

class MCTSPlayer(Player):
    def __init__(self, name: str, iterations: int = 1000, c: float = 1.41) -> None:
        super().__init__(name)
        self._name = name
        self._hand = []
        self.iterations = iterations
        self.c = c  # Exploration parameter
        self.player_count = 4  # Assuming 4 players in Hearts
        self.played_cards = set()  # Track cards seen so far
        self.all_cards = [Card(suit, rank) for suit in ["♥", "♦", "♠", "♣"] 
                        for rank in ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]]
        self.player_position = 0  # Position of this player in the game (0-3)
        
    def play_card(self, trick: list[Card]) -> Card:
        # Update knowledge of played cards
        for card in trick:
            self.played_cards.add(card)
            
        # Update player position based on trick length
        current_position = len(trick)
        self.player_position = current_position
        
        # Get valid cards to play
        valid_cards = self.get_valid_cards(trick)
        
        # If only one option, play it
        if len(valid_cards) == 1:
            card = valid_cards[0]
            self._hand.remove(card)
            self.played_cards.add(card)
            return card
        
        # Run MCTS to find best card
        best_card = self.run_mcts(trick, valid_cards, current_position)
        self._hand.remove(best_card)
        self.played_cards.add(best_card)
        return best_card
    
    def run_mcts(self, trick: list[Card], valid_cards: list[Card], current_position: int) -> Card:
        # Create root node representing current state
        root = MCTSNode(parent=None)
        
        # Run MCTS for specified number of iterations
        for _ in range(self.iterations):
            # Clone current game state for this simulation
            game_state = self.create_game_state(trick.copy(), current_position)
            
            # Run MCTS phases
            selected_node = self.select(root)
            expanded_node = self.expand(selected_node, game_state, valid_cards)
            simulation_result = self.simulate(expanded_node, game_state)
            self.backpropagate(expanded_node, simulation_result)
        
        # Choose best card based on statistics
        return self.best_card(root, valid_cards)
    
    def create_game_state(self, current_trick: list[Card], current_position: int):
        """Create a game state for simulation"""
        # Cards not in player's hand and not yet played
        unknown_cards = [card for card in self.all_cards 
                        if card not in self._hand and card not in self.played_cards]
        
        # Randomly distribute unknown cards to other players
        random.shuffle(unknown_cards)
        
        # Create hands for other players
        other_hands = []
        cards_per_player = len(unknown_cards) // (self.player_count - 1)
        
        for i in range(self.player_count - 1):
            start_idx = i * cards_per_player
            end_idx = start_idx + cards_per_player if i < self.player_count - 2 else len(unknown_cards)
            other_hands.append(unknown_cards[start_idx:end_idx])
        
        # Create game state
        return {
            'current_trick': current_trick,
            'current_position': current_position,
            'player_hand': self._hand.copy(),
            'other_hands': other_hands,
            'scores': [0] * self.player_count  # Track scores during simulation
        }
    
    def select(self, node):
        """Select a leaf node using UCB1"""
        while node.children and not node.is_expandable():
            node = self.select_uct(node)
        return node
    
    def select_uct(self, node):
        """Select child with highest UCT value"""
        log_parent_visits = math.log(node.visits)
        
        def uct_score(child):
            exploitation = child.score / child.visits if child.visits > 0 else 0
            exploration = self.c * math.sqrt(log_parent_visits / child.visits) if child.visits > 0 else float('inf')
            return exploitation + exploration
        
        return max(node.children, key=uct_score)
    
    def expand(self, node: MCTSNode, game_state: dict, valid_cards: list[Card]):
        """Expand node by adding a child"""
        if node.is_terminal(game_state):
            return node
            
        # If node is root and has no children, create children for all valid cards
        if node.parent is None and not node.children:
            for card in valid_cards:
                action = {'card': card, 'player': game_state['current_position']}
                child = MCTSNode(parent=node, action=action)
                node.add_child(child)
            # Return a random child to continue simulation
            return random.choice(node.children)
        
        # Expand one untried action
        untried_actions = node.get_untried_actions(game_state)
        if untried_actions:
            action = random.choice(untried_actions)
            child = MCTSNode(parent=node, action=action)
            node.add_child(child)
            return child
            
        return node
    
    def simulate(self, node, game_state):
        """Simulate random play from node until game end"""
        # Apply the action that got us to this node
        if node.action:
            self.apply_action(game_state, node.action)
        
        # Continue random play until game end
        while not self.is_game_over(game_state):
            possible_actions = self.get_possible_actions(game_state)
            action = random.choice(possible_actions)
            self.apply_action(game_state, action)
        
        # Return negative of player's score (lower is better in Hearts)
        return -game_state['scores'][0]  # Assuming player is at index 0
    
    def backpropagate(self, node, result):
        """Update statistics on path back to root"""
        while node:
            node.visits += 1
            node.score += result
            node = node.parent
    
    def best_card(self, root, valid_cards):
        """Choose best card based on visit count"""
        best_child = max(root.children, key=lambda child: child.visits)
        return best_child.action['card']
    
    def get_possible_actions(self, game_state):
        """Get all possible actions in current game state"""
        current_player = (game_state['current_position'] + len(game_state['current_trick'])) % self.player_count
        
        # If current player is the MCTS agent
        if current_player == 0:
            hand = game_state['player_hand']
        else:
            # Adjust index since other_hands doesn't include the agent's hand
            hand = game_state['other_hands'][current_player - 1]
        
        # Get valid cards based on trick
        valid_cards = self.get_valid_cards_for_simulation(hand, game_state['current_trick'])
        
        # Convert valid cards to actions
        return [{'card': card, 'player': current_player} for card in valid_cards]
    
    def get_valid_cards_for_simulation(self, hand, trick):
        """Get valid cards for a hand based on trick"""
        if not trick:
            return hand.copy()
            
        lead_suit = trick[0].suit
        valid_cards = [card for card in hand if card.suit == lead_suit]
        
        if valid_cards:
            return valid_cards
        return hand.copy()
    
    def apply_action(self, game_state, action):
        """Apply an action to the game state"""
        card = action['card']
        player = action['player']

        # Add card to trick
        game_state['current_trick'].append(card)
        
        # Remove card from player's hand
        if player == self.player_position:
            game_state['player_hand'].remove(card)
        else:
            game_state['other_hands'][player].remove(card)
        
        # Check if trick is complete
        if len(game_state['current_trick']) == self.player_count:
            # Determine trick winner
            lead_suit = game_state['current_trick'][0].suit
            highest_card = max([c for c in game_state['current_trick'] if c.suit == lead_suit])
            winner = (game_state['current_position'] + game_state['current_trick'].index(highest_card)) % self.player_count
            
            # Update score
            points = sum(1 for c in game_state['current_trick'] if c.suit == "♥")
            if Card("♠", "Q") in game_state['current_trick']:
                points += 13
                
            game_state['scores'][winner] += points
            
            # Start new trick
            game_state['current_trick'] = []
            game_state['current_position'] = winner
    
    def is_game_over(self, game_state):
        """Check if game is over"""
        # Game is over when all players have no cards left
        return (len(game_state['player_hand']) == 0 and 
                all(len(hand) == 0 for hand in game_state['other_hands']))
