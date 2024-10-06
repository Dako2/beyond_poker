from math import inf
from pokerkit import Automation, Mode, NoLimitTexasHoldem

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
    (50000,50000),  # Starting stacks
    2,  # Number of players
    mode=Mode.CASH_GAME,
)

state.complete_bet_or_raise_to(7000)  # Dwan
state.complete_bet_or_raise_to(23000)  # Ivey
state.check_or_call()  # Dwan

state.burn_card('??')
state.deal_board('Jc3d5c')

state.complete_bet_or_raise_to(5000)  # Ivey
state.check_or_call()  # Dwan

state.burn_card('??')
state.deal_board('Jd')
