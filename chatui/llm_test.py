"""
**Prompt Generation f
https://www.youtube.com/watch?v=nGnT7f7V-iE
"""

# Set up OpenAI API key
import openai
import os
import requests
from urllib.parse import quote

from llama_index.agent.openai import OpenAIAgent
from typing import Sequence, List

from llama_index.llms.openai import OpenAI
from llama_index.core.tools import FunctionTool
import nest_asyncio
nest_asyncio.apply()

import base64
import requests
openai.api_key = os.getenv('OPENAI_API_KEY')

#from tts import TextToSpeech
#tts = TextToSpeech()

TEXAS_HOLDEM_ASSISTANT = "Your name is Eliza, a professional poker game player. \
you play and teach the game with the user Player 1. you always provide a useful \
question or response to carry on the conversation in the game.\n\n \
Example: \n \
A game start with your hands: Ace of Spades, and 2 of Spades. The user got his hand also. Now it's pre-flop.\
You made the move and throw a comment to ask the user to make his move (call, fold, raise) if the user doesn't know how to. \
The game has community cards of 2 of Clubs, Ace of Diamonds, and 10 of Clubs."

def game_state_calling():
    """query game state"""
    print("hello, this is triggered from chatgpt!")
    game_state = "check"
    return game_state

def function_to_tool(func):
    func_tool = FunctionTool.from_defaults(fn=func)
    return func_tool

class LLMPlayer():
    def __init__(self, ):
        self.llm = OpenAI(model="gpt-3.5-turbo-0613", max_tokens=150, temperature=0.9)
        self.agent = OpenAIAgent.from_tools(
            [],
            llm=self.llm,
            verbose=True,
            system_prompt=TEXAS_HOLDEM_ASSISTANT,
        )
        self.hand = []

    def renew_function_calling_tools(self, tools_list):
        self.agent = OpenAIAgent.from_tools(
            [function_to_tool(tool) for tool in tools_list],
            llm=self.llm,
            verbose=True,
            system_prompt=TEXAS_HOLDEM_ASSISTANT,
        )

    def get_chatgpt_response(self, prompt):
        response = self.agent.chat(prompt)
        print(response)
        return response.response
    
    def get_cards(self,):
        return self.hand
    
#<= get_chatgpt tool calling 

if __name__ == '__main__':

    llm = LLMPlayer()
    llm.renew_function_calling_tools([game_state_calling])

    while True:
        user_input = input("Please enter your query (or 'exit' to quit): ").strip().lower()
        if user_input == 'exit':
            print("Exiting...")
            break        
        response = llm.get_chatgpt_response(user_input)

    