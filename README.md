# AgentPro

AgentPro, built upon RLCard, seamlessly connects to large models like GPT, LLama, QWEN, and more. These interfaces facilitate the integration of RLCard's functionalities with robust language models, enabling advanced applications in natural language processing and reinforcement learning.


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




## Pre Trained Models
The specific training example code can be found in [train_example](AgentPro\train_example).

## Prompt for Blackjack

### Game Settings:
You are a player in blackjack. Please beat the dealer and win the game.

### Game Information:
Game Rule:
1. Please try to get your card total to as close to 21 as possible, without going over, and still having a higher total than the dealer.
2. If anyone's point total exceeds 21, he or she loses the game. 
3. You can only choose one of the following two actions: {"Stand", "Hit"}. If you choose to Stand, you will stop taking cards and wait for the dealer to finish. If you choose to Hit, you can continue to take a card, but there is also the risk of losing the game over 21 points. 
4. After all players have completed their hands, the dealer reveals their hidden card. Dealers must hit until their cards total 17 or higher.


### Prompt For Vanilla
#### Input Format:

You are a player in blackjack. Please beat the dealer and win the game.

{Game Rules}

{Game Information}

#### Output Format: 
Output your action in following format : {" action ": " "} without any other text.

### Prompt For Radical
#### Input Format:

You are an aggressive player of blackjack who likes to take risks to earn high returns. Please beat the dealer and win the game.

{Game Rules}

{Game Information}

#### Output Format: 
Output your action in following format : {" action ": " "} without any other text.

### Prompt For ReAct
#### Input Format:

You are a player in blackjack. Please beat the dealer and win the game.

{Game Rules}

{Game Information}

Please first think and reason about the current hand and then generate your action.

#### Output Format: 
Output your action in following format :  ###My thought is {Your Thought}. My action is {your action}.

### Prompt For Reflexion
#### Input Format:

You are a player in blackjack. Please beat the dealer and win the game.

{Game Rules}

{Game Information}

Please first think about the current hand and then generate your action 

Assistant : {LLM Response}. My action is {LLM Response}

Please carefully check the thought and the action you just output , and then
refine your answer.

#### Output Format: 
Output your action in following format :  ### My revised thought is { Your Thought }. My revised action is {" action ": " "}.


### Prompt For AgentPro
#### Input Format:
You are a player in blackjack. Please beat the dealer and win the game.

{Game Rules}

{Game Information}

{Behavioral Guideline: Goal, Strategy, Demonstration}

{World Modeling: Rule Description}

Please read the behavoiral guideline and world modeling carefully . Then you should analyze your own cards and your strategies in Self-belief and then analyze the dealer cards in World-belief. Lastly, please select your action from {"Stand","Hit"}.

#### Output Format: 

Self-Belief is {Belief about youself}. World-Belief is {Belief about the dealer}. My action is {Your action}. Please output in the given format .

## Prompt for Limit Texas Hold'em

### Game Settings:
You are playing the Limit Texas poker game. In this game, there are 4 players from 0 to 3, and your role is player 3. 

The number of chips every player has is infinite.  

You just need to win new chips in the competition as much as possible.

The actions you can choose are ['call', 'raise', 'fold', 'check']

### Game Information:
Your current hands are [Private Cards]. 

The current stage: [Stage]. Public cards are [Public cards]. 

Number of chips all players have invested are [Inveseted Chip List]. 

Available actions you can choose are {Available Actions} 

Previous actions of all players are: {Preflop: Actions Sequences, Flop: Actions ...}

### Prompt For Agent-Pro
**Input Format:**
You are a player in Limited Texas Hold'em. Beat your opponents and win the game.
{Game Rules}

{Game Information}

{Behavioral Guideline: Goal, Strategy, Demonstration}

{World Modeling: Rule Description, Opponents Description}

Please read the behavoiral guideline and world modeling carefully. Then, following their instructions, you should analyze your own cards and your strategies in Self-belief and then analyze and reason about your opponents in World-belief. Lastly, output your action.

#### Output Format: 
Self-Belief is {belief about youself}. World-Belief is {belief about the all opponents}. My action is {"action": " "}. Please output in the given format.

### Prompt For Policy-Level Reflection
**Input Format:**
{Game Rules}

{Game Information}

Game Record: {Game Record, Belief Sequences, Final Result}

You are a seasoned Limited Texas Hold'em expert, and you need to carefully reflect on the following record of this losing game:
* Correctness: Whether its beliefs about yourself, the game, and the opponents align with the final results.
* Consistency: Whether each belief and action is self-contradictory.
* Rationality: Whether the beliefs accurately reflect the underlying intentions behind the opponents. 
* Reasons: Reflect on why you lost to your opponents, which beliefs and actions are problematic, and what the underlying reasons are.

**Output Format:** 
I analyze this game as follows: {Your analysis about the game and belief}.

### Prompt For Generating Behavioral Guideline and World Modeling
**Input Format:**
Game Record: {Game Record, Belief Sequences, Final Result}

Policy-Level Reflection: {Reflection}

Following the previous rigorous analysis, you should distill and articulate a set of Behavioral Guidelines and World Modeling. The Behavioral Guideline is about what you consider to be a more reasonable and effective behavioral strategy and suggestions. World Modeling is about the description of the game and all opponents. 

Here are some suggestions for you: 
* {Behavioral Guideline}
* {Goal}: Please summarize the detailed goal based on your reflection ... 
* {Strategy}: What kind of strategy can lead you to win in similar games ... 
* {Demonstration}: Can this game be considered a typical example to be preserved for future reference ... 

**Output Format:**
World Modeling
* {Rule-Description}: Based on the recent reflection, describe any game rules or details that are easy to overlook ... 
* {Opponent-Modeling}: Based on each opponent's action and the real hands shown at the end of the game, what do you think their style and strategy are ... 

## Library Structure
The purposes of the main modules are listed as below:

*   [/LimitTexasHoldem](AgentPro\LimitTexasHoldem): The environment of Limit Texas Holdem.
*   [/Blackjack](AgentPro\Blackjack): The environment of Blackjack.
*   [/example](AgentPro\example): Store example in paper.
*   [/train_example](AgentPro\train_example): Example of training model.
