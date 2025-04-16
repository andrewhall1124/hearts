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
        
    def add_child(self, child):
        """Add a child node"""
        self.children.append(child)
        
    def is_terminal(self, game_state):
        """Check if node is terminal (game over)"""
        return (len(game_state['hands'][game_state['mcts_position']]) == 0)


class MCTSPlayer(Player):
    def __init__(self, name: str, iterations: int = 1000, c: float = 1.41) -> None:
        super().__init__(name)
        self.iterations = iterations
        self.c = c  # Exploration parameter
        self.player_count = 4  # Assuming 4 players in Hearts
        self.played_cards = set()  # Track cards seen so far
        self.all_cards = [Card(suit, rank) for suit in ["♥", "♦", "♠", "♣"] 
                         for rank in ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]]
        
    def play_card(self, trick: list[Card]) -> Card:
        # Update knowledge of played cards
        for card in trick:
            self.played_cards.add(card)
            
        # Get valid cards to play
        valid_cards = self.get_valid_cards(trick)
        
        # If only one option, play it
        if len(valid_cards) == 1:
            card = valid_cards[0]
            self._hand.remove(card)
            self.played_cards.add(card)
            return card
        
        # Run MCTS to find best card
        best_card = self.run_mcts(trick, valid_cards)
        self._hand.remove(best_card)
        self.played_cards.add(best_card)
        return best_card
    
    def run_mcts(self, trick: list[Card], valid_cards: list[Card]) -> Card:
        # Create root node representing current state
        root = MCTSNode()
        
        # Run MCTS for specified number of iterations
        for _ in range(self.iterations):
            # Create a game state for this simulation
            game_state = self.create_game_state(trick.copy())
            
            # Select
            selected_node = self.select(root)
            
            # Expand
            expanded_node = self.expand(selected_node, game_state, valid_cards)
            
            # Simulate
            simulation_result = self.simulate(expanded_node, game_state)
            
            # Backpropagate
            self.backpropagate(expanded_node, simulation_result)
        
        # Choose best card based on statistics
        if not root.children:
            # If no simulations were successful, choose a random card
            return random.choice(valid_cards)
            
        best_child = max(root.children, key=lambda child: child.visits)
        return best_child.action['card']
    
    def create_game_state(self, current_trick: list[Card]):
        """Create a game state for simulation"""
        # Cards not in player's hand and not yet played
        unknown_cards = [card for card in self.all_cards 
                        if card not in self._hand and card not in self.played_cards]
        
        # Randomly distribute unknown cards to other players
        random.shuffle(unknown_cards)
        
        # Determine player positions
        # Calculate the position of MCTS player based on trick length
        mcts_position = len(current_trick)
        
        # Calculate who leads the trick (important for determining turn order)
        trick_starter = (4 - len(current_trick)) % 4
        
        # Create hands for all players
        hands = [[] for _ in range(self.player_count)]
        hands[mcts_position] = self._hand.copy()  # MCTS player's hand
        
        # Distribute unknown cards to other players
        other_positions = [i for i in range(self.player_count) if i != mcts_position]
        cards_per_player = len(unknown_cards) // len(other_positions)
        
        for i, pos in enumerate(other_positions):
            start_idx = i * cards_per_player
            end_idx = start_idx + cards_per_player if i < len(other_positions) - 1 else len(unknown_cards)
            hands[pos] = unknown_cards[start_idx:end_idx]
        
        # Create game state
        return {
            'current_trick': current_trick,
            'trick_starter': trick_starter,
            'current_player': (trick_starter + len(current_trick)) % self.player_count,
            'hands': hands,
            'mcts_position': mcts_position,
            'scores': [0] * self.player_count  # Track scores during simulation
        }
    
    def select(self, node):
        """Select a leaf node using UCB1"""
        current_node = node
        
        # Travel down the tree until we reach a leaf or unexpanded node
        while current_node.children and not self.is_expandable(current_node):
            current_node = self.select_uct(current_node)
            
        return current_node
    
    def is_expandable(self, node):
        """Check if node can be expanded (has untried actions)"""
        # For this implementation, a node is expandable if it has no children
        return len(node.children) == 0
    
    def select_uct(self, node):
        """Select child with highest UCT value"""
        log_parent_visits = math.log(node.visits + 1)
        
        def uct_score(child):
            # UCB1 formula: exploitation + exploration
            if child.visits == 0:
                return float('inf')  # Always explore unvisited nodes
                
            exploitation = child.score / child.visits
            exploration = self.c * math.sqrt(log_parent_visits / child.visits)
            return exploitation + exploration
        
        return max(node.children, key=uct_score)
    
    def expand(self, node, game_state, valid_cards):
        """Expand node by adding a child"""
        # If node has no children yet and is the root (MCTS player's turn)
        if node.parent is None and not node.children and game_state['current_player'] == game_state['mcts_position']:
            for card in valid_cards:
                action = {'card': card, 'player': game_state['mcts_position']}
                child = MCTSNode(parent=node, action=action)
                node.children.append(child)
            
            # Return a random child to continue simulation
            if node.children:
                return random.choice(node.children)
                
        # For non-root nodes or if not MCTS player's turn
        # Just pass through as we'll handle these moves in simulation
        return node
    
    def simulate(self, node, game_state):
        """Simulate random play from node until game end"""
        # Make a deep copy of the game state to avoid modifying the original
        sim_state = {
            'current_trick': game_state['current_trick'].copy(),
            'trick_starter': game_state['trick_starter'],
            'current_player': game_state['current_player'],
            'hands': [hand.copy() for hand in game_state['hands']],
            'mcts_position': game_state['mcts_position'],
            'scores': game_state['scores'].copy()
        }
        
        # Apply the action that got us to this node if it exists
        if node.action:
            self.apply_action(sim_state, node.action)
        
        # Continue random play until game end
        while not self.is_game_over(sim_state):
            # Get possible actions for current player
            possible_actions = self.get_possible_actions(sim_state)
            if not possible_actions:
                break  # No valid actions, shouldn't happen in a valid game
                
            # Select a random action and apply it
            action = random.choice(possible_actions)
            self.apply_action(sim_state, action)
        
        # Return negative of MCTS player's score (lower is better in Hearts)
        return -sim_state['scores'][sim_state['mcts_position']]
    
    def backpropagate(self, node, result):
        """Update statistics on path back to root"""
        current_node = node
        while current_node:
            current_node.visits += 1
            current_node.score += result
            current_node = current_node.parent
    
    def get_possible_actions(self, game_state):
        """Get all possible actions for the current player"""
        current_player = game_state['current_player']
        hand = game_state['hands'][current_player]
        
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
        game_state['hands'][player].remove(card)
        
        # Move to next player
        game_state['current_player'] = (game_state['current_player'] + 1) % self.player_count
        
        # Check if trick is complete
        if len(game_state['current_trick']) == self.player_count:
            # Determine trick winner
            lead_suit = game_state['current_trick'][0].suit
            highest_cards = [c for c in game_state['current_trick'] if c.suit == lead_suit]
            if highest_cards:
                highest_card = max(highest_cards)
                winner_index = game_state['current_trick'].index(highest_card)
                winner = (game_state['trick_starter'] + winner_index) % self.player_count
                
                # Calculate points
                points = sum(1 for c in game_state['current_trick'] if c.suit == "♥")
                if Card("♠", "Q") in game_state['current_trick']:
                    points += 13
                    
                # Update score
                game_state['scores'][winner] += points
                
                # Start new trick with winner leading
                game_state['current_trick'] = []
                game_state['trick_starter'] = winner
                game_state['current_player'] = winner
    
    def is_game_over(self, game_state):
        """Check if game is over"""
        # Game is over when all players have no cards left
        return all(len(hand) == 0 for hand in game_state['hands'])
