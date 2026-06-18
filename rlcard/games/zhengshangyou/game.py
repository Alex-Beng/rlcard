import numpy as np
from copy import deepcopy

from rlcard.games.base import Card
from rlcard.games.zhengshangyou.player import ZSYPlayer
from rlcard.games.zhengshangyou.dealer import ZSYDealer
from rlcard.games.zhengshangyou.judger import ZSYJudger
from rlcard.games.zhengshangyou.hand_checker import HandChecker, HandType
from rlcard.games.zhengshangyou.ranking import create_ranking
from rlcard.games.zhengshangyou.scoring import create_scoring
from rlcard.games.zhengshangyou.presets import REGIONAL_PRESETS

class ZSYGame:
    def __init__(self, allow_step_back=False):
        self.allow_step_back = allow_step_back
        self.np_random = np.random.RandomState()
        self.num_players = 4
        self.ranking = create_ranking('standard')
        self.hand_checker = HandChecker(self.ranking)
        self.scoring = create_scoring('standard')

    def configure(self, game_config):
        variant = game_config.get('game_variant', 'standard')
        if variant in REGIONAL_PRESETS:
            config = REGIONAL_PRESETS[variant].copy()
            config.update({k: v for k, v in game_config.items() if k.startswith('game_')})
        else:
            config = game_config
        self.num_players = config.get('game_num_players', 4)
        ranking_name = config.get('game_card_ranking', 'standard')
        self.ranking = create_ranking(ranking_name)
        self.hand_checker = HandChecker(self.ranking)
        scoring_name = config.get('game_scoring', 'standard')
        self.scoring = create_scoring(scoring_name)

    def init_game(self):
        self.dealer = ZSYDealer(self.np_random)
        self.players = [ZSYPlayer(i, self.np_random) for i in range(self.num_players)]
        self.dealer.deal_cards(self.players)
        self.current_player_id = self._find_first_player()
        self.winner_ranking = []
        self.last_play_type = HandType.PASS
        self.last_play_rank = -1
        self.last_play_len = 0
        self.last_play_player = None
        self.consecutive_passes = 0
        self.trace = []
        self.history = []
        self.judger = ZSYJudger(self.players, self.scoring)
        state = self.get_state(self.current_player_id)
        return state, self.current_player_id

    def _find_first_player(self):
        for i, player in enumerate(self.players):
            for card in player.hand:
                if card.suit == 'D' and card.rank == '3':
                    return i
        return 0

    def step(self, action):
        if self.allow_step_back:
            self.history.append(self._snapshot())
        player = self.players[self.current_player_id]
        if action == 'pass':
            self.trace.append((self.current_player_id, 'pass'))
            self.consecutive_passes += 1
            if self.consecutive_passes >= self.num_players - 1:
                self.last_play_type = HandType.PASS
                self.last_play_rank = -1
                self.last_play_len = 0
                self.consecutive_passes = 0
                if self.last_play_player is not None and self.last_play_player not in self.winner_ranking:
                    self.current_player_id = self.last_play_player
                else:
                    self.current_player_id = self._next_alive_player(self.current_player_id)
            else:
                self.current_player_id = self._next_alive_player(self.current_player_id)
        else:
            cards = self._parse_action(action)
            classified = self.hand_checker.classify(cards)
            if classified is None:
                raise ValueError('Invalid action: {}'.format(action))
            htype, hrank, hlen = classified
            player.remove_cards(cards)
            self.last_play_type = htype
            self.last_play_rank = hrank
            self.last_play_len = hlen
            self.last_play_player = self.current_player_id
            self.consecutive_passes = 0
            action_str = ' '.join(sorted(c.get_index() for c in cards))
            self.trace.append((self.current_player_id, action_str))
            if not player.hand:
                self.winner_ranking.append(self.current_player_id)
                if self.judger.judge_game_over(self.winner_ranking):
                    self.current_player_id = self._next_alive_player(self.current_player_id)
                else:
                    self.current_player_id = self._next_alive_player(self.current_player_id)
                    self.last_play_type = HandType.PASS
                    self.last_play_rank = -1
                    self.last_play_len = 0
                    self.last_play_player = None
                    self.consecutive_passes = 0
            else:
                self.current_player_id = self._next_alive_player(self.current_player_id)
        state = self.get_state(self.current_player_id)
        return state, self.current_player_id

    def _next_alive_player(self, current):
        next_id = (current + 1) % self.num_players
        while next_id in self.winner_ranking:
            next_id = (next_id + 1) % self.num_players
            if next_id == current:
                break
        return next_id

    def _parse_action(self, action):
        parts = action.strip().split()
        cards = []
        for part in parts:
            if len(part) >= 2:
                suit = part[0]
                rank = part[1:]
            else:
                continue
            card = Card(suit, rank)
            if card in self.players[self.current_player_id].hand:
                cards.append(card)
        return cards

    def _snapshot(self):
        return {
            'current_player': self.current_player_id,
            'winner_ranking': list(self.winner_ranking),
            'last_play_type': self.last_play_type,
            'last_play_rank': self.last_play_rank,
            'last_play_len': self.last_play_len,
            'last_play_player': self.last_play_player,
            'consecutive_passes': self.consecutive_passes,
            'trace': list(self.trace),
            'players': [{
                'hand': list(p.hand),
                'player_id': p.player_id,
                'rank': p.rank,
            } for p in self.players],
            'deck': list(self.dealer.deck),
        }

    def step_back(self):
        if not self.history:
            return False
        state = self.history.pop()
        self.current_player_id = state['current_player']
        self.winner_ranking = state['winner_ranking']
        self.last_play_type = state['last_play_type']
        self.last_play_rank = state['last_play_rank']
        self.last_play_len = state['last_play_len']
        self.last_play_player = state['last_play_player']
        self.consecutive_passes = state['consecutive_passes']
        self.trace = state['trace']
        for i, pdata in enumerate(state['players']):
            self.players[i].hand = list(pdata['hand'])
            self.players[i].player_id = pdata['player_id']
            self.players[i].rank = pdata['rank']
        self.dealer.deck = list(state['deck'])
        return True

    def get_state(self, player_id):
        player = self.players[player_id]
        legal_actions = self._get_legal_actions(player)
        num_cards_left = [len(p.hand) if p.player_id not in self.winner_ranking else 0
                          for p in self.players]
        last_play_info = (self.last_play_type, self.last_play_rank, self.last_play_len)
        state = player.get_state(last_play_info, num_cards_left,
                                 self.consecutive_passes, legal_actions)
        state['current_player'] = player_id
        return state

    def _get_legal_actions(self, player):
        hand = player.hand
        if not hand:
            return ['pass']
        raw_actions = self.hand_checker.get_legal_actions(
            hand, self.last_play_type, self.last_play_rank, self.last_play_len)
        actions = []
        if self.last_play_type != HandType.PASS:
            actions.append('pass')
        for cards in raw_actions:
            action_str = ' '.join(c.get_index() for c in cards)
            actions.append(action_str)
        return actions

    def get_num_actions(self):
        return 10000

    def get_player_id(self):
        return self.current_player_id

    def get_num_players(self):
        return self.num_players

    def is_over(self):
        if len(self.winner_ranking) >= self.num_players - 1:
            return True
        return self.judger is not None and self.judger.judge_game_over(self.winner_ranking)

    def get_payoffs(self):
        return self.judger.judge_payoffs(self.winner_ranking, self.num_players)
