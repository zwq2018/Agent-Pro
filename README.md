# AgentPro
[![arXiv](https://img.shields.io/badge/arXiv-Paper-<COLOR>.svg)]([https://arxiv.org/abs/2402.17574])

<video src="https://github.com/zwq2018/Agent-Pro/assets/44236100/95fcde18-ffbb-48da-8917-81e1af74b0c3" width="640" height="480" controls></video>


AgentPro, built upon RLCard, seamlessly connects to large models like GPT, LLama, QWEN, and more. These interfaces facilitate the integration of RLCard's functionalities with robust language models, enabling advanced applications in natural language processing and reinforcement learning.

See our paper: [Agent-Pro: Learning to Evolve via Policy-Level Reflection and Optimization](https://arxiv.org/abs/2402.17574), Wenqi Zhang, Ke Tang, Hai Wu, Mengna Wang, Yongliang Shen, Guiyang Hou, Zeqi Tan, Peng Li, Yueting Zhuang, Weiming Lu

## Installation
Ensure that you have Python 3.6+ and pip installed. Additionally, confirm that your Python environment includes the PyTorch, OpenAI, and RLCard libraries before proceeding with the installation of AgentPro.

### 1. Install PyTorch

Follow the official PyTorch installation guide to install PyTorch.

```
pip install torch
```
### 2. Install OpenAI GPT
Install the OpenAI GPT library using the following command:

```
pip install openai
```
### 3. Install dashscope
Install the dashscope library using the following command:

```
pip install dashscope
```
### 4. Install replicate
Install the dashscope library using the following command:

```
pip install replicate
```

### 5. Install RLCard
You can visit the official RLCard website at https://github.com/datamllab/rlcard to access RLCard-related files and find more information about the library.

Here is the same installation method as the official website:


```
pip3 install rlcard
```
The default installation will only include the card environments. To use PyTorch implementation of the training algorithms, run
```
pip3 install rlcard[torch]
```
If the above command is too slow, you can use the mirror provided by Tsinghua University:
```
pip3 install rlcard -i https://pypi.tuna.tsinghua.edu.cn/simple
```
Alternatively, you can clone the latest version with (if Github is slow, you can use the mirror in [Gitee](https://gitee.com/daochenzha/rlcard)):
```
git clone https://github.com/datamllab/rlcard.git
```
or only clone one branch to make it faster:
```
git clone -b master --single-branch --depth=1 https://github.com/datamllab/rlcard.git
```
Then install with
```
cd rlcard
pip3 install -e .
pip3 install -e .[torch]
```

RLCard also provide [**conda** installation method](https://anaconda.org/toubun/rlcard):

```
conda install -c toubun rlcard
```

Conda installation only provides the card environments, you need to manually install Pytorch on your demands.

### 6. Install AgentPro

```
git clone 
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
*   [/example](example): Store example in paper.
*   [/train_example](train_example): Example of training model.
