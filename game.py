from math import inf
from pokerkit import Automation, Mode, NoLimitTexasHoldem
from treys import Evaluator
from treys import Card, Deck
import asyncio
import random

evaluator = Evaluator()

class TreysCard:
    def __init__(self, card_int, flipped=True):
        self.card_int = card_int
        self.card_str = Card.int_to_str(card_int).upper()
        self.flipped = flipped  # True if face up, False if face down

    def flip(self):
        """Toggle the flipped state of the card."""
        self.flipped = not self.flipped

    def __repr__(self):
        """Provide a string representation of the card, useful for debugging."""
        return self.card_str if not self.flipped else "BACK"

class Player:
    def __init__(self, sid, name, stack, bot = False):
        self.name = name
        self.sid = sid
        self.bot = bot

    def query_action(self):
        """Ask the player for their action."""
        if self.bot:
            action = random.choice(['fold', 'call', 'raise'])
            if action == 'raise':
                action += str(random.randrange(200, 20000, 200))
            return action
        
class Game:
    def __init__(self):
        self.deck = Deck()
        self.deck.shuffle()
        self.players = []
        self.dealer_position = 0

    def post_blinds(self):
        players = list(self.players.values())
        # Calculate the positions of the small blind and big blind
        small_blind_position = (self.dealer_position + 1) % len(players)
        big_blind_position = (self.dealer_position + 2) % len(players)
    
    def rotate_dealer(self):
        self.dealer_position = (self.dealer_position + 1) % len(self.players)

    def add_player(self, sid, name, stack, bot=False):
        player = Player(sid, name, stack, bot)
        self.players.append(player)


state = NoLimitTexasHoldem.create_state(
    # Automations
    (
        Automation.ANTE_POSTING,
        Automation.BET_COLLECTION,
        Automation.BLIND_OR_STRADDLE_POSTING,
        Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
        Automation.HAND_KILLING,
        Automation.CHIPS_PUSHING,
        Automation.CHIPS_PULLING,
    ),
    False,  # Uniform antes?
    0,  # Antes
    (100, 200,),  # Blinds or straddles
    200,  # Min-bet
    (50000, 50000, 50000),  # Starting stacks
    3,  # Number of players
    mode=Mode.CASH_GAME,
)

state.deal_hole('Ac2d')  # Ivey
state.deal_hole('????')  # Antonius
state.deal_hole('7h6h')  # Dwan

state.complete_bet_or_raise_to(7000)  # Dwan
state.complete_bet_or_raise_to(23000)  # Ivey
state.fold()  # Antonius
state.check_or_call()  # Dwan

state.burn_card('??')
state.deal_board('Jc3d5c')

state.complete_bet_or_raise_to(5000)  # Ivey
state.check_or_call()  # Dwan

state.burn_card('??')
state.deal_board('Jd')

state.complete_bet_or_raise_to(5000)  # Dwan
state.check_or_call()  # Dwan

try:
    a = state.burn_card('??')
    a = state.deal_board('Qd')
except:
    print("invalid action")
