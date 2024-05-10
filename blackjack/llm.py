import openai
import os
import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
from llama_index.agent.openai import OpenAIAgent
from llama_index.llms.openai import OpenAI
from llama_index.core import PromptTemplate
import threading

import openai
from tts_openai import start_tts_async, stop_audio

import nest_asyncio
nest_asyncio.apply()

openai.api_key = os.getenv('OPENAI_API_KEY')
BLACKJACK_PLAYER = f"Your name is Jane, and you are a Blackjack game player and tutor with a colorful personality. \
You will be given your hand cards and game state information, \
and you can hit, or stand. You always provide a playful \
response to carry on some conversation in the game. \n"

context_tmpl_str = """\
It's Black Jack game, the goal is to be as close to 21 as possible but not over. Your hand is: {hand_str}, Dealer's hand is: {dealer_hand_str} and hidden cards.\
Then, You have decided to make a move: <hit> or <stand>, and provide the tutor response \
on why you made this move.\n
===========more context============\n
{additional_context}
"""

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

        self.system_prompt = BLACKJACK_PLAYER
        self.context_tmpl_str = PromptTemplate(context_tmpl_str)
    
        self.llm = OpenAI(model="gpt-3.5-turbo-0613", max_tokens=125, temperature=0.9)
        
        self.agent = OpenAIAgent.from_tools(
            [],
            llm=self.llm,
            verbose=True,
            system_prompt=self.system_prompt,
        )

    def update_prompt_template(self, context):
        final_prompt_template = PromptTemplate("Here is the status of the game: {context}")
        final_prompt = final_prompt_template.format(
            context=context
            )
        print(final_prompt)
        return final_prompt
    
    def query_action(self, context, role="play"):
        stop_audio()
        if role == "play":
            hand_str = context.get('hand', 'Unknown hand')
            dealer_hand_str = context.get('dealer_hand', 'Unknown dealer hand')
            additional_context = context.get('additional_context', 'No additional context provided.')

            context_formatted = self.context_tmpl_str.format(
                hand_str=hand_str,
                dealer_hand_str=dealer_hand_str,
                additional_context=additional_context,
            )
            final_prompt = self.update_prompt_template(context_formatted)

            response = self.agent.chat(final_prompt)
            print("Model Response:")
            print(response.response)

            start_tts_async(response.response)

            if "hit" in response.response.lower():
                self.action = "hit"
            elif "stand" in response.response.lower():
                self.action = "stand"
            else:
                self.action = "unknown"
                logging.warning("Action not clear from the model's response.")
        else: #just chat
            self.action = "unknown"
            response = self.agent.chat(str(context))
            print("Model Response:")
            print(response.response)            
            start_tts_async(response.response)

            logging.warning("Role not clear for the model's response.") 

        return response.response

if __name__ == "__main__":
    jane = LLMPlayer(1, "Jane")
    jane.query_action({'hand': '2♠ 3♠', 'dealer_hand': '5♠ [hidden card]', 'additional_context': 'firstly state the action as <hit> or <stand>, then provide the response based on this action.'})