import re
from collections import Counter
from itertools import combinations


class InfExtra:

    def evaluate_hand(cards):
        """Evaluate the given hand in Texas Hold'em and return its rank and high card.
        
        Args:
            card (list): hand + public card(community card)
        """
        values = "23456789TJQKA"
        value_dict = {v: i for i, v in enumerate(values)}
        # Adjust the hand to account for '10'
        adjusted_hand = [(card[-1], card[0]) for card in cards]
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
            four_card = [
                rank for rank, count in counter.items() if count == 4
            ][0]
            return 7, [four_card
                       ] + [rank for rank in ranks if rank != four_card]
        # Full House
        if 3 in counter.values() and 2 in counter.values():
            three_card = [
                rank for rank, count in counter.items() if count == 3
            ][0]
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
            three_card = [
                rank for rank, count in counter.items() if count == 3
            ][0]
            return 3, [three_card
                       ] + [rank for rank in ranks if rank != three_card]
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
            card (list): hand + public card(community card)
        """
        best_rank = -1
        best_high_card = []
        best_hand = []

        for hand in combinations(cards, 5 if len(cards) > 2 else 2):
            rank, high_card = InfExtra.evaluate_hand(hand)
            if rank > best_rank or (rank == best_rank
                                    and high_card > best_high_card):
                best_rank = rank
                best_high_card = high_card
                best_hand = hand
        return best_hand, best_rank, best_high_card

    def extract_cards_from_gi(text):
        hand_pattern = re.compile(r"Player (\d+)'s hand is (\[.*?\]).")
        community_card_pattern = re.compile(
            r"The community card is (\[.*?\]).")

        hand_matches = hand_pattern.findall(text)
        hands = {int(player): eval(cards) for player, cards in hand_matches}

        community_card_matches = community_card_pattern.findall(text)
        community_cards = eval(
            community_card_matches[0]) if community_card_matches else []

        return hands, community_cards

    def extract_cards_from_prompt(text):
        hand = eval(re.search(r"Now your hand is (\[.*?\])", text).group(1))
        community_cards = eval(
            re.search(r"your public cards is (\[.*?\])", text).group(1))

        return hand, community_cards

    def extract_result_from_gi(input_string):
        result_pattern = re.compile(
            r'Player (\d) (neither wins nor loses|loses by|wins by) ([\d.]+) chip\(s\)'
        )
        result_matches = result_pattern.findall(input_string)
        results = {
            int(player):
            (0.0 if outcome == 'neither wins nor loses' else
             float(chips) if outcome == 'wins by' else -float(chips))
            for player, outcome, chips in result_matches
        }
        for player in range(4):
            if player not in results:
                results[player] = 0.0
        sorted_results = dict(sorted(results.items()))
        return sorted_results

    def find_player_position(game_string):
        position_pattern = re.compile(
            r'Player (\d) (call|fold|raise|check)s\.')
        position_matches = position_pattern.findall(game_string)
        for i, position_match in enumerate(position_matches):
            if position_match[0] == '3':
                return i
        return len(position_match)

    def parse_poker_game(log):
        dict_action = {"raise": 3, "call": 1, "check": 0, "fold": -1}
        actions = re.findall(r"Player (\d+) (call|fold|raise|check)s\.", log)
        player_actions = {i: [] for i in range(4)}

        for player, action in actions:
            player_actions[int(player)].append(dict_action[action])

        return player_actions

    def change_poke(cards: list):
        ret = []
        decorAbbreviation = ["H", "C", "D", "S"]
        decor = ["heart", "club", "diamond", "spade"]
        for card in cards:
            _card = decor[decorAbbreviation.index(card[0])]
            _card += " "
            if card[1] == "T":
                _card += "10"
            else:
                _card += card[1]
            ret.append(_card)
        return ret

    def print_choose(addres_agent):
        with open(addres_agent, 'r') as f:
            ls = f.readlines()

        choose = -1
        l_old = ""
        for l in ls:
            result = re.search(r"{\"result\": ", l)
            if result is not None:
                choose = -1
            choose = re.search(
                r"{\"role\": \"assistant\", \"content\": \"{'choose': '(\w)'}\"}",
                l)
            if choose is not None:
                choose = int(choose.group(1)) - 1
                hand = re.search(r"Now your hand is (\[.*?\])", l_old).group(1)
                print(choose)
            l_old = l
