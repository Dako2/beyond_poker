"""
**Prompt Generation f
https://www.youtube.com/watch?v=nGnT7f7V-iE
"""
# Set up OpenAI API key
import openai
import os 
import requests
from llama_index.core.chat_engine import SimpleChatEngine
from urllib.parse import quote
from game_engine import Game

from llama_index.agent.openai import OpenAIAgent
import json
from typing import Sequence, List

from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage
from llama_index.core.tools import BaseTool, FunctionTool
from openai.types.chat import ChatCompletionMessageToolCall
import nest_asyncio

import base64
import requests

openai.api_key = os.getenv('OPENAI_API_KEY')

TEXAS_HOLDEM_ASSISTANT = """Your name is Eliza, a professional poker game player. you play and teach the game with the Player1. You are provided with a game context and make an action correspondingly

Example: 
A game start with your hands: Ace of Spades, and 2 of Spades. The user got his hand also. Now it's pre-flop. You made the move and throw a comment to ask the user to make his move (call, fold, raise) if the user doesn't know how to. 
The game has community cards of 2 of Clubs, Ace of Diamonds, and 10 of Clubs. 
"""
nest_asyncio.apply()

def send_cards_api(cards, base_url='http://localhost:3002'):
    try:
        url = f"{base_url}/deal_cards"
        # Ensure the payload is structured as expected by the server
        payload = {'data': cards}
        # Send the POST request with JSON data
        response = requests.post(url, json=payload)
        
        # Check if the request was successful
        if response.status_code == 200:
            print("Cards sent successfully!")
            print("Response:", response.json())
        else:
            print("Failed to send cards. Status code:", response.status_code)
            print("Response text:", response.text)  # Additional debug information
    except Exception as e:
        print("An error occurred:", e)

def send_chat_message(base_url, message):
    try:
        url = f"{base_url}/chat"
        # Send the POST request with JSON data
        response = requests.post(url, json={'message': message})
        # Check if the request was successful
        if response.status_code == 200:
            print("Message sent successfully!")
            print("Response:", response.json())
        else:
            print("Failed to send message. Status code:", response.status_code)
    except Exception as e:
        print("An error occurred:", e)

def send_chat_message_from_url_input(base_url, message):
    try:
        # Encode the message to handle special characters
        encoded_message = quote(message)
        # Construct the URL with the encoded message
        url = f"{base_url}/chat_input/{encoded_message}"
        # Send the GET request
        response = requests.get(url)
        # Check if the request was successful
        if response.status_code == 200:
            print("Message sent successfully!")
            print("Response:", response.json())
        else:
            print("Failed to send message. Status code:", response.status_code)
    except Exception as e:
        print("An error occurred:", e)

def multiply(x, y):
    """Multiple two integers and returns the result integer"""
    return x * y
multiply_tool = FunctionTool.from_defaults(fn=multiply)

def add(x, y):
    """Add two integers and returns the result integer"""
    return x + y
add_tool = FunctionTool.from_defaults(fn=add)

def extract_current_game_state():
    """extract the current game state from the game engine"""
    return game.get_game_state()
extract_current_game_state_tool = FunctionTool.from_defaults(fn=extract_current_game_state)




llm = OpenAI(model="gpt-3.5-turbo-0613", max_tokens=150, temperature=0.9)
game = Game(num_players = 2)

game.add_player(1)
game.start_game()

agent = OpenAIAgent.from_tools(
    [multiply_tool, add_tool, extract_current_game_state_tool],
    llm=llm,
    verbose=True,
    system_prompt=TEXAS_HOLDEM_ASSISTANT,
)

# Define the base URL where the Flask app is running
base_url = 'http://localhost:3001'

# Example usage
#send_chat_message_from_url_input(base_url, 'hello! how are you doing? ')

game_summary = game.log

response = agent.chat(
    str(game_summary)
)

while True:
    user_input = input("Please enter your query (or 'exit' to quit): ").strip().lower()
    if user_input == 'exit':
        print("Exiting...")
        break
    
    response = agent.chat(
        user_input
    )
    print(response)

    #tts.synthesize_text(response.response)
    send_chat_message(base_url, response.response)
 

 