from math import inf
from pokerkit import Automation, Mode, NoLimitTexasHoldem
from treys import Evaluator
from treys import Card, Deck
import asyncio
import random
from collections import deque

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
    def __init__(self, players):
        self.deck = Deck()
        self.deck.shuffle()

        self.players = deque(players)
        self.num_players = len(players)
        
        self.dealer_position = 0
        self.small_blind_position = (self.dealer_position + 1) % self.num_players
        self.big_blind_position = (self.dealer_position + 2) % self.num_players
        self.starting_position = (self.dealer_position + 3) % self.num_players  # Betting starts left of the big blind
        
        self.current_position = self.starting_position

        self.state = None
        self.pot = 0
        self.current_bet = 0

    def get_next_player(self):
        # Rotate the deque until you find an active player or return to the original position.
        attempts = len(self.players)
        while attempts > 0:
            player = self.players.popleft()  # Remove the player from the front
            self.players.append(player)  # Add the player back to the end
            if player.in_game:  # Check if the player is still active in the game
                return player
            attempts -= 1
        return None  # Return None if no active players are found

    def post_blinds(self):
        pass
    def rotate_dealer(self):
        self.players.rotate(-1)

    def start_game(self,):
        self.rotate_dealer()
        self.current_position = self.starting_position
        starting_stacks = [player.stack for player in self.players]

        self.state = NoLimitTexasHoldem.create_state(
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
            starting_stacks,  # Starting stacks
            3,  # Number of players
            mode=Mode.CASH_GAME,
        )

    def deal_holes(self):
        player = self.get_next_player()
        while player:
            player.in_game = True
            player.hand = [TreysCard(x, flipped=False) for x in self.deck.draw(2)]
            hand = ''.join(card.card_str for card in player.hand)
            print(f"{player.name} has {hand}")
            self.state.deal_hole(hand)
            player = self.get_next_player()

    def bet_round(self):
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

        state.complete_bet_or_raise_to(5000)  # Ivey