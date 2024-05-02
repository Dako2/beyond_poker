from treys import Card as TreyCard
from treys import Evaluator as TreyEvaluator
from treys import Deck as TreyDeck

# Abbreviation mappings
suit_abbreviations = {
    'Hearts': 'h',
    'Diamonds': 'd',
    'Clubs': 'c',
    'Spades': 's'
}
rank_abbreviations = {
    '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', 
    '7': '7', '8': '8', '9': '9', '10': 'T', 
    'Jack': 'J', 'Queen': 'Q', 'King': 'K', 'Ace': 'A'
}

PNG_DECK_MAPPING = {
    '2C': './cards_png/face/2C@1x.png',
    '2D': './cards_png/face/2D@1x.png',
    '2H': './cards_png/face/2H@1x.png',
    '2S': './cards_png/face/2S@1x.png',
    '3C': './cards_png/face/3C@1x.png',
    '3D': './cards_png/face/3D@1x.png',
    '3H': './cards_png/face/3H@1x.png',
    '3S': './cards_png/face/3S@1x.png',
    '4C': './cards_png/face/4C@1x.png',
    '4D': './cards_png/face/4D@1x.png',
    '4H': './cards_png/face/4H@1x.png',
    '4S': './cards_png/face/4S@1x.png',
    '5C': './cards_png/face/5C@1x.png',
    '5D': './cards_png/face/5D@1x.png',
    '5H': './cards_png/face/5H@1x.png',
    '5S': './cards_png/face/5S@1x.png',
    '6C': './cards_png/face/6C@1x.png',
    '6D': './cards_png/face/6D@1x.png',
    '6H': './cards_png/face/6H@1x.png',
    '6S': './cards_png/face/6S@1x.png',
    '7C': './cards_png/face/7C@1x.png',
    '7D': './cards_png/face/7D@1x.png',
    '7H': './cards_png/face/7H@1x.png',
    '7S': './cards_png/face/7S@1x.png',
    '8C': './cards_png/face/8C@1x.png',
    '8D': './cards_png/face/8D@1x.png',
    '8H': './cards_png/face/8H@1x.png',
    '8S': './cards_png/face/8S@1x.png',
    '9C': './cards_png/face/9C@1x.png',
    '9D': './cards_png/face/9D@1x.png',
    '9H': './cards_png/face/9H@1x.png',
    '9S': './cards_png/face/9S@1x.png',
    'TC': './cards_png/face/TC@1x.png',
    'TD': './cards_png/face/TD@1x.png',
    'TH': './cards_png/face/TH@1x.png',
    'TS': './cards_png/face/TS@1x.png',
    'JC': './cards_png/face/JC@1x.png',
    'JD': './cards_png/face/JD@1x.png',
    'JH': './cards_png/face/JH@1x.png',
    'JS': './cards_png/face/JS@1x.png',
    'QC': './cards_png/face/QC@1x.png',
    'QD': './cards_png/face/QD@1x.png',
    'QH': './cards_png/face/QH@1x.png',
    'QS': './cards_png/face/QS@1x.png',
    'KC': './cards_png/face/KC@1x.png',
    'KD': './cards_png/face/KD@1x.png',
    'KH': './cards_png/face/KH@1x.png',
    'KS': './cards_png/face/KS@1x.png',
    'AC': './cards_png/face/AC@1x.png',
    'AD': './cards_png/face/AD@1x.png',
    'AH': './cards_png/face/AH@1x.png',
    'AS': './cards_png/face/AS@1x.png',
    'BACK': './cards_png/back/bicycle_blue@1x.png',
}

def convert_card_str_to_img_url(abbr):
    return '/static/'+PNG_DECK_MAPPING[abbr.upper()][2:]

def convert_card_str_to_abbr(suit, rank):
    # Convert the suit and rank to their abbreviations
    return rank_abbreviations[rank]+suit_abbreviations[suit]

def convert_card_abbr_to_str(abbr):
    # Inverting dictionaries
    inverted_suit_abbreviations = {v: k for k, v in suit_abbreviations.items()}
    inverted_rank_abbreviations = {v: k for k, v in rank_abbreviations.items()}
    # Convert the suit and rank to their abbreviations
    return inverted_rank_abbreviations[abbr[0]]+' of '+ inverted_suit_abbreviations[abbr[1]]

