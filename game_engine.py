import random
from treys import Evaluator
from treys import Deck, Card
from llm_test import LLMPlayer
from tts_openai import tts_openai_replay, tts_openai_to_wav_files
import time
from collections import deque

evaluator = Evaluator()

class TreysCard:
    def __init__(self, card_int, flipped=True):
        self.card_int = card_int
        self.card_str = Card.int_to_str(card_int).upper()
        self.flipped = flipped  # True if face up, False if face down

    def flip(self):
        """Toggle the flipped state of the card."""
        print("flipping")
        self.flipped = not self.flipped

    def __repr__(self):
        """Provide a string representation of the card, useful for debugging."""
        return self.card_str if not self.flipped else "BACK"

class Player:
    def __init__(self, id, name, chips=1000, autobot = True):
        self.id = id
        self.name = name
        self.hand_str = []
        self.hand = []
        self.hand_int = []

        self.chips = chips
        self.current_bet = 0
        self.all_in = False

        self.in_game = True  # True if the player hasn't folded
        self.autobot = autobot

        self.action = None

        self.log = ""
        self.waiting_for_action = False

    def logging(self,text):
        self.log += text

    def query_action(self,):
        if self.autobot:
            action = random.choice(['call', 'bet'])
            if action == 'bet':
                action += str(random.randrange(5, int(self.chips), 5))
            return action
        else:
            #tts_openai_to_wav_files("it's your move now, you can either fold, check, call, raise or all-in.")
            #tts_openai_replay("it's your move now, you can either fold, check, call, raise or all-in.")
            
            self.waiting_for_action = True
            while self.waiting_for_action:
                #if self.action = input(message):
                #    self.waiting_for_action = False
                #print("waiting for the action")
                time.sleep(0.5)           
            return self.action
    
    def bet(self, amount):
        if amount <= self.chips:
            self.chips -= amount
            self.current_bet += amount
            self.logging(f"{self.name} bet additional {amount} with current total bet of {self.current_bet}\n")
            return True
        return False
    
    def allin(self,):
        if self.bet(self.chips):
            self.logging(f"{self.name} all in!\n")

    def fold(self):
        self.in_game = False

    def get_updates(self, game_updates = ""):
        return game_updates

