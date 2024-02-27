import json, re, os
from AgentPro.LimitTexasHoldem.LLM import LLM
from AgentPro.LimitTexasHoldem.believe import Believe

DEFAULT_CONFIG = {
    "is_self_model": False,
    "is_believe": False,
    "is_analogy": False,
    "is_summarize": False
}


class LimitTexasHoldemAgent(LLM):

    def __init__(self,
                 index_player,
                 LLM_model="gpt-3.5-turbo",
                 key="",
                 config={}):
        """
        Args:
            index_player (int): index of of the current player
            num_players (int): number of players
            gpt_model (str, optional): the type of gpt model. Defaults to "gpt3.5".
            config (dict, optional): module enabling instructions. 
                Defaults to { 
                    "is_analyse_agent": False, 
                    "is_analyse_cards": False, 
                }.
        """
        self.use_raw = True
        self.stage = {0: "Preflop", 3: "Flop", 4: "Turn", 5: "River"}
        self.state = []
        self.self_model = ""
        self.system_information = ""
        self.game_information = ""
        self.action_record = ""
        self.LLM_model = LLM_model
        self.key = key

        super().__init__("", LLM_model, key)
        self.index_player = index_player
        self.num_players = -1
        self.be = None
        _config = DEFAULT_CONFIG
        for key in config.keys():
            if key in _config.keys():
                _config[key] = config[key]
        self.is_self_model = _config["is_self_model"]
        self.is_believe = _config["is_believe"]
        self.is_analogy = _config["is_analogy"]
        self.is_summarize = _config["is_summarize"]
        self.is_update_analogy = True

    def update_agent(self, version, num_players):
        self.version = version
        self.num_players = num_players
        self.system_information = f"In this Limit Texas poker game, there are {num_players} players from 0 to {num_players-1}, and your identity is player {self.index_player}. The number of chips every player has is infinite. You just need to win more chips in the competition as much as possible."
        self.folder = f"save/{version}/" + self.LLM_model
        if os.path.exists(self.folder + ".json") is not True:
            with open(self.folder + ".json", 'w') as f:
                json.dump([], f)
        if os.path.exists(self.folder + '_belief_log.json') is not True:
            with open(self.folder + '_belief_log.json', 'w') as f:
                json.dump([], f)
        self.address = self.folder + '.json'
        self.be = Believe(self.folder + '.json',
                          self.folder + '_belief_log.json', self.index_player,
                          self.LLM_model, self.key)
        if self.is_believe:
            self.belief, self.summary = self.be.load_log()

    def generate_game_information(self):
        """generate game information base on the state

        Returns:
            str: game information
        """
        game_information = ""
        if self.state == []:
            raise Exception("STATE IS NONE.")
        else:
            state = self.state["raw_obs"]
            hand = state["hand"]
            public_cards = state["public_cards"]
            all_chips = state["all_chips"]
            legal_actions = state["legal_actions"]
            game_information = f"Now your hand is {hand}, and the community cards is {public_cards}. "
            game_information += f"The number of chips all players have invested is {all_chips}. "
            game_information += ''
            game_information += f"the actions you can choose are {legal_actions}. "
            if self.action_record != "":
                game_information += "Currently, " + self.action_record
        return game_information

    def step(self, state):
        self.state = state
        action = self.run()
        return action

    def run(self):
        legal_actions = self.state["raw_obs"]["legal_actions"]
        game_information = self.generate_game_information()
        ques = f"{game_information}"
        if self.is_analogy and self.is_update_analogy:
            with open("AgentPro\LimitTexasHoldem\example.json", 'r') as f:
                games = json.load(f)
            ques2 = "Current game is: " + ques + "There are now five decks of cards, with hand and community cards being "
            for i, game in enumerate(games):
                ques2 += f"index {i+1}: hand = {game['hand']}, community cards = {game['community_cards']}; "
            ques2 += "Please select a pair of cards that are similar to the current game, and tell me the number of the game you have chosen in the form of '{'choose': '...'}'. "
            ans = self.communicate(ques2)
            try:
                choose = re.search(r"{\s*'choose'\s*:\s*'(.*)'\s*}", ans,
                                   re.DOTALL).group(1)
            except:
                pass
            else:
                for i, game in enumerate(games):
                    if f"{i+1}" in choose:
                        choose = f"{game['game']}"
                        break
                self.is_update_analogy = False
                self.reset_prompt()
                ques += "\nHere is a similar card game with complete information as follows:\n" + choose + "\n"
        if self.is_self_model:
            ques += self.self_model
        ques += (
            "Please provide your results in the form of {'action': ''}. You must choose one from "
            f"{legal_actions} as your answer. ")
        if self.is_believe:
            action, self.belief = self.be.believe(ques, self.summary,
                                                  self.belief, legal_actions,
                                                  self.system_information)
            self.be.save_log(self.belief, self.summary)
        else:
            ques += "Just output the dictionary, don't use any other text."
            self.update_prompt("system", self.system_information)
            self.result = self.communicate(ques)
            action = eval(self.result)["action"]
        self.reset_prompt()
        if action not in legal_actions:
            print(
                f"{action} is not legal action. Legal actions: {legal_actions}. The action will be replace by {legal_actions[0]}. "
            )
            action = legal_actions[0]
        return action

    def eval_step(self, state):
        return self.step(state), []

    def update_action_record(self, ac):
        self.action_record = ac

    def init_self_model(self, sm):
        if isinstance(sm, str):
            self.self_model = sm
        else:
            raise TypeError(
                f"{type(sm)} is not approved for initializing self model. The type of self model should be <class 'str'>. "
            )

    def summarize(self, gi):
        if self.is_believe:
            if self.is_summarize:
                system_infomration = (
                    f"In this Limit Texas poker game, there are {self.num_players} players from 0 to "
                    f"{self.num_players-1}, and your identity is player {self.index_player}. The number of chips every player has is "
                    "infinite. You just finished playing a game, now you need to analyze the problems in the game."
                )
                self.summary = self.be.summarize(gi, self.belief,
                                                 system_infomration)
            else:
                self.summary = {"rea": "", "ref": ""}
            self.belief = {"ses": "", "ops": "", "opo": ""}
            self.be.save_log(self.belief, self.summary)
