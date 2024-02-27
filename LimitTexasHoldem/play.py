from AgentPro.LimitTexasHoldem import AgentEnv, LimitTexasHoldemAgent
import numpy as np
import torch
import rlcard
from rlcard.agents import RandomAgent, LimitholdemHumanAgent
from rlcard.utils import set_seed
from rlcard.games.limitholdem.game import LimitHoldemGame
from rlcard.games.limitholdem import Dealer
from rlcard.games.limitholdem import Player
from rlcard.games.limitholdem import Judger
from rlcard.games.limitholdem import Round
import os


class Play:
    ds = 0

    def init_game(self):
        # Initialize a dealer that can deal cards
        self.dealer = Dealer(self.np_random)
        # Initialize two players to play the game
        self.players = [
            Player(i, self.np_random) for i in range(self.num_players)
        ]
        # Initialize a judger class which will decide who wins in the end
        self.judger = Judger(self.np_random)
        # Deal cards to each  player to prepare for the first round
        for i in range(2 * self.num_players):
            self.players[i % self.num_players].hand.append(
                self.dealer.deal_card())
        # Initialize public cards
        self.public_cards = []
        # Randomly choose a small blind and a big blind
        s = self.np_random.randint(0, self.num_players)
        s = (s + Play.ds) % self.num_players
        b = (s + 1) % self.num_players
        self.players[b].in_chips = self.big_blind
        self.players[s].in_chips = self.small_blind
        # The player next to the big blind plays the first
        self.game_pointer = (b + 1) % self.num_players
        # Initialize a bidding round, in the first round, the big blind and the small blind needs to
        # be passed to the round for processing.
        self.round = Round(raise_amount=self.raise_amount,
                           allowed_raise_num=self.allowed_raise_num,
                           num_players=self.num_players,
                           np_random=self.np_random)
        self.round.start_new_round(game_pointer=self.game_pointer,
                                   raised=[p.in_chips for p in self.players])
        # Count the round. There are 4 rounds in each game.
        self.round_counter = 0
        # Save the history for stepping back to the last state.
        self.history = []
        state = self.get_state(self.game_pointer)
        # Save betting history
        self.history_raise_nums = [0 for _ in range(4)]
        return state, self.game_pointer

    def check_file_exists(file_path):
        return os.path.exists(file_path)

    def play_game(version,
                  _range=range(400),
                  self_model="",
                  key="",
                  is_turn=True,
                  mode=0):
        if is_turn:
            LimitHoldemGame.init_game = Play.init_game
        if mode == 0:
            config = {}
        elif mode == 1:
            config = {"is_believe": True}
        elif mode == 2:
            config = {"is_self_model": True}
        elif mode == 3:
            config = {"is_analogy": True}
        elif mode == 4:
            config = {"is_believe": True, "is_summarize": True}
        set_seed(70)
        # Number of players in the game
        num_players = 4
        # Create the game environment with the specified number of players
        env = rlcard.make("limit-holdem",
                          config={
                              "game_num_players": num_players,
                          })
        # Version for saving files
        folder_path = "save/{}".format(version)
        if os.path.exists(folder_path):
            print(f"The folder at {folder_path} exists.")
        else:
            os.mkdir(folder_path)
        # Initialize the game logic
        game = AgentEnv(version)
        # Create different agents for the game
        random_agent = RandomAgent(num_actions=env.num_actions)
        dqn_agent = torch.load("models/dqn_LTH_500k.pth")
        dmc_agent = torch.load("models/dmc_LTH.pth")
        human_agent = LimitholdemHumanAgent(num_actions=env.num_actions)

        # Create agents using GPT models
        gpt35_agent = LimitTexasHoldemAgent(index_player=2,
                                            LLM_model="gpt-3.5-turbo",
                                            key=key,
                                            config={})
        gpt4_agent = LimitTexasHoldemAgent(index_player=3,
                                           LLM_model="gpt-4",
                                           key=key,
                                           config=config)
        gpt4_agent.init_self_model(self_model)
        # gpt4_agent.updare_wrong_book_2(basic_wrong_book)

        # List of agents to participate in the game
        agents = [dqn_agent, dmc_agent, gpt35_agent, gpt4_agent]

        # Arrays to keep track of scores
        sum_all = [0] * num_players

        # Game simulation loop
        for i in _range:
            set_seed(70)
            if is_turn:
                env.seed(int(i / 16))
                Play.ds = i
                _agents = agents[int(i % 16 / 4):] + agents[:int(i % 16 / 4)]
                game.footstep = int(i % 16 / 4)
            else:
                env.seed(i)
            # Initialize the game with agents
            game.init(_agents)
            # Set agents for the environment and seed it
            env.set_agents([game, game, game, game])
            # Run the game simulation
            t, p = env.run(is_training=False)
            t, p = game.reorder_tp(t, p)
            game.save_result(p)
            game.update_card(t, p)
            # Generate and save game information
            gi = game.generate_game_result(t, p)
            game.summarize(gi)
            game.save_game_result(gi)
            game.reset_game()
            # Update the total scores
            sum_all = np.sum([sum_all, p], axis=0)
        print(*sum_all)


def reproduce(self_model, mode, key, version):
    r = []
    r = [
        791 * 16,
        791 * 16 + 1,
        970 * 16,
        970 * 16 + 3,
        5 * 16 + 1,
        5 * 16 + 3,
        56 * 16 + 2,
        56 * 16 + 3,
        1042 * 16 + 1,
        1042 * 16 + 2,
        80 * 16 + 3,
        80 * 16 + 2,
        230 * 16 + 2,
        230 * 16 + 1,
        965 * 16 + 3,
        965 * 16,
        1880 * 16,
        1880 * 16 + 2,
        216 * 16 + 2,
        216 * 16 + 3,
    ]
    r = r[:]
    Play.play_game(version,
                   _range=r,
                   self_model=self_model,
                   key=key,
                   mode=mode)
