import random

class Card:
    def __init__(self, card, flipped=True):
        self.card = card
        self.flipped = flipped  # True if face up, False if face down

    def flip(self):
        """Toggle the flipped state of the card."""
        self.flipped = not self.flipped

    def __repr__(self):
        """Provide a string representation of the card, useful for debugging."""
        return self.card if not self.flipped else "back"

class Player:
    def __init__(self, id, name, chips=1000, bot = False):
        self.id = id
        self.name = name
        self.hand = []

        self.chips = chips
        self.current_bet = 0
        self.all_in = False

        self.in_game = True  # True if the player hasn't folded
        self.bot = bot

        self.log = ""
        self.action = ""

    def logging(self,text):
        self.log += text
        self.action = text

    def allin(self,):
        if self.bet(self.chips):
            self.logging(f"{self.name} all in!\n")

    def bet(self, amount):
        if amount <= self.chips:
            self.chips -= amount
            self.current_bet += amount
            self.logging(f"{self.name} bet additional {amount} with current total bet of {self.current_bet}\n")
            return True
        return False
    
    def fold(self):
        self.in_game = False
        self.logging(f"{self.name} folds.\n")

    def get_updates(self):
        if self.is_updated:
            updates = self.events.copy()
            self.events.clear()
            self.is_updated = False
            return updates
        return []

class Deck:
    def __init__(self):
        ranks = '23456789TJQKA'
        suits = 'HDCS'  # Hearts, Diamonds, Clubs, Spades
        self.cards = [f"{rank}{suit}" for suit in suits for rank in ranks]
        random.shuffle(self.cards)

    def deal(self, count):
        dealt_cards = self.cards[:count]
        self.cards = self.cards[count:]
        return dealt_cards

class Game:
    def __init__(self, max_players):
        self.players = {'Eliza':Player(1, 'Eliza', bot=True)}

        self.deck = Deck()
        self.max_players = max_players
        self.game_state = 'waiting'
        self.board_sid = None
        self.community_cards = []
        self.community_cards_secret = []
        self.pot = 0
        self.current_highest_bet = 0
        self.game_id = 0
        self.log = ""
        self.action = ""
        self.dealer_position = 0
        self.small_blind_amount = 5
        self.big_blind_amount = 10

    def logging(self, text):
        self.log += text
        self.action = text

    def add_player(self, player_id, player_name = 'Player 1'):
        self.players['Player 1'] = Player(player_id, player_name, bot = False)
           
    def post_blinds(self):
        players = list(self.players.values())
        # Calculate the positions of the small blind and big blind
        small_blind_position = (self.dealer_position + 1) % len(players)
        big_blind_position = (self.dealer_position + 2) % len(players)

        # Post small blind
        players[small_blind_position].bet(self.small_blind_amount)
        players[small_blind_position].current_bet = self.small_blind_amount
        self.pot += self.small_blind_amount
        self.logging(f"{players[small_blind_position].name} posts small blind of {self.small_blind_amount}\n")

        # Post big blind
        players[big_blind_position].bet(self.big_blind_amount)
        players[big_blind_position].current_bet = self.big_blind_amount
        self.pot += self.big_blind_amount
        self.current_highest_bet = self.big_blind_amount
        self.logging(f"{players[big_blind_position].name} posts big blind of {self.big_blind_amount}\n")

    def rotate_dealer(self):
        self.dealer_position = (self.dealer_position + 1) % len(self.players)
        self.logging(f"Dealer position is now at {self.dealer_position}.\n")

    def start_game(self):
        self.deck = Deck()
        self.rotate_dealer()
        self.community_cards = ['back']*5
        self.community_cards_secret = ['back']*5
        self.game_id += 1
        self.logging(f"Starting Game #{self.game_id}\n")
        self.pot = 0
        self.current_bet = 0

        self.post_blinds()
        self.players['Eliza'].hand = self.deck.deal(2)
        self.logging(f"Eliza are dealt with a hand of {self.players['Eliza'].hand}\n")
        self.players['Player 1'].hand = self.deck.deal(2)
        self.logging(f"Player 1 are dealt with a hand of {self.players['Player 1'].hand}\n")

        self.game_state = 'pre-flop'
        self.community_cards_secret = self.deck.deal(5)

        return self.players['Eliza'].hand, self.players['Player 1'].hand
    
    def deal_community_cards(self):
        # Deal 5 community cards as an example
        if self.game_state == 'pre-flop':
            self.community_cards = self.community_cards_secret[:3] + ['back', 'back']
            self.logging(f"Flop Community cards: {self.community_cards}\n")
            self.game_state = 'flop'
        elif self.game_state == 'flop':
            self.community_cards = self.community_cards_secret[:4] + ['back']
            self.logging(f"Turn Community cards: {self.community_cards}\n")
            self.game_state = 'turn'
        elif self.game_state == 'turn':
            self.community_cards = self.community_cards_secret
            self.logging(f"River Community cards: {self.community_cards}\n")
            self.game_state = 'river'
        return self.community_cards
    
    def run_betting_round(self):
        players = self.players.values()
        print(f"Starting {self.game_state} betting round.")
        starting_position = (self.dealer_position + 3) % len(players)  # Betting starts left of the big blind
        current_position = starting_position

        while True:
            print(f"Stage: {self.game_state}, Current highest bet: {self.current_highest_bet}")
            player = players[current_position]
            if player.in_game:
                self.player_bet(player, self.game_state)

            current_position = (current_position + 1) % len(players)
            if current_position == starting_position:
                break

    def player_bet(self, player_id, amount):
        if self.players[player_id].bet(amount):
            self.pot += amount
            return True
        return False
    
    def player_call(self, player_id):
        if self.current_highest_bet > self.players[player_id].current_bet:
            self.players[player_id].bet(self.current_highest_bet - self.players[player_id].current_bet)
            self.pot += self.current_highest_bet - self.players[player_id].current_bet
            self.logging(f"{self.players[player_id].name} calls with {self.current_highest_bet - self.players[player_id].current_bet}\n")
    
    def reset_bets(self):
        self.player_bets = {player: 0 for player in self.players}
        self.current_bet = 0
        
    def fold_player(self, player_id):
        # Remove player from current game but keep in session for future rounds
        self.players[player_id].fold()
        self.logging(f"{self.players[player_id].name} folds.\n")

    def bot_action(self):
        self.players['Eliza']

def cards_to_img(cards_list):
    card_images = [f"{card}.png" for card in cards_list]
    return card_images


