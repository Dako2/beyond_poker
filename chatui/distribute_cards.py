# Set up OpenAI API key
import openai
import os 
import requests
from llama_index.core.chat_engine import SimpleChatEngine
from urllib.parse import quote
from game_tutorial import Game, convert_card_str_to_img_url, game_example, game_example2

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

from tts import TextToSpeech
tts = TextToSpeech()

openai.api_key = os.getenv('OPENAI_API_KEY')

# OpenAI API Key
api_key = "YOUR_OPENAI_API_KEY"

"""
**Prompt Generation f
https://www.youtube.com/watch?v=nGnT7f7V-iE
"""

TEXAS_HOLDEM_ASSISTANT = "Your name is Eliza and you are professional Texas Hold'em Poker player and tutor. Based on the user's query, always follow up with a new question."

nest_asyncio.apply()

llm = OpenAI(model="gpt-3.5-turbo-0613", max_tokens=150, temperature=0.9)

agent = OpenAIAgent.from_tools(
    [],
    llm=llm,
    verbose=True,
    system_prompt=TEXAS_HOLDEM_ASSISTANT,
)


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
        
cards, game_summary = game_example2()

