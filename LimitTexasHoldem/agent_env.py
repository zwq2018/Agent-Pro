from AgentPro.LimitTexasHoldem.LimittexasholdemAgent import LimitTexasHoldemAgent
from collections import Counter
from itertools import combinations
import json, os


class AgentEnv:
    """ A game environment in which the order of play can be controlled. 
    """

    def __init__(self, version) -> None:
        """ Initilize the Game.
        """
        # Game stage mapping
        self.stage = {0: "Preflop", 3: "Flop", 4: "Turn", 5: "River"}
        # List of possible actions in the game
        self.action_list = ["call", "raise", "fold", "check"]
        # List to record actions taken in the game
        self.action_record = []
        # Index representing the current player
        self.index_player = 0
        # Boolean indicating whether to use raw data
        self.use_raw = True
        # Initial the first player's index
        self.index_player_begin = -1
        # Step in the game
        self.footstep = 0
        # Number of players
        self.num_players = -1
        # List to store player models
        self.models = []
        # List of indices indicating which players are GPT-based
        self.gpt_index = []
        # List of booleans indicating whether a player has folded
        self.is_fold = []
        self.cards_num = []
        self.cards_num_2 = []
        self.self_model = []
        self.version = version
        self.folder = f"save/{version}/"
        if os.path.exists(self.folder) is not True:
            os.mkdir(self.folder)
        if os.path.exists(self.folder + "gi.json") is not True:
            with open(self.folder + "gi.json", 'w') as f:
                json.dump([], f, indent=2)

    def init(self, models: list):
        """ Initializes some parameter Settings in the Game.
        
        Args:
            model: a list to store player models
        """
        self.models = models
        self.num_players = len(models)
        self.gpt_index = []
        for t, agent in enumerate(models):
            if isinstance(agent, LimitTexasHoldemAgent):
                self.gpt_index.append(t)
                agent.update_agent(self.version, self.num_players)
        self.is_fold = [False] * self.num_players
        self.cards_num = [0] * self.num_players
        self.cards_num_2 = [0] * self.num_players
        self.self_model = ""

    def step(self, state):
        """ Handle various game-related logic, including updating the number of the first player in the rlcard library 
        and adjusting the number output in actual play, obtaining player actions, updating the index, managing chip 
        information and action records.

        Args:
            state: The game state containing information like action records, public cards, and chip distribution.

        Returns:
            action: The action chosen by the current player based on the game logic.
        """
        # updating the number of the first player in the rlcard library
        if self.index_player_begin == -1 and len(state["action_record"]) != 0:
            self.index_player_begin = state["action_record"][0][0]
        # detect if the player has folded
        while self.is_fold[self.index_player]:
            self.index_player = (self.index_player + 1) % self.num_players
        # gets the public card(community cards) length
        k = len(state["raw_obs"]["public_cards"])
        # adjusting the number output in actual play
        new_begin = (self.index_player_begin -
                     self.footstep) % self.num_players
        # managing chip information
        state["raw_obs"]["all_chips"] = state["raw_obs"]["all_chips"][
            new_begin:] + state["raw_obs"]["all_chips"][:new_begin]
        # simple hand ranking judgment based on action records.
        card_rank = _rank(self.action_record)
        # add game stage
        if self.stage[k] not in self.action_record:
            self.action_record.append(self.stage[k])
            ac = self.update_action_record(self.action_record,
                                           state["raw_obs"]["public_cards"])
            for gin in self.gpt_index:
                self.models[gin].update_action_record(ac)
        # Update gpt agent's self modeling, and hand ranking.
        if self.index_player in self.gpt_index:
            if self.models[self.index_player].is_self_model:
                self.models[self.index_player].init_self_model(self.self_model)
        # get the action of the agent
        action, _ = self.models[self.index_player].eval_step(state)
        # If the use_raw value of the agent is False, you need to map the action of the agent.
        if self.models[self.index_player].use_raw is False:
            action = self.action_list[action]
        # update action records
        self.action_record.append(
            ((self.index_player + self.footstep) % self.num_players, action))
        # update self.is_fold
        if action == "fold":
            self.is_fold[self.index_player] = True
        # update action records in gpt agent
        ac = self.update_action_record(self.action_record,
                                       state["raw_obs"]["public_cards"])
        for gin in self.gpt_index:
            self.models[gin].update_action_record(ac)
        # next player ready
        self.index_player = (self.index_player + 1) % self.num_players
        return action

    def eval_step(self, state):
        """ Predict the action given the curent state for evaluation. The same to step here.

        Args:
            state (numpy.array): an numpy array that represents the current state

        Returns:
            action (int): the action predicted (randomly chosen) by the random agent
        """
        return self.step(state), []

    def get_action_record(self):
        """ get action records

        Returns:
            action_record: action records in the game
        """
        return self.action_record

    def clear_action_record(self):
        """ Clear self.action_record
        """
        self.action_record = ["Preflop"]

    def reset_game(self):
        """ reset Game
        """
        self.clear_action_record()
        self.index_player = 0
        self.is_fold = [False] * len(self.models)
        self.index_player_begin = -1
        for gin in self.gpt_index:
            self.models[gin].reset_prompt()
            self.models[gin].action_record = ""
            self.models[gin].is_update_self_search = True

    def reorder_tp(self, trajectories, payoffs):
        """ change the order of payoffs

        Args:
            trajectories: game trajectories
            payoffs: game payoffs

        Returns:
            new_trajectories, new_payoffs: game trajectories and payoffs after changing the order
        """
        new_begin = (self.index_player_begin -
                     self.footstep) % self.num_players
        # print(new_begin, self.num_player_begin, self.footstep)
        return list(trajectories[new_begin:]) + list(
            trajectories[:new_begin]), list(payoffs[new_begin:]) + list(
                payoffs[:new_begin])

    def save_result(self, p):
        """ save the game result

        Args:
            p (list): game result
        """
        for gi in self.gpt_index:
            self.models[gi].save_result(p)

    def init_self_model(self, sm):
        """ Initializes the self modeling

        Args:
            sm (string): self modeling
        """
        self.self_model[0] = sm

    def init_self_model_2(self, sm):
        """ Initializes the self modeling

        Args:
            sm (list): self modeling
        """
        self.self_model = sm

    def update_card(self, ts, ps):
        """ 
        Args:
            ts (list): game trajectories
            ps (list): game payoffs
        """
        for i, t in enumerate(ts):
            _, br, _ = best_hand(t[-1]["raw_obs"]["hand"] +
                                 t[-1]["raw_obs"]["public_cards"])
            if br != -1:
                self.cards_num[i] += br
        self.cards_num_2[ps.index(max(ps))] += 1

    def add_footstep(self):
        """ add footstep
        """
        self.footstep = (self.footstep + 1) % self.num_players

    def generate_game_result(self, trajectories, payoffs):
        game_result = ""
        if trajectories == []:
            raise Exception("STATE IS NONE.")
        hand = ""
        for i in range(self.num_players):
            hand += f"Player {i}'s hand is {trajectories[i][0]['raw_obs']['hand']}. "
        community_cards = trajectories[0][-1]['raw_obs']['public_cards']
        action_record = self.update_action_record(self.action_record,
                                                  community_cards)
        p = change_result(payoffs)
        game_result = (
            f"In this Limit Texas poker game, there are {self.num_players} players from 0 to {self.num_players-1}.\n"
            f"{hand}The community card is {community_cards}. "
            f"{(action_record)}\n"
            f"{p}\n")
        return game_result

    def save_game_result(self, gi):
        if os.path.exists(self.folder + "gi.json"):
            with open(self.folder + "gi.json", 'r') as f:
                gi_old = json.load(f)
        else:
            gi_old = []
        with open(self.folder + "gi.json", 'w') as f:
            gi_old.append(gi)
            json.dump(gi_old, f, indent=2)

    def update_action_record(self, ars, community_cards):
        action_record = ""
        for i, ar in enumerate(ars):
            if isinstance(ar, str):
                k = list(self.stage.keys())[list(
                    self.stage.values()).index(ar)]
                ccs = community_cards[:k]
                # action_record += f"\nIn the {ar} stage with the community cards composed of {ccs}, "
                action_record += f"{ar}. "
            else:
                action_record += f"Player {ar[0]} {ar[1]}s. "
                # if i != len(ars) - 1:
                #     action_record += ', '
        # action_record += '. '
        return action_record

    def summarize(self, gi):
        for gin in self.gpt_index:
            self.models[gin].summarize(gi)


