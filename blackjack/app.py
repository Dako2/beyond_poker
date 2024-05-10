from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import random
from llm import LLMPlayer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret'
socketio = SocketIO(app)

# Assuming LLMPlayer class is already defined and imported
jane = LLMPlayer(1, "Jane")

def get_deck():
    """ Create a new deck of cards """
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    return [{'rank': rank, 'suit': suit} for suit in suits for rank in ranks]

def shuffle_deck(deck):
    """ Shuffle the deck of cards """
    random.shuffle(deck)
    return deck

def deal_card(deck):
    """ Deal a single card from the deck """
    return deck.pop(0)

def calculate_score(cards):
    """ Calculate the score of the current hand """
    value = 0
    aces = 0
    for card in cards:
        rank = card['rank']
        if rank in 'TJQK':
            value += 10
        elif rank == 'A':
            aces += 1
        else:
            value += int(rank)
    # Value adjustments for aces
    for _ in range(aces):
        if value + 11 <= 21:
            value += 11
        else:
            value += 1
    return value

deck = shuffle_deck(get_deck())
players = {}
player_id = 1

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/welcome')
def game():
    return render_template('welcome.html')

@socketio.on('connect')
def handle_connect():
    emit('gameMessage', {'message': f'waiting for the start of the game...'}, room=request.sid)

@socketio.on('start_game')
def on_start_game():
    global deck
    if len(deck) < 20:  # Shuffle deck if low
        deck = shuffle_deck(get_deck())
    players[player_id] = {'hand': [], 'dealer_hand': [], 'score': 0, 'dealer_score': 0, 'status': 'playing'}
    # Deal initial cards
    for _ in range(2):
        players[player_id]['hand'].append(deal_card(deck))
        players[player_id]['dealer_hand'].append(deal_card(deck))
    players[player_id]['score'] = calculate_score(players[player_id]['hand'])
    players[player_id]['dealer_score'] = calculate_score(players[player_id]['dealer_hand'])
    # Show only one dealer card and player cards
    
    action_prompt = 'firstly state the action as <hit> or <stand>, then provide the response based on this action.'
    context = {
        'hand': players[player_id]['hand'],  # Example starting hand
        'dealer_hand': players[player_id]['dealer_hand'][0],
        'additional_context': action_prompt,
    }
    emit('deal_cards', {'hand': players[player_id]['hand'], 'score': players[player_id]['score'], 'dealer_card': players[player_id]['dealer_hand'][0]})
    response = jane.query_action(context)  # Jane decides her action at game start
    print(response)
    # Send the initial game state to the player
    emit('gameMessage', {'message': response})
    
@socketio.on('hit')
def on_hit():
    hand = players[player_id]['hand']
    hand.append(deal_card(deck))
    score = calculate_score(hand)
    players[player_id]['score'] = score
    if score > 21:
        players[player_id]['status'] = 'bust'
        emit('card_dealt', {'hand': hand, 'score': score})
        emit('game_over', {'message': 'Bust!', 'hand': hand, 'score': score, 'dealer_hand': players[player_id]['dealer_hand'], 'dealer_score': players[player_id]['dealer_score']})
    else:
        emit('card_dealt', {'hand': hand, 'score': score})
        action_prompt = 'The game continues. firstly state the action as <hit> or <stand>, then provide the response based on this action.'
        context = {
            'hand': hand,  # Example starting hand
            'dealer_hand': players[player_id]['dealer_hand'][0],
            'additional_context': action_prompt,
        }
        response = jane.query_action(context)  # Jane decides her action at game start
        print(response)

@socketio.on('stand')
def on_stand():
    player_score = players[player_id]['score']
    dealer_hand = players[player_id]['dealer_hand']
    dealer_score = players[player_id]['dealer_score']
    # Dealer hits until reaching 17 or higher
    print(player_score, dealer_hand, dealer_score)

    while dealer_score < 17:
        dealer_hand.append(deal_card(deck))
        dealer_score = calculate_score(dealer_hand)
    players[player_id]['dealer_score'] = dealer_score
    if dealer_score > 21 or player_score > dealer_score:
        result = 'You win!'
    elif player_score < dealer_score:
        result = 'Dealer wins!'
    else:
        result = 'It\'s a tie!'
    response = jane.query_action(result, role='chat')
    emit('gameMessage', {'message': response})
    emit('game_over', {'message': result, 'score': player_score, 'dealer_hand': dealer_hand, 'dealer_score': dealer_score})


@socketio.on('player_action')
def player_action(data):
    # Data contains player decisions and game state updates
    if data['player_id'] == jane.id:
        response = jane.query_action(data)
        emit('bot_action', {'action': jane.action, 'message': response})

if __name__ == '__main__':
    socketio.run(app, port=5002,debug=True)
