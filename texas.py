from math import inf

from pokerkit import Automation, NoLimitTexasHoldem

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
    True,  # Uniform antes?
    500,  # Antes
    (1000, 2000),  # Blinds or straddles
    2000,  # Min-bet
    (1125600, inf, 553500),  # Starting stacks
    3,  # Number of players
)

state.deal_hole('Ac2d')  # Ivey
state.deal_hole('????')  # Antonius
state.deal_hole('7h6h')  # Dwan

state.complete_bet_or_raise_to(7000)  # Dwan
state.complete_bet_or_raise_to(23000)  # Ivey
state.fold()  # Antonius
state.check_or_call()  # Dwan