def change_result(payoffs):
    p = ''
    for i, rn in enumerate(payoffs):
        if rn < 0:
            p += f"Player {i} loses by {rn * -1} chip(s). "
        elif rn == 0:
            p += f"Player {i} neither wins nor loses. "
        else:
            p += f"Player {i} wins by {rn} chip(s). "
    return p


def evaluate_hand(card):
    """Evaluate the given hand in Texas Hold'em and return its rank and high card.
    
    Args:
        card (list): hand + public card(community card)
    """
    values = "23456789TJQKA"
    value_dict = {v: i for i, v in enumerate(values)}

    # Adjust the hand to account for '10'
    adjusted_hand = [(card[-1], card[0]) for card in card]

    # Sorting hand by the rank of cards
    sorted_hand = sorted(adjusted_hand,
                         key=lambda x: value_dict[x[0]],
                         reverse=True)
    ranks = [value_dict[card[0]] for card in sorted_hand]
    suits = [card[1] for card in sorted_hand]

    is_flush = len(set(suits)) == 1
    is_straight = all(ranks[i] - ranks[i + 1] == 1
                      for i in range(len(ranks) - 1))

    # Straight Flush
    if is_straight and is_flush:
        return 8, ranks

    # Four of a Kind
    counter = Counter(ranks)
    if 4 in counter.values():
        four_card = [rank for rank, count in counter.items() if count == 4][0]
        return 7, [four_card] + [rank for rank in ranks if rank != four_card]

    # Full House
    if 3 in counter.values() and 2 in counter.values():
        three_card = [rank for rank, count in counter.items() if count == 3][0]
        pair = [rank for rank, count in counter.items() if count == 2][0]
        return 6, [three_card, pair]

    # Flush
    if is_flush:
        return 5, ranks

    # Straight
    if is_straight:
        return 4, ranks

    # Three of a Kind
    if 3 in counter.values():
        three_card = [rank for rank, count in counter.items() if count == 3][0]
        return 3, [three_card] + [rank for rank in ranks if rank != three_card]

    # Two Pair
    if list(counter.values()).count(2) == 2:
        pairs = [rank for rank, count in counter.items() if count == 2]
        return 2, sorted(pairs, reverse=True) + [
            rank for rank in ranks if rank not in pairs
        ]

    # Pair
    if 2 in counter.values():
        pair = [rank for rank, count in counter.items() if count == 2][0]
        return 1, [pair] + [rank for rank in ranks if rank != pair]

    # High Card
    return 0, ranks