class Player:
    def __init__(self, id, name, chips=1000):
        self.id = id
        if name:
            self.player_name = name
        else:
            self.player_name = f"Player {id}"

        self.hand = []
        self.hand_str = "" # 2 of Clubs, 3 of Hearts, 4 of Spades, 5 of Diamonds
        self.hand_abbr = "" # 2c, 3h, 4s, 5d
        self.hand_score = -1 # Default value -1 means the score hasn't been calculated yet

        self.chips = chips
        self.current_bet = 0

        self.actions = []
        self.last_action = None
        self.in_game = 1  # True if the player hasn't folded yet

    def show(self,):
        for card_int in self.hand:
            self.hand_str += "\""+convert_card_abbr_to_str(TreyCard.int_to_str(card_int)) + "\"" + ", "
        print(self.player_name + " hand: " + self.hand_str)
        return self.player_name + " hand: "  +self.hand_str  + "\n"

class Table:
    def __init__(self, num_players):
        self.deck = TreyDeck() # 52 cards
        self.num_players = num_players # players
        self.players = [] #player list
        self.board = self.deck.draw(5) #
        self.board_str = ""
        self.show()

    def show(self,):
        self.board_str = ""
        for card_int in self.board:
            self.board_str += "\"" + convert_card_abbr_to_str(TreyCard.int_to_str(card_int))  + "\"" + ", "
        return "Board: " + str(self.board_str) + "\n"
    

class Game:
    def __init__(self) -> None:
        self.log = ""
        self.evaluator = TreyEvaluator()
        self.num_players = 4
        self.table = Table(4)
        self.players = []
        self.state = "pre-flop"
        
        for i in range(self.num_players):
            self.player = Player(i, f"Player {i+1}")
            self.player.hand = self.table.deck.draw(2)
            self.player.hand_score = self.evaluator.evaluate(self.player.hand, self.table.board)
            self.players.append(self.player)

    def start_game(self,):
        print("board:")
        TreyCard.print_pretty_cards(self.table.board)
        self.log += "board: " + self.table.show()

        for player in self.players:
            print(f"{player.player_name} hand:")
            TreyCard.print_pretty_cards(player.hand)
            self.log += player.show()

        hands = [player.hand for player in self.players]
        self.log += self.evaluator.hand_summary(self.table.board, hands)

        return self.log
        
    def next_cards(self,):
        if self.game.board():
            pass
        
def convert_int_to_str_cards(cards):
    output = []
    for card in cards:
        output.append(TreyCard.int_to_str(card).upper())
    return output

def game_example():
    g = Game()
    g.start_game()


    board_cards = convert_int_to_str_cards(g.table.board)

    player_hands = [convert_int_to_str_cards(g.players[x].hand) for x in range(g.num_players)]

    cards_to_display_list = []
    cards_to_display_dict = {}


    for i, hand in enumerate(player_hands):
        for x, card in enumerate(hand):
            cards_to_display_dict['card_place_id'] = 'cardPlaceholder_player%d_%d'%(i+1, x+1)
            cards_to_display_dict['card_png_filepath'] = convert_card_str_to_img_url(card)
            cards_to_display_dict['card_data'] = ''
            cards_to_display_list.append(cards_to_display_dict.copy())
            cards_to_display_dict.clear()

    for i, card in enumerate(board_cards):
        cards_to_display_dict['card_place_id'] = 'cardPlaceholder_dealer_%d'%(i+1)
        cards_to_display_dict['card_png_filepath'] = convert_card_str_to_img_url(card)
        cards_to_display_dict['card_data'] = ''
        cards_to_display_list.append(cards_to_display_dict.copy())
        cards_to_display_dict.clear()

    print(cards_to_display_list)
    return cards_to_display_list, g.log

def game_example2():
    g = Game()
    g.start_game()

    board_cards = convert_int_to_str_cards(g.table.board)
    player_hands = [convert_int_to_str_cards(g.players[x].hand) for x in range(g.num_players)]

    all_cards_display_dict = {}

    # Distribute cards to each player
    for i, hand in enumerate(player_hands):
        player_key = f'player_{i+1}'
        player_cards = []
        for x, card in enumerate(hand):
            card_details = {
                'card_place_id': f'cardPlaceholder_player{i+1}_{x+1}',
                'card_png_filepath': convert_card_str_to_img_url(card),
                'card_data': ''
            }
            player_cards.append(card_details)
        all_cards_display_dict[player_key] = player_cards

    # Add dealer cards
    dealer_cards = []
    for i, card in enumerate(board_cards):
        card_details = {
            'card_place_id': f'cardPlaceholder_dealer_{i+1}',
            'card_png_filepath': convert_card_str_to_img_url(card),
            'card_data': ''
        }
        dealer_cards.append(card_details)
    all_cards_display_dict['dealer'] = dealer_cards

    print(all_cards_display_dict)
    return all_cards_display_dict, g.log
