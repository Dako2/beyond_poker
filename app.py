from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit
import random
import os
from game_engine import Game, cards_to_img
from chatui.llm_test import LLMPlayer

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)  # Generates a random secret key
socketio = SocketIO(app, manage_session=False)  # Let Flask manage session instead of SocketIO

game = Game(max_players = 2)
llm = LLMPlayer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/table')
def board():
    return render_template('table.html')

@socketio.on('connect')
def handle_connect():
    emit('message', {'message': f'joining the game...'})

@socketio.on('disconnect')
def handle_disconnect():
    # Here you can handle the cleanup if necessary
    emit('message', {'message': 'Click <Connect> to join the game...'})

@socketio.on('connect_table')
def handle_initialize_table_cards():
    game.board_sid = request.sid
    emit('message', {'message': f'Game {game.game_id}'}, broadcast=True)
    emit('update_community_cards', {'cards': cards_to_img(['empty']*5)}, broadcast=True)  # Optionally, you can target only boards
    emit('prompt', {'prompt': game.log})

@socketio.on('join_game')
def on_join_game(): 
    player_id = 1
    game.add_player(player_id)  # Reconnect the existing player
    print(f"New player connected: {'player_id'}")
    emit('message', {'message': f'Welcome new player, waiting for the game start...'}, room=request.sid)
    emit('deal_cards', {'cards': cards_to_img(['empty','empty'])}, room=request.sid)
    game.bot_action()

@socketio.on('start_game')
def on_start_game():
    _, player_cards = game.start_game()
    print(player_cards)
    emit('deal_cards', {'cards': cards_to_img(player_cards)}, broadcast=True)
    emit('update_community_cards', {'cards': cards_to_img(game.community_cards)}, room=game.board_sid)
    emit('message', {'message': f'Game {game.game_id} {game.game_state} Pot ${game.pot}'}, broadcast=True)
    emit('prompt', {'prompt': game.log})
        

@socketio.on('deal_cards')
def on_deal_community_cards():
    game.deal_community_cards()
    print(cards_to_img(game.community_cards))
    try:
        emit('message', {'message': f'Game {game.game_id} {game.game_state} Pot ${game.pot}'}, broadcast=True)
        emit('update_community_cards', {'cards': cards_to_img(game.community_cards)}, broadcast=True)
    except:
        print("board not connected")
    emit('prompt', {'prompt': game.log})
    return game.community_cards
    
@socketio.on('place_bet')
def handle_place_bet(data):
    amount = data['amount']
    if game.player_bet('Player 1', amount):
        emit('message', {'message': f'Player 1 bet {amount}. current pot size {game.pot}'}, broadcast=True)
    else:
        emit('error', {'message': 'Bet not placed. Insufficient funds or invalid amount.'}, broadcast=True)
    emit('prompt', {'prompt': game.log})

    chat_response = llm.get_chatgpt_response(f"I bet {amount} chips.")
    emit('receive_chat_message', {'message': chat_response}, broadcast=True)

@socketio.on('fold_game')
def on_fold():
    print("folded")
    emit('deal_cards', {'cards': ['empty.png','empty.png']}, room=request.sid)
    emit('message', {'message': f'Player 1 fold. current pot size {game.pot}'}, broadcast=True)
    emit('prompt', {'prompt': game.log})
    
@socketio.on('check_game')
def on_check():
    print("check")
    game.player_call('Player 1')
    user_message = f'Player 1 check. current pot size {game.pot}'
    emit('message', {'message': user_message}, broadcast=True)
    emit('prompt', {'prompt': game.log})

@socketio.on('send_chat_message')
def handle_chat_message(data):
    user_message = data['message']
    print(f"Received message from player: {user_message}")

    chat_response = llm.get_chatgpt_response(user_message)
    emit('receive_chat_message', {'message': chat_response}, broadcast=True)

@socketio.on('update_logs')
def update_logs():
    """Send the latest logs to all clients."""
    logs = game.get_logs()
    emit('log_update', {'logs': logs}, broadcast=True)

llm.renew_function_calling_tools([on_start_game, on_deal_community_cards, handle_place_bet, on_check])

if __name__ == '__main__':
    socketio.run(app, host = '0.0.0.0', port = 3002, debug=True)
