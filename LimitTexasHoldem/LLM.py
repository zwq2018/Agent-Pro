import AgentPro.LimitTexasHoldem.API as API
import json
import time


class LLM:

    def __init__(self, address, LLM_model="gpt-3.5-turbo", key="") -> None:
        self.api = None
        self.api = API.API(LLM_model, key)
        self.prompt = []
        self.address = address

    def reset_prompt(self):
        self.prompt = []

    def update_prompt(self, role, content):
        self.prompt += [{"role": role, "content": content}]
        if self.address != "":
            with open(self.address, "r") as f:
                prompts = json.load(f)
            prompts.append({"role": role, "content": content})
            with open(self.address, "w") as f:
                json.dump(prompts, f, indent=2)

    def api_response(self, n):
        return self.api.response(self.prompt, n)

    def print_prompt(self):
        for p in self.prompt:
            print("---")
            print(p["role"] + ":\n" + p["content"])

    def communicate(self, ques, n=1):
        self.update_prompt("user", ques)
        resp = self.api_response(n)
        self.update_prompt("assistant", resp[0])
        if n == 1:
            resp = resp[0]
        # time.sleep(2)
        return resp

    def save_result(self, p):
        if self.address != "":
            with open(self.address, "r") as f:
                prompts = json.load(f)
            prompts.append({"result": "{}".format(p)})
            with open(self.address, "w") as f:
                json.dump(prompts, f, indent=2)
