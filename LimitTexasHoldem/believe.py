from AgentPro.LimitTexasHoldem.LLM import LLM
import re, json, os


class Believe(LLM):

    def __init__(self,
                 address,
                 log_address,
                 index,
                 LLM_model="gpt-3.5-turbo",
                 key=""):
        super().__init__(address, LLM_model, key)
        self.index = index
        self.log_address = log_address

    def believe(self, game_information, history_summary, history_belief,
                legal_actions, system_information):
        belief = {"ses": "", "ops": "", "opo": ""}
        _history_summary = ""
        _history_belief = ""
        self.update_prompt('system', system_information)
        if dict_empty(history_summary) is not True:
            _history_summary = (
                f"As Player {self.index}, your previous reflection on the game was:\n"
                f"{history_summary['ref']}\n")
        if dict_empty(history_belief) is not True:
            _history_belief = (
                "In a previous round, you have established a belief like this:\n"
                f"your own game situation is: {history_belief['ses']}\n"
                f"the game situation of opponents who have not chosen to fold is: {history_belief['ops']}\n"
                f"your opponent's opinion of you is: {history_belief['opo']}\n"
            )
        ques = (
            f"The game information is: {game_information}\n"
            f"{_history_summary}"
            f"{_history_belief}"
            f"As Player {self.index}, please analyze your own game situation bracketed with <ses> and </ses>, that includes hand and community card types, feasible game strategies, "
            "the game situation of opponents who have not chosen to fold bracketed with <ops> and </ops>, that includes opponents' behavior, opponents' possible strategies, "
            "and then briefly talk about your opponent's opinion of you bracketed with <opo> and </opo>, "
            "and finally give the most reasonable action in the form of '{'action': '...'}'. "
            f"Note that your action must be selected from {legal_actions}. "
            "For example, <ses> My card type is ... </ses>, <ops> I think that Player 0 is ... </ops>, <opo> Player 0 think that ... </opo>. I will choose {'action': 'raise'}."
            f"You should use player {self.index} as the first person. ")
        ans = self.communicate(ques)
        self.reset_prompt()
        try:
            belief['ses'] = re.search(r'<ses>(.*?)</ses>', ans,
                                      re.DOTALL).group(1)
        except AttributeError:
            print("Error: Update Self-Situation Error.")
        try:
            belief['ops'] = re.search(r'<ops>(.*?)</ops>', ans,
                                      re.DOTALL).group(1)
        except AttributeError:
            print("Error: Update Opponent-Situation Error.")
        try:
            belief['opo'] = re.search(r'<opo>(.*?)</opo>', ans,
                                      re.DOTALL).group(1)
        except AttributeError:
            print("Error: Update Opponent-Option Error.")
        try:
            action = re.search(r"{\s*'action'\s*:\s*'(\w+)'\s*}", ans).group(1)
        except AttributeError:
            action = legal_actions[0]
            print(
                f"Error: Update Opponent-Option Error. Action will be replaced by {action}"
            )
        return action, belief

    def summarize(self, gi, history_belief, system_information):
        summary = {}
        self.update_prompt("system", system_information)
        prompt = (
            "In the latest game, you have established a belief like this:\n"
            f"your own game situation is: {history_belief['ses']}\n"
            f"the game situation of opponents who have not chosen to fold is: {history_belief['ops']}\n"
            f"your opponent's opinion of you is: {history_belief['opo']}\n"
            f"Based on the new game information ({gi}), "
            "Please summarize the reasons for your failure or success bracketed with <rea> and </rea> and briefly propose a reasonable strategy bracketed with <ref> and </ref>. "
            f"You should use player {self.index} as the first person. ")
        ans = self.communicate(prompt)
        try:
            summary['rea'] = re.search(r'<rea>(.*?)</rea>', ans,
                                       re.DOTALL).group(1)
        except AttributeError:
            print("Error: Update Reason Error.")
        try:
            summary['ref'] = re.search(r'<ref>(.*?)</ref>', ans,
                                       re.DOTALL).group(1)
        except AttributeError:
            print("Error: Update Reflection Error.")
        self.reset_prompt()
        return summary

    def load_log(self):
        belief = {"ses": "", "ops": "", "opo": ""}
        summary = {"rea": "", "ref": ""}
        with open(self.log_address, 'r') as f:
            try:
                ls = json.load(f)
                if ls != []:
                    belief = ls[-1]['belief']
                    summary = ls[-1]['summary']
            except:
                pass
        return belief, summary

    def save_log(self, belief, summary):
        ls = []
        if os.path.exists(self.log_address):
            with open(self.log_address, 'r') as f:
                ls = json.load(f)
        ls.append({'belief': belief, 'summary': summary})
        with open(self.log_address, 'w') as f:
            json.dump(ls, f, indent=2)


def dict_empty(d):
    for v in list(d.values()):
        if v != "":
            return False
    return True
