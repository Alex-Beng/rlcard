from collections import Counter

class HandType:
    PASS = 0
    SINGLE = 1
    PAIR = 2
    TRIPLE = 3
    STRAIGHT = 4
    CONSECUTIVE_PAIRS = 5
    BOMB = 6

TYPE_NAMES = {
    0: 'pass', 1: 'single', 2: 'pair', 3: 'triple',
    4: 'straight', 5: 'consecutive_pairs', 6: 'bomb',
}

class HandChecker:
    def __init__(self, ranking):
        self.ranking = ranking

    def classify(self, cards):
        if not cards:
            return None
        ranks = Counter(c.rank for c in cards)
        rank_values = sorted(self.ranking.rank_value(r) for r in ranks)
        n = len(cards)
        unique_ranks = len(ranks)

        if n == 1:
            return (HandType.SINGLE, rank_values[0], len(cards))

        if unique_ranks == 1:
            count = list(ranks.values())[0]
            if count == 2:
                return (HandType.PAIR, rank_values[0], len(cards))
            if count == 3:
                return (HandType.TRIPLE, rank_values[0], len(cards))
            if count == 4:
                return (HandType.BOMB, rank_values[0], len(cards))
            return None

        all_same_count = len(set(ranks.values())) == 1
        if not all_same_count:
            return None

        count = list(ranks.values())[0]

        values = sorted({self.ranking.rank_value(r) for r in ranks})
        max_possible_rank_val = self.ranking.rank_value('A')

        if count == 1:
            if n >= 5 and self._is_consecutive(values, max_possible_rank_val):
                return (HandType.STRAIGHT, values[0], len(cards))
            return None

        if count == 2 and n >= 6 and n % 2 == 0:
            if self._is_consecutive(values, max_possible_rank_val):
                return (HandType.CONSECUTIVE_PAIRS, values[0], len(cards))
            return None

        return None

    def _is_consecutive(self, values, max_val):
        for i in range(1, len(values)):
            if values[i] != values[i-1] + 1:
                return False
        if values[-1] > max_val:
            return False
        return True

    def can_beat(self, new_type, new_rank, new_len, last_type, last_rank, last_len):
        if last_type == HandType.PASS:
            return True
        if new_type == HandType.BOMB:
            if last_type == HandType.BOMB:
                return new_rank > last_rank
            return True
        if new_type == last_type:
            return new_rank > last_rank and new_len == last_len
        return False

    def get_legal_actions(self, hand, last_type, last_rank, last_len):
        ranks = Counter()
        for card in hand:
            ranks[card.rank] += 1

        actions = []

        if last_type == HandType.PASS:
            for rank, count in ranks.items():
                rv = self.ranking.rank_value(rank)
                cards_of_rank = [c for c in hand if c.rank == rank]
                if count >= 1:
                    actions.append(cards_of_rank[:1])
                if count >= 2:
                    actions.append(cards_of_rank[:2])
                if count >= 3:
                    actions.append(cards_of_rank[:3])
                if count == 4:
                    actions.append(cards_of_rank[:4])

            actions.extend(self._find_straights(hand, ranks))
            actions.extend(self._find_consecutive_pairs(hand, ranks))

        else:
            for rank, count in ranks.items():
                rv = self.ranking.rank_value(rank)
                cards_of_rank = [c for c in hand if c.rank == rank]

                if last_type == HandType.SINGLE and count >= 1:
                    if self.can_beat(HandType.SINGLE, rv, 1, last_type, last_rank, last_len):
                        actions.append(cards_of_rank[:1])

                elif last_type == HandType.PAIR and count >= 2:
                    if self.can_beat(HandType.PAIR, rv, 2, last_type, last_rank, last_len):
                        actions.append(cards_of_rank[:2])

                elif last_type == HandType.TRIPLE and count >= 3:
                    if self.can_beat(HandType.TRIPLE, rv, 3, last_type, last_rank, last_len):
                        actions.append(cards_of_rank[:3])

                elif last_type == HandType.BOMB and count == 4:
                    if self.can_beat(HandType.BOMB, rv, 4, last_type, last_rank, last_len):
                        actions.append(cards_of_rank[:4])

            if last_type == HandType.STRAIGHT:
                actions.extend(self._find_straights(hand, ranks, min_len=last_len,
                                                     min_rank=last_rank))

            if last_type == HandType.CONSECUTIVE_PAIRS:
                actions.extend(self._find_consecutive_pairs(hand, ranks, min_pairs=last_len//2,
                                                            min_rank=last_rank))

        for rank, count in ranks.items():
            if count == 4:
                rv = self.ranking.rank_value(rank)
                if self.can_beat(HandType.BOMB, rv, 4, last_type, last_rank, last_len):
                    cards_of_rank = [c for c in hand if c.rank == rank]
                    bomb_action = cards_of_rank[:4]
                    if bomb_action not in actions:
                        actions.append(bomb_action)

        return actions

    def _find_straights(self, hand, ranks, min_len=5, min_rank=None):
        unique_ranks = sorted(set(ranks.keys()), key=lambda r: self.ranking.rank_value(r))
        rank_values = [self.ranking.rank_value(r) for r in unique_ranks]
        max_val = self.ranking.rank_value('A')

        straights = []
        i = 0
        while i < len(rank_values):
            if rank_values[i] > max_val:
                break
            j = i + 1
            while j < len(rank_values) and j - i < 13 and rank_values[j] == rank_values[j-1] + 1 and rank_values[j] <= max_val + 1:
                j += 1
            if j - i >= min_len:
                for k in range(i, j - min_len + 1):
                    for length in range(min_len, j - k + 1):
                        if min_rank is not None and rank_values[k] < min_rank:
                            continue
                        if min_rank is not None and length != min_len:
                            continue
                        if min_rank is not None and length > 5:
                            continue
                        cards = []
                        for idx in range(k, k + length):
                            r = unique_ranks[idx]
                            cards_of_r = [c for c in hand if c.rank == r]
                            cards.append(cards_of_r[0])
                        straights.append(cards)
            i = j

        return straights

    def _find_consecutive_pairs(self, hand, ranks, min_pairs=3, min_rank=None):
        pairs = [(r, self.ranking.rank_value(r)) for r, c in ranks.items() if c >= 2]
        pairs.sort(key=lambda x: x[1])
        max_val = self.ranking.rank_value('A')

        result = []
        i = 0
        while i < len(pairs):
            if pairs[i][1] > max_val:
                break
            j = i + 1
            while j < len(pairs) and j - i < 13 and pairs[j][1] == pairs[j-1][1] + 1 and pairs[j][1] <= max_val + 1:
                j += 1
            if j - i >= min_pairs:
                for k in range(i, j - min_pairs + 1):
                    for length in range(min_pairs, j - k + 1):
                        if min_rank is not None and pairs[k][1] < min_rank:
                            continue
                        if min_rank is not None and length != min_pairs:
                            continue
                        cards = []
                        for idx in range(k, k + length):
                            r = pairs[idx][0]
                            cards_of_r = [c for c in hand if c.rank == r]
                            cards.extend(cards_of_r[:2])
                        result.append(cards)
            i = j

        return result
