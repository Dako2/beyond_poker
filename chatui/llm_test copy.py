# Set up OpenAI API key
import openai
import os 
import requests
from llama_index.core.chat_engine import SimpleChatEngine
from urllib.parse import quote
from game_tutorial import Game, convert_card_str_to_img_url, game_example

from llama_index.agent.openai import OpenAIAgent
import json
from typing import Sequence, List

from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage
from llama_index.core.tools import BaseTool, FunctionTool
from openai.types.chat import ChatCompletionMessageToolCall

import nest_asyncio
openai.api_key = os.getenv('OPENAI_API_KEY')

"""
**Prompt Generation for Poker Conversational Model**

1. Identify Natural Breakpoints: Read through the poker-related text and look for points where a question naturally leads to an answer or where topics shift.

2. Look for Questions and Answers: Identify sections with direct Q&A or implied questions and their corresponding answers.

3. Spot Transitional Phrases: Find words or phrases indicating shifts in topic or conclusion. Use them as breakpoints.

4. Understand Contextual Shifts: Recognize changes in context, especially when moving from rules to strategies or example plays.

5. Segment Example Plays: Break down play-by-play examples into individual moves or decision points.

6. Use Paragraphs and Headings: Utilize new paragraphs or section headings as indicators of topic shifts.

7. Create Prompt-Response Pairs: Form pairs by turning questions into prompts and answers into responses. Ensure clarity and context.

Remember to keep prompts concise and specific to guide the model in generating informative and relevant responses.

https://www.youtube.com/watch?v=nGnT7f7V-iE
"""
TEXAS_HOLDEM_ASSISTANT = "Your name is Eliza and you are professional Texas Hold'em Poker player and tutor."

nest_asyncio.apply()

llm = OpenAI(model="gpt-3.5-turbo-0613", max_tokens=150, temperature=0.9)

agent = OpenAIAgent.from_tools(
    [],
    llm=llm,
    verbose=True,
    system_prompt=TEXAS_HOLDEM_ASSISTANT,
)

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



# Define the base URL where the Flask app is running
base_url = 'http://localhost:3001'

# Example usage
#send_chat_message_from_url_input(base_url, 'hello! how are you doing? ')

print("Welcome to the Texas Hold'em Assistant! Let's start a game example of Texas Hold'em with the Beyond Expo tutor.")
cards, game_summary = game_example()
send_cards_api(cards)

game_summary += "I am player 1."

response = agent.chat(
    str(game_summary)
)

print(response)

while True:
    user_input = input("Please enter your query (or 'exit' to quit): ").strip().lower()
    if user_input == 'exit':
        print("Exiting...")
        break
    
    response = agent.chat(
        user_input
    )
    print(response)
    send_chat_message(base_url, response.response)
 