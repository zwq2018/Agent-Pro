import json
import random
import rlcard
from rlcard.agents import RandomAgent
from rlcard.utils import get_device
from AgentPro.Blackjack.LLMAPIs import GPT35API
from AgentPro.Blackjack.LLMAPIs import GPT4API
from AgentPro.Blackjack.LLMAPIs import llama2_70b_chatAPI
from AgentPro.Blackjack.LLMAPIs import QwenAPI
import rlcard.envs


class Round:
    round = 0
    num_hit = 0
    num_stand = 0

    @staticmethod
    def reset():
        Round.round = 0


def play(game_num, model, game_style, storage_name):
    Round.reset()

    class LlmAgent(RandomAgent):

        def __init__(self, num_actions):
            super().__init__(num_actions)

        @staticmethod
        def step(state):
            Round.round += 1
            deal_card = state['raw_obs']['dealer hand']
            hand_card = state['raw_obs']['player0 hand']
            llm = find_model(model)
            p = []
            begin_info = "You are a player in blackjack. Please beat the dealer and win the game.\n"
            game_rule = "Game Rule:\n1. Please try to get your card total to as close to 21 as possible, without going over, and still having a higher total than the dealer.\n2. If anyone's point total exceeds 21, he or she loses the game. \n3. You can only choose one of the following two actions: {\"Stand\", \"Hit\"}. If you choose to Stand, you will stop taking cards and wait for the dealer to finish. If you choose to Hit, you can continue to take a card, but there is also the risk of losing the game over 21 points. \n4. After all players have completed their hands, the dealer reveals their hidden card. Dealers must hit until their cards total 17 or higher.\n"
            game_info = "The dealer's current card is {" + card2string(
                deal_card
            ) + "}. The dealer has another hidden card. You don't know what it is. Your current cards are {" + card2string(
                hand_card) + "}. "

            if game_style == 'Vanilla':
                p.append({"role": "system", "content": begin_info + game_rule})
                game_info += "Please output your action in following format: ###My action is {your action}, without any other text."
                p.append({"role": "user", "content": game_info})
            if game_style == 'Radical':
                begin_info = "You are an aggressive player of blackjack who likes to take risks to earn high returns. Please beat the dealer and win the game."
                p.append({"role": "system", "content": begin_info + game_rule})
                game_info += "Please output your action in following format: ###My action is {your action}, without any other text."
                p.append({"role": "user", "content": game_info})
            if game_style == 'ReAct':
                p.append({"role": "system", "content": begin_info + game_rule})
                game_info += "Please first think and reason about the current hand and then generate your action as follows: ###My thought is {Your Thought}. My action is {your action}."
                p.append({"role": "user", "content": game_info})
            if game_style == 'ReFlexion':
                p.append({"role": "system", "content": begin_info + game_rule})
                game_info += "Please first think and reason about the current hand and then generate your action as follows: ###My thought is {Your Thought}. My action is {your action}."
                p.append({"role": "user", "content": game_info})
                llm_res = llm.response(p)
                p.append({"role": "assistant", "content": llm_res})
                reflexion_info = "Please carefully check the response you just output, and then refine your answer . The final output is also in following format: ###My thought is {Your Thought}. My action is {your action}."
                p.append({"role": "user", "content": reflexion_info})
            if game_style == 'AgentPro':
                begin_info = "You are an aggressive player of blackjack who likes to take risks to earn high returns. Please beat the dealer and win the game."
                p.append({"role": "system", "content": begin_info + game_rule})
                game_info += "Please read the behavoiral guideline and world modeling carefully . Then you should analyze your own cards and your strategies in Self-belief and then analyze the dealer cards in World-belief. Lastly, please select your action from {\"Stand\",\"Hit\"}.### Output Format: Self-Belief is {Belief about youself}. World-Belief is {Belief about the dealer}. My action is {Your action}. Please output in the given format."
                p.append({"role": "user", "content": game_info})
            llm_res = llm.response(p)
            p.append({"role": "assistant", "content": llm_res})
            filename = storage_name + '.json'
            with open(filename, 'a') as file:
                json.dump(p, file, indent=4)
                # file.write(json_str + '\n')
            choice = -1
            if extract_choice(llm_res) == "hit":
                choice = 0
            elif extract_choice(llm_res) == "stand":
                choice = 1
            else:
                choice = -1
            return choice

    def find_model(model):
        if model == "gpt-3.5":
            return GPT35API()
        if model == "gpt-4":
            return GPT4API()
        if model == "Llama70b":
            return llama2_70b_chatAPI()
        if model == "Qwen":
            return QwenAPI()

    def extract_choice(text):
        text = to_lower(text)
        last_hit_index = text.rfind("hit")
        last_stand_index = text.rfind("stand")
        if last_hit_index > last_stand_index:
            return "hit"
        elif last_stand_index > last_hit_index:
            return "stand"
        else:
            return None

    def to_lower(str):
        lowercase_string = str.lower()
        return lowercase_string

    def card2string(cardList):
        str = ''
        str = ','.join(cardList)
        str = str.replace('C', 'Club ')
        str = str.replace('S', 'Spade ')
        str = str.replace('H', 'Heart ')
        str = str.replace('D', 'Diamond ')
        str = str.replace('T', '10')
        return str

    device = get_device()
    num_players = 1
    env = rlcard.make('blackjack',
                      config={
                          'game_num_players': num_players,
                          "seed": random.randint(0, 10**10)
                      })

    llm_agent = LlmAgent(num_actions=env.num_actions)

    env.set_agents([llm_agent])

    def play_game(env):
        trajectories, payoffs = env.run(is_training=False)
        if len(trajectories[0]) != 0:
            final_state = []
            action_record = []
            state = []
            _action_list = []

            for i in range(num_players):
                final_state.append(trajectories[i][-1])
                state.append(final_state[i]['raw_obs'])

            action_record.append(final_state[i]['action_record'])
            for i in range(1, len(action_record) + 1):
                _action_list.insert(0, action_record[-i])

        Round.round += 1
        res_str = ('dealer {}, '.format(state[0]['state'][1]) +
                   'player {}, '.format(state[0]['state'][0]))
        if payoffs[0] == 1:
            final_res = "win."
        elif payoffs[0] == 0:
            final_res = "draw."
        elif payoffs[0] == -1:
            final_res = "lose."
        p = ({"final cards": res_str, "final results": final_res})
        with open(storage_name + ".json", 'a', encoding='utf-8') as file:
            json.dump(p, file, indent=4)
        return env.get_payoffs()

    num_matches = game_num

    for i in range(num_matches):
        play_game(env)
