from treys import Evaluator
from treys import Deck, Card

evaluator = Evaluator()
deck = Deck()

player1_hand = deck.draw(2)
player2_hand = deck.draw(2)

board = deck.draw(52)

full = [Card.int_to_pretty_str(x) for x in deck._FULL_DECK]
print(full)
print(Card.ints_to_pretty_str(deck._FULL_DECK))


Card.int_to_str(deck._FULL_DECK[0])