def best_hand(cards):
    """Find the best possible hand in Texas Hold'em from the given cards.
    
    Args:
        card (list): hand + community cards
    """
    best_rank = -1
    best_high_card = []
    best_hand = []
    rankdict = {
        -1: "None",
        0: "High Card",
        1: "One Pair",
        2: "Two pair",
        3: "Three of a Kind",
        4: "Straight",
        5: "Flush",
        6: "Full House",
        7: "Four of a Kind",
        8: "Straight Flush",
    }

    for hand in combinations(cards, 5):
        rank, high_card = evaluate_hand(hand)
        if rank > best_rank or (rank == best_rank
                                and high_card > best_high_card):
            best_rank = rank
            best_high_card = high_card
            best_hand = hand

    return best_hand, best_rank, rankdict[best_rank]


def rank(actions):
    # As we don't have the specific hands of the players, we can't calculate exact hand strength
    # However, we can assign them rankings based on the betting sequence
    # In a simplified view: more aggressive betting might imply a stronger hand

    # Assign initial rank based on the last action taken by each player
    # Assuming players who raise or re-raise have stronger hands
    # This is a simplification and does not take into account bluffing or other strategic considerations
    player_ranks = {i: 0 for i in range(4)}  # Initial ranks
    for player, action in actions:
        if action == "raise":
            player_ranks[player] += 3
        elif action == "call":
            player_ranks[player] += 1
        elif action == "fold":
            player_ranks[player] -= 1  # Penalize for folding

    # Sort players by their final rank
    sorted_players = sorted(player_ranks.items(),
                            key=lambda item: item[1],
                            reverse=True)

    # Return player rankings
    return sorted_players


def _rank(action_record):
    actions = []
    for ar in action_record:
        if isinstance(ar, tuple):
            actions.append(ar)
    sorted_players = rank(actions=actions)
    return sorted_players
