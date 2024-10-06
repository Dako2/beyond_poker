import openai
import os
from urllib.parse import quote
import time 
import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
import random
import json
from typing import Sequence, List

from llama_index.agent.openai import OpenAIAgent
from llama_index.core.indices.struct_store import JSONQueryEngine

from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage
from llama_index.core.tools import BaseTool, FunctionTool
from llama_index.core import PromptTemplate
from openai.types.chat import ChatCompletionMessageToolCall

from termcolor import colored  
import openai
from tts_openai import tts_openai_replay, tts_openai_to_wav_files

from prompt import TEXAS_HOLDEM_PLAYER
from typing import List
from pydantic import BaseModel

import nest_asyncio
nest_asyncio.apply()

openai.api_key = os.getenv('OPENAI_API_KEY')

def pretty_print_conversation(messages):
    role_to_color = {
        "system": "red",
        "user": "green",
        "assistant": "blue",
        "function": "magenta",
    }
    
    for message in messages:
        if message["role"] == "system":
            print(colored(f"system: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "user":
            print(colored(f"user: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and message.get("function_call"):
            print(colored(f"assistant: {message['function_call']}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and not message.get("function_call"):
            print(colored(f"assistant: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "function":
            print(colored(f"function ({message['name']}): {message['content']}\n", role_to_color[message["role"]]))

class GameAction(BaseModel):
    """Data model for game actions, including bet, fold, call, raise, and check. if bet, then assign the amount of betting."""
    action: str
    amount: int = 0

def function_to_tool(func):
    func_tool = FunctionTool.from_defaults(fn=func)
    return func_tool

class LLMPlayer():
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

        self.log = ""
        self.action = ""
    
        self.llm = OpenAI(model="gpt-3.5-turbo-0613", max_tokens=75, temperature=0.9)
        
        self.agent = OpenAIAgent.from_tools(
            [],
            llm=self.llm,
            verbose=True,
            system_prompt=TEXAS_HOLDEM_PLAYER,
        )
        self.tools_list = [self.bet, self.fold, self.call, self.allin, self.check]

        self.fmt_prompt = ""

    def logging(self, log_str):
        self.log += log_str
        self.action = log_str

    def update_prompt_template(self, action, content, knowing_game_state_str, knowing_game_history_str):
        query_prompt_tmpl_str = """\
Your hand is: {hand_str}, The game is in the state: {game_state_str}.\
Then, You have decided to make a move:{action}, and provide the response based on this move (maybe also based on the game history).\n
===========Game History============\n
{history_str}
"""
        query_prompt_tmpl_str = PromptTemplate(query_prompt_tmpl_str)

        self.fmt_prompt = query_prompt_tmpl_str.format(
            hand_str=self.get_hand_str(),
            game_state_str=knowing_game_state_str,
            history_str=knowing_game_history_str,
            content=content,
            action=action,
            )
        print(self.fmt_prompt)

    def renew_function_calling_tools(self, tools_list):
        if not tools_list:
            self.agent = OpenAIAgent.from_tools(
                [function_to_tool(x) for x in tools_list],
                llm=self.llm,
                verbose=True,
                system_prompt=TEXAS_HOLDEM_PLAYER,
            )
            print(f"renew_function_calling_tools:{tools_list}")

    def query_action(self, content, game_state="", game_history="", source="user"):
        if self.autobot:
            time.sleep(3)
            self.action = random.choice(['check', 'call', 'bet'])
            if self.action == 'bet':
                self.action += str(random.randrange(5, int(self.chips//2), 5))
            
            return self.action
        
        if source == "game_engine":
            self.action = random.choice(['check', 'call', 'bet'])
            if self.action == 'bet':
                self.action += str(random.randrange(5, int(self.chips), 5))
            self.update_prompt_template(self.action, content, game_state, game_history)
            print(self.fmt_prompt)
            response = self.agent.chat(self.fmt_prompt)
            tts_openai_replay(response.response)

            print("xxxx")
            print(response.response)
            print("xxxx")
            return response.response
        elif source == "review":
            content = "this is a review of the hand power of the player:\n"+content
            content += "\n Give a feedback based by comparing the hand power with the real game history:\n"
            response = self.agent.chat(content)
            tts_openai_replay(response.response)
            print("xxxx")
            print(response.response)
            print("xxxx")
            return response.response
        else:
            response = self.agent.chat(content, tool_choice="auto")
            tts_openai_replay(response.response)
            return response.response
   
    def get_hand_str(self,):
        return str(self.hand_str)

    def get_game_str(self,game):
        return game.game_state

    def get_game_hisotry_str(self,game):
        return game.game_history

    def bet(self, amount):
        """raise the bet by the given amount."""
        if amount <= self.chips:
            self.chips -= amount
            self.current_bet += amount
            self.logging(f"{self.name} bet additional {amount} with current total bet of {self.current_bet}\n")
            self.amount = amount
            self.action = f"bet{self.amount}"
            print(f"{self.name}--------=++++++++++++++=-------- {self.action} --------=++++++++++++++=--------")
            return True
        else:
            self.amount = self.chips
            self.current_bet += self.amount
            self.chips -= self.amount
            self.action = f"allin"
            print(f"{self.name}--------=++++++++++++++=-------- {self.action} --------=++++++++++++++=--------")
        
            return True
    
    def allin(self,):
        """all in the current bet."""
        if self.bet(self.chips):
            self.logging(f"{self.name} all in!\n")
            self.action = "allin"
        print(f"{self.name}--------=++++++++++++++=-------- {self.action} --------=++++++++++++++=--------")

    def fold(self):
        """fold the game."""
        self.in_game = False
        self.action = "fold"
        print(f"{self.name}--------=++++++++++++++=-------- {self.action} --------=++++++++++++++=--------")
        

    def call(self):
        """call the current bet."""
        self.action = "call"
        print(f"{self.name}--------=++++++++++++++=-------- {self.action} --------=++++++++++++++=--------")


    def check(self):
        """check the current hand."""
        self.action = "check"
        print(f"{self.name}--------=++++++++++++++=-------- {self.action} --------=++++++++++++++=--------")

    def get_updates(self, game_updates = ""):
        return game_updates
    
if __name__ == '__main__':
 
    eliza = LLMPlayer(1, 'Eliza', autobot=True)
    while True:
        user_input = input("Please enter your query (or 'exit' to quit): ").strip().lower()
        if user_input == 'exit':
            print("Exiting...")
            break
        response = eliza.query_action(user_input, "", "", source="user")
        tts_openai_replay(response)
 
 