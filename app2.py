import eventlet
eventlet.monkey_patch()  # Crucial for making standard I/O operations non-blocking

from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit
import random
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)  # Generates a random secret key
socketio = SocketIO(app, manage_session=False, async_mode='eventlet')  # Let Flask manage session instead of SocketIO

from game_engine import Game, cards_to_img, Player
from llm_test import LLMPlayer

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/table')
def board():
    return render_template('table.html')

@socketio.on('connect')
def handle_connect():
    emit('gameMessage', {'message': f'joining the game...'}, room=request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    # Here you can handle the cleanup if necessary
    emit('gameMessage', {'message': 'diconnected...'}, room=request.sid)

@socketio.on('join_game')
def on_join_game(): 
    print(f"New player connected: {'player_id'}")
    emit('gameMessage', {'message': f'Welcome new player, waiting for the game start...'}, room=request.sid)
    emit('deal_player_cards', {'cards': cards_to_img(['BACK','BACK'])}, room=request.sid)

@socketio.on('connect_table')
def handle_initialize_table_cards():
    game.board_sid = request.sid
    emit('update_community_cards', {'cards': cards_to_img(['BACK']*5)}, broadcast=True)  # Optionally, you can target only boards

@socketio.on('start_game')
def on_start_game():
    """start the game and deal the cards to all players"""
    print("starting the game")
    game.start_game()
    player_cards = human.hand_str
    print(player_cards)
    emit('deal_player_cards', {'cards': cards_to_img(player_cards)}, broadcast=True)
    board = [card for card in game.community_cards]
    print(cards_to_img(board))
    emit('gameMessage', {'message': f'Game started.'}, room=request.sid)
    
    emit('update_community_cards', {'cards': cards_to_img(board)}, room=game.board_sid)
    emit('gameStatus', {'message': f'Game #{game.game_id}, Pot Size ${game.pot}, Next move: {game.get_current_player().name}'}, broadcast=True)
    #on_deal_community_cards()

@socketio.on('deal_cards')
def on_deal_community_cards():
    game.proceed_game()

    board = [card for card in game.community_cards]
    print(cards_to_img(board))
    try:
        emit('update_community_cards', {'cards': cards_to_img(board)}, room=game.board_sid)
        emit('gameStatus', {'message': f'Game #{game.game_id}, Pot Size ${game.pot}, Next move: {game.get_current_player().name}'}, broadcast=True)
    except:
        print("board not connected")
    
    return game.community_cards

@socketio.on('action')
def handle_action(data):
    try:
        action = data['action']
        print("----from client----->", action)

        # Validate action
        if action not in ['fold', 'check', 'bet', 'call', 'allin']:
            raise ValueError(f"Invalid action: {action}")

        if action == 'bet':
            amount = int(data['amount'])
            if amount <= 0:
                raise ValueError("Bet amount must be positive")
            human.current_action = f"bet{amount}"
            print("betting amount", amount)
        else:
            human.current_action = action
        
        human.action_event.set()  # Trigger the event to unblock `wait_for_action`

        emit('gameStatus', {'message': f'Game #{game.game_id}, Pot Size ${game.pot}, {game.game_state} Next move: {game.get_current_player().name}'}, broadcast=True)
        emit('gameMessage', {'message': f'Your action: {action}'}, broadcast=True)
        
    except Exception as e:
        print(f"Error handling action: {e}")
        emit('gameMessage', {'message': str(e)}, room=request.sid)

@socketio.on('send_chat_message')
def handle_chat_message(data):
    user_message = data['message']
    print(f"Received message from player: {user_message}")

    chat_response = game.players['Player 1'].query_action(user_message, source = "user")
    emit('receive_chat_message', {'message': chat_response}, broadcast=True)

@socketio.on('update_logs')
def update_logs():
    """Send the latest logs to all clients."""
    logs = game.get_logs()
    emit('log_update', {'logs': game.game_history}, broadcast=True)

if __name__ == '__main__':
    eliza = LLMPlayer(1, 'Eliza', autobot=True)
    human = Player(2, 'Human', autobot=False)

    tool_list =[on_start_game, on_deal_community_cards]
    eliza.renew_function_calling_tools(tool_list)

    game = Game(eliza, human)

    socketio.run(app, host = '0.0.0.0', port = 3002, debug=True)
