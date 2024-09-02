# AgentPro
[![arXiv](https://img.shields.io/badge/arXiv-Paper-b31b1b.svg)](https://arxiv.org/abs/2402.17574)
[![QbitAI](https://img.shields.io/badge/QbitAI-Article-007bff.svg)](https://www.qbitai.com/2024/03/127294.html)
[![Jiangmen Ventures](https://img.shields.io/badge/JiangmenVentures-Article-007bff.svg)](https://mp.weixin.qq.com/s/gD4pZc6pvX8f_62uiPJacg)


🎆 [New 0517] **Our paper is accepted by ACL 2024 Main**

🎆 [New 0511] **Agent-Pro is presented in ICLR 2024 LLMAgents Workshop, Vienna.**

🎆 [New 0326] **Our article has been noticed and reported by Jiangmen Ventures(将门创投). (https://mp.weixin.qq.com/s/gD4pZc6pvX8f_62uiPJacg)**

🎆 [New 0301] **Agent-Pro is accepted by ICLR 2024 LLMAgents Workshops as a Poster paper.(https://llmagents.github.io/)**

🎆 [New 0227] **Our article has been noticed and reported by QbitAI(量子位): [![QbitAI Article](https://img.shields.io/badge/QbitAI-Article-007bff.svg)](https://www.qbitai.com/2024/03/127294.html).**
<video src="https://github.com/zwq2018/Agent-Pro/assets/44236100/95fcde18-ffbb-48da-8917-81e1af74b0c3" width="640" height="480" autoplay loop></video>



AgentPro, built upon RLCard, seamlessly connects to large models like GPT, LLama, QWEN, and more. These interfaces facilitate the integration of RLCard's functionalities with robust language models, enabling advanced applications in natural language processing and reinforcement learning.

See our paper: [Agent-Pro: Learning to Evolve via Policy-Level Reflection and Optimization](https://arxiv.org/abs/2402.17574), Wenqi Zhang, Ke Tang, Hai Wu, Mengna Wang, Yongliang Shen, Guiyang Hou, Zeqi Tan, Peng Li, Yueting Zhuang, Weiming Lu

## Installation
Ensure that you have Python 3.6+ and pip installed. Additionally, confirm that your Python environment includes the PyTorch, OpenAI, and RLCard libraries before proceeding with the installation of AgentPro.

### 1. Install PyTorch

You can follow the official PyTorch installation guide to install PyTorch. Or you can choose your preferred version and complete the installation yourself.
```
pip3 install torch
```
### 2. Install RLCard
You can visit the official RLCard website at https://github.com/datamllab/rlcard to access RLCard-related files and find more information about the library.

Here is the same installation method as the official website:

```
pip3 install rlcard
```

### 3. Install AgentPro

First, you should clone the code from github as follow:
```
git clone https://github.com/zwq2018/Agent-Pro.git
```
Then install with
```
cd Agent-Pro
pip3 install .
```

## Available Environments
**RLCard** provide a complexity estimation for the games on several aspects. **InfoSet Number:** the number of information sets; **InfoSet Size:** the average number of states in a single information set; **Action Size:** the size of the action space. **Name:** the name that should be passed to `rlcard.make` to create the game environment. We also provide the link to the documentation and the random example.

|Game                                                                                                                                                                                           | InfoSet Number  | InfoSet Size      | Action Size | Name   |
| :--------: | :----------: | :---------: | :--------: | :------: | 
| Blackjack ([wiki](https://en.wikipedia.org/wiki/Blackjack))                                                              | 10^3            | 10^1              | 10^0        | blackjack                             |
| Limit Texas Hold'em ([wiki](https://en.wikipedia.org/wiki/Texas_hold_%27em))    | 10^14           | 10^3              | 10^0        | limit-holdem    |



## Code Run Instructions
### Blackjack

If you intend to reproduce content related to Blackjack in paper, please utilize the following code snippet:

```python
from play_blackjack_game import play

if __name__ == "__main__":
    number_of_game = 2
    model = 'Qwen'
    game_style = 'ReAct'
    storage_name = "Qwen Play ReAct Blackjack"

    play(number_of_game,model,game_style,storage_name)
```
* `number_of_game` is used to set the total number of games.
* `model` is used to set the model for playing the game, you can choose `gpt-3.5` `gpt-4` `Llama70b` `Qwen`
* `game_style` is used to set the style of the game, you can choose `Vanilla` `Radical` `ReAct` `Reflexion` `AgentPro`
* `storage_name` is used to set the file name for storing game records.

Before running, you also need to fill in the corresponding Key into the `YOUR KEY` field in `API.py`. Taking GPT-4 as an example, you can adjust the parameters of the model here.
```python
class GPT4API:
    def __init__(self) -> None:
        openai.api_key = "YOUR KEY"

    def response(self, mes):
        response = openai.ChatCompletion.create(
            model='MODEL NAME',
            messages=mes,
            top_p=0.95,
            temperature=1,
        )
        return response.get("choices")[0]["message"]["content"]
```

### Limit Texas Hold`em

If you intend to reproduce content related to Limit Texas Hold'em in paper, please utilize the following code snippet:

```python
from AgentPro import reproduce

self_model = "I should be radical."
mode = 0
key = ""
reproduce(self_model, mode, key)
```
* When `mode` is set to 0, a pure LLM with only a simple action will be executed.
* When `mode` is set to 1, it will run an LLM that establishes beliefs and generates actions based on those beliefs.
* When `mode` is set to 2, the LLM will run by selecting similar questions from the [AgentPro/LimitTexasHoldem/example.json](LimitTexasHoldem\example.json) file for analogical reasoning before generating actions.
* When `mode` is set to 3, you can customize the game style and strategy of LLM by rewriting the `self_model`.
* When `mode` is set to 4, it will operate an LLM that establishes beliefs, generates actions based on those beliefs, and then produces a summary at the end of each game for subsequent use.
* `key`(str) is your `openai.api_key`.

To integrate an LLM into a custom game, you need to create an `LLM_Agent`. Here is an example:

```python
from AgentPro import LimitTexasHoldemAgent

index_player = 3
LLM_model = "gpt-3.5-turbo"
key = ""
config = {
    "is_self_model": True,
    "is_believe": True,
    "is_analogy": True,
    "is_summarize": True
}
LLM_agent = LimitTexasHoldemAgent(index_player=index_player,
                                  LLM_model=LLM_model,
                                  key=key,
                                  config=config)
LLM_agent.init_self_model("I should be radical.")
```

* `index_player`(int) is the number of LLM players in the game.
* `LLM_model`(str) is the model you want to load. Currently, only `GPT-3.5 Turbo`, `GPT-4`, and `GPT-4 Turbo` in the OpenAI Models directory are supported.
* `key`(str) is your `openai.api_key`.
* `config`(dict) contains four keys: `"is_self_model"`, `"is_believe"`, `"is_analogy"`, and `"is_summarize"`, whose default state is `False`. If you want to turn on a feature and set it to `True`, you can do it.
If you make `"is_self_model"=True`, you can use the function `LLM_agent.init_self_model("")` to provide LLM with a game style or strategy.
If you make `"is_believe"=True`, LLM will generate a belief during gameplay.
If you make `"is_analogy"=True`, the LLM will run by selecting similar questions from the [AgentPro/LimitTexasHoldem/example.json](LimitTexasHoldem\example.json) file for analogical reasoning before generating actions.
If you make `"is_summarize"=True`, LLM will summarize and reflect on the game after playing one game.

After creating all the agents, you'll need to set up a Limit Texas Hold'em game environment using a method similar to the following:

```python
import rlcard
from rlcard.agents import RandomAgent
from AgentPro import AgentEnv, LimitTexasHoldemAgent

version = "test"
num_players = 3
index_player = 2
LLM_model = "gpt-3.5-turbo"
key = ""
config = {
    "is_self_model": True,
    "is_believe": True,
    "is_analogy": True,
    "is_summarize": True
}
self_model = "I should be radical."

env = rlcard.make("limit-holdem", config={
    "game_num_players": num_players,
})
game = AgentEnv(version)
LLM_agent = LimitTexasHoldemAgent(index_player=index_player,
                                  LLM_model=LLM_model,
                                  key=key,
                                  config=config)
LLM_agent.init_self_model(self_model)
random_agent = RandomAgent(num_actions=env.num_actions)

agents = [random_agent, random_agent, LLM_agent]
game.init(agents)

env.set_agents([game] * len(agents))

t, p = env.run(is_training=False)
t, p = game.reorder_tp(t, p)

game.save_result(p)
game.update_card(t, p)

gi = game.generate_game_result(t, p)

game.summarize(gi)
game.save_game_result(gi)
game.reset_game()

```
* `num_player`(int) is the num of players.
* `agents`(list) is players who will appear in this game. If you wish to replace one of the agents (denoted as agent_i) with an `LLM-Agent`, you'll need to set `LLM-Agent.index_player` to i.
* `version`(str) determines the save location of all files in the `save/version/` folder during this operation.



## Library Structure
The purposes of the main modules are listed as below:

*   [/LimitTexasHoldem](LimitTexasHoldem): The environment of Limit Texas Holdem.
*   [/Blackjack](Blackjack): The environment of Blackjack.
*   [/data_examples](data_example): Store example in paper.
*   [/train_examples](train_example): Example of training model.

## Citation
```
@inproceedings{zhang-etal-2024-agent,
    title = "Agent-Pro: Learning to Evolve via Policy-Level Reflection and Optimization",
    author = "Zhang, Wenqi  and
      Tang, Ke  and
      Wu, Hai  and
      Wang, Mengna  and
      Shen, Yongliang  and
      Hou, Guiyang  and
      Tan, Zeqi  and
      Li, Peng  and
      Zhuang, Yueting  and
      Lu, Weiming",
    booktitle = "Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)",
    year = "2024",
    address = "Bangkok, Thailand",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2024.acl-long.292",
    pages = "5348--5375"
}
```

```
@inproceedings{zhang-etal-2024-self-contrast,
    title = "Self-Contrast: Better Reflection Through Inconsistent Solving Perspectives",
    author = "Zhang, Wenqi  and
      Shen, Yongliang  and
      Wu, Linjuan  and
      Peng, Qiuying  and
      Wang, Jun  and
      Zhuang, Yueting  and
      Lu, Weiming",
    booktitle = "Proceedings of the 62nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)",
    year = "2024",
    address = "Bangkok, Thailand",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2024.acl-long.197",
    pages = "3602--3622"
}

```