class Game:
    def __init__(self,):
        eliza = Player(1, 'Eliza', autobot=True)
        human = Player(2, 'Human', autobot=False)
        self.players = {'Player 1': eliza, 'Player 2': human}
        #self.max_players = 2
        self.deck = Deck()
        self.community_cards = []
        
        self.players_queue = deque([eliza, human])
        self.num_players = 2
        

        self.pot = 0
        self.side_pots = []
        self.current_highest_bet = 0
        
        self.game_id = 0
        self.current_position = 0
        self.board_sid = None
        self.game_state = 'waiting'
        self.game_history = ""
        self.game_histories = {}

        self.dealer_position = 0

        self.small_blind_amount = 5
        self.big_blind_amount = 10

    def get_current_player(self):
        return list(self.players.values())[self.current_position]

    def logging(self, text):
        self.game_history += text
    
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
        #self.logging(f"Dealer position is now at {self.dealer_position}.\n")

    def start_game(self):
        self.game_id += 1
        self.pot = 0
        self.current_highest_bet = 0
        
        self.deck = Deck()
        self.rotate_dealer()
        self.post_blinds()
        
        players = list(self.players.values())
        for player in players:
            player.in_game = True
            player.hand = [TreysCard(x, flipped=False) for x in self.deck.draw(2)]
            player.hand_str = [card.card_str for card in player.hand]
            player.hand_int = [card.card_int for card in player.hand]
        
        self.community_cards = [TreysCard(x) for x in self.deck.draw(5)] #['back']*5, object class, not string
        self.community_cards_str = [card.card_str for card in self.community_cards]
        print(self.community_cards_str) #to be hidden

        self.game_state = 'pre-flop'
        self.run_betting_round('pre-flop')
    
    def proceed_game(self):
        # Deal 5 community cards as an example
        print("proceeding the game ...")
        if self.game_state == 'pre-flop':
            for i in range(3):
                self.community_cards[i].flip()
            self.logging(f"Flop Community cards\n")
            self.game_state = 'flop'
            self.run_betting_round('flop')
            #self.proceed_game()

        elif self.game_state == 'flop':
            self.community_cards[3].flip()
            self.logging(f"Turn Community cards\n")
            self.game_state = 'turn'
            self.run_betting_round('turn')
            #self.proceed_game()

        elif self.game_state == 'turn':
            self.community_cards[4].flip()
            self.logging(f"River Community cards\n")
            self.game_state = 'river'
            self.run_betting_round('river')
            #self.proceed_game()

        elif self.game_state == 'river':
            self.logging(f"Showdown!\n")
            self.showdown()
            self.game_state = 'waiting'
    
    def showdown(self):
        players = list(self.players.values())
        for player in players:
            self.logging(f"{player.name}'s hand: {player.hand_str}\n")
        self.declare_winner()

    def evaluate_hand(self, board, hand):
        p1_score = evaluator.evaluate(board, hand)
        p1_class = evaluator.get_rank_class(p1_score)
        print(p1_score, p1_class)
        return p1_score, p1_class
    
    def declare_winner(self):
        active_players = [player for player in self.players.values() if player.in_game]

        # Evaluate hands if more than one player remains
        if len(active_players) > 1:
            board = [card.card_int for card in self.community_cards]
            player_scores = [(player, self.evaluate_hand(board, player.hand_int)) for player in active_players]
            # Sort by the score, lower is better in Treys
            player_scores.sort(key=lambda x: x[1][0])

            # Distribute the main pot and any side pots
            self.distribute_pots(player_scores)
        elif len(active_players) == 1:
            # Only one player remains, they win all the pots
            winner = active_players[0]
            total_winnings = self.pot + sum(pot['amount'] for pot in self.side_pots)
            winner.chips += total_winnings
            self.logging(f"{winner.name} wins the total pot of {total_winnings} chips.")
        
        self.logging("End of game.\n")
        self.logging("==========\n")
        self.logging('\n'.join(f"{player.name} left with {player.chips} chips." for player in self.players.values()))
        self.game_state = 'waiting'
        #self.players['Player 1'].query_action(self.game_analysis(), source = 'user')

    def distribute_pots(self, player_scores):
        # Main pot distribution
        self.distribute_pot(self.pot, player_scores)

        # Side pots distribution
        for side_pot in self.side_pots:
            # Find eligible players for this side pot
            eligible_players = [score for score in player_scores if score[0].id in side_pot['eligible']]
            self.distribute_pot(side_pot['amount'], eligible_players)

    def distribute_pot(self, pot_amount, player_scores):
        if not player_scores:
            return

        # Determine the winner(s)
        winners = [player_scores[0]]
        for score in player_scores[1:]:
            if score[1][0] == winners[0][1][0]:  # Compare scores
                winners.append(score)
            else:
                break

        # Divide the pot among the winners
        win_amount = pot_amount / len(winners)
        for winner in winners:
            winner[0].chips += win_amount
            hand_rank = evaluator.class_to_string(winner[1][1])
            self.logging(f"{winner[0].name} wins {win_amount} chips with a {hand_rank} hand.")

    def game_analysis(self):
        summary = "========== Players Info ==========\n"
        board = [card.card_int for card in self.community_cards]
        for player_id, player in self.players.items():
            summary += f"{player_id}: {player.name}\n"
        summary += "\n"
        players = list(self.players.values())
        hands = []
        for player in players:
            hands.append([card.card_int for card in player.hand])
        #print(board, hands)
        summary += evaluator.hand_summary(board, hands)
        self.game_histories[self.game_id] = self.game_history
        
        print(summary)
        return summary
    
    def get_next_player(self):
        # Rotate the deque until you find an active player or return to the original position.
        attempts = len(self.players_queue)
        while attempts > 0:
            player = self.players_queue.popleft()  # Remove the player from the front
            self.players_queue.append(player)  # Add the player back to the end
            if player.in_game:  # Check if the player is still active in the game
                return player
            attempts -= 1
        return None  # Return None if no active players are found
    
    def run_betting_round(self, stage):
        print(f"Starting {stage} betting round.")
        initial_player_count = len(self.players_queue)
        min_actions_required = initial_player_count
        actions_taken = 0

        while actions_taken < min_actions_required or not self.bets_equalized():
            player = self.get_next_player()
            if not player.in_game:
                continue  # Skip players who have folded or are all-in without further chips to bet

            print(f"It's {player.name}'s turn to act.")
            action = player.query_action()
            print(f"Player {player.name}'s action: {action}")

            if action == 'fold':
                player.fold()
                self.logging(f"{player.name} folds.")
                if len(self.active_players()) == 1:
                    break
            elif action.startswith('call'):
                self.handle_call(player)
            elif action == 'check':
                self.handle_check(player)
            elif action == 'allin':
                self.handle_all_in(player)
            elif action.startswith('bet') or action.startswith('raise'):
                if self.handle_bet_or_raise(player, action):
                    min_actions_required += initial_player_count - 1  # Reset actions for others to respond to the raise

            actions_taken += 1

    def bets_equalized(self):
        """ Check if all active players have the same current bet or are all-in. """
        highest_bet = max(player.current_bet for player in self.players_queue if player.in_game)
        for player in self.players_queue:
            if player.in_game and player.current_bet < highest_bet and not player.is_all_in:
                return False
        return True
    
    def run_betting_round11(self, stage): #only two players
        while True:
            player = self.get_next_player()
            print(f"Starting {stage} betting round. it's player {player.name} turn to act.")
            print(f"in game or not {self.players_queue[0].in_game}, {self.players_queue[1].in_game}")
            print(f"waiting for {player.name} action ... ")

            action = player.query_action()            
            print(f"Player {player.name} action:{action}")

            if 'fold' in action:
                player.fold()
                self.logging(f"{player.name} folds.\n")
                break
            elif 'call' in action:
                #if self.current_highest_bet > 0:
                call_amount = self.current_highest_bet - player.current_bet
                if call_amount > 0:
                    if player.bet(call_amount):
                        print(f"{player.name} calls {self.current_highest_bet}.")
                        self.pot += call_amount
                        self.logging(f"{player.name} calls. Pot size goes to {self.pot}.\n")
                    else:
                        message = "Not enough chips to call."
                else:
                    self.logging(f"{player.name} checks.\n")
                    break
            elif 'check' in action:
                if player.current_bet - self.current_highest_bet == 0:
                    self.logging(f"{player.name} checks.\n")
                    break
                else:
                    message = "Cannot check unless all in."
            elif action == 'allin':
                all_in_amount = player.allin()
                if all_in_amount < self.current_highest_bet:
                    # Handle side pot scenario
                    self.side_pots.append(self.manage_side_pots(player))
                    self.logging(f"Side pot created with {self.side_pot} chips due to all-in.")
                else:
                    self.current_highest_bet = all_in_amount
                self.pot += all_in_amount
                break
            elif 'bet' in action:
                try:
                    bet_amount = int(action.split('bet')[-1])
                    if bet_amount > self.current_highest_bet:
                        additional_bet = bet_amount - player.current_bet
                        if player.bet(additional_bet):
                            self.current_highest_bet = bet_amount
                            self.pot += additional_bet
                            self.logging(f"{player.name} raises to {bet_amount}. Pot size goes up to {self.pot}.\n")
                            # After action, update and send game state
                            active_betting = False
                            break
                        else:
                            message = "Not enough chips."
                    else:
                        message = "Raise must exceed the current highest bet."
                except ValueError:
                    message = "Please add a valid bet amount."
            else:
                print(f"Invalid action: {action}")

        active_players = [player for player in self.players.values() if player.in_game]
        if len(active_players) == 1:
            self.declare_winner()  # Only two players, other player wins            
        self.proceed_game()

    def manage_side_pots(self, all_in_player):
        all_in_amount = all_in_player.current_bet
        excess_amount = 0

        # Initialize side pots list if not already done
        if not hasattr(self, 'side_pots'):
            self.side_pots = []

        # Adjust existing side pots and main pot based on the all-in amount
        new_side_pots = []
        for side_pot in self.side_pots:
            if all_in_amount < side_pot['amount']:
                # Reduce the current side pot and create a new one if necessary
                excess_amount += side_pot['amount'] - all_in_amount
                side_pot['amount'] = all_in_amount
            new_side_pots.append(side_pot)

        # Add the all-in player to eligible players for all existing side pots up to their all-in amount
        for side_pot in new_side_pots:
            if all_in_player.id not in side_pot['eligible']:
                side_pot['eligible'].append(all_in_player.id)

        # Adjust the main pot and create a new side pot if there's excess
        if excess_amount > 0:
            new_side_pot = {
                'amount': excess_amount,
                'eligible': [player.id for player in self.players.values() if player.current_bet > all_in_amount and player.in_game]
            }
            new_side_pots.append(new_side_pot)

        # Update the side pots attribute
        self.side_pots = new_side_pots

        # Adjust the main pot
        self.pot -= excess_amount


def cards_to_img(cards_list):
    card_images = [f"{card}.png" for card in cards_list]
    return card_images


if __name__ == '__main__':

    game = Game()

    game.start_game()
    game.proceed_game()
    game.game_analysis()
    print(game.game_history)
    