from flask import Flask, render_template, request, jsonify, url_for
from flask_socketio import SocketIO, emit
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

@app.route('/chat_input/<message>')
def message_from_url_input(message):
    print("New player trigger received")
    # Use the message from the URL in the response
    response_message = f"system state: {message}"
    socketio.emit('receive_message', {'data': response_message})
    return jsonify({"status": "success", "message": response_message})

@app.route('/chat', methods=['POST'])
def message():
    # Extract message from JSON body of the request
    message_data = request.json
    message = message_data.get('message', 'No message received')
    print("New player trigger received")
    print(message)
    # Use the extracted message
    response_message = f"{message}"
    socketio.emit('receive_message', {'data': response_message})
    return jsonify({"status": "success", "message": response_message})

@socketio.on('connect')
def handle_connect():
    print('Client Connected')

@app.route('/new_player')
def trigger_redirect():
    print("New player trigger received")
    socketio.emit('redirect', {'url': '/welcome'})
    socketio.emit('receive_message', {'data': "Welcome to Beyond Expo Game!"})
    return jsonify({"status": "success", "message": "Redirect event triggered immediately"})

@app.route('/exit')
def trigger_redirect_exitgame():
    print("Exit game trigger received")
    socketio.emit('redirect', {'url': '/index'})
    return jsonify({"status": "success", "message": "Redirect event triggered immediately"})

if __name__ == '__main__':
    # Run the thread as a daemon so it exits when the main process does
    socketio.run(app, host='0.0.0.0', port=3001, debug=True)
