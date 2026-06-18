import numpy as np
from collections import OrderedDict

from rlcard.envs import Env
from rlcard.games.zhengshangyou import Game
from rlcard.games.zhengshangyou.hand_checker import HandType, TYPE_NAMES

CARD_RANK_INDEX = {'3': 0, '4': 1, '5': 2, '6': 3, '7': 4, '8': 5, '9': 6,
                   'T': 7, 'J': 8, 'Q': 9, 'K': 10, 'A': 11, '2': 12}

DEFAULT_GAME_CONFIG = {
    'game_num_players': 4,
}

class ZhengshangyouEnv(Env):
    def __init__(self, config):
        self.name = 'zhengshangyou'
        self.default_game_config = DEFAULT_GAME_CONFIG
        self.game = Game()
        super().__init__(config)
        self.num_actions = self.game.get_num_actions()
        self.state_shape = [[167] for _ in range(self.num_players)]
        self.action_shape = [[53] for _ in range(self.num_players)]
        self.actions = ['pass'] + list(range(self.num_actions - 1))

    def _extract_state(self, state):
        extracted = {}
        player_id = state['current_player']

        hand_vec = np.zeros(52, dtype=np.int8)
        for card in self.game.players[player_id].hand:
            idx = self._card_to_idx(card)
            if idx >= 0:
                hand_vec[idx] = 1

        last_play_vec = np.zeros(52, dtype=np.int8)
        if self.game.last_play_type != HandType.PASS and self.game.trace:
            for entry in reversed(self.game.trace):
                if entry[1] != 'pass':
                    cards = entry[1].split()
                    for card_str in cards:
                        idx = self._card_str_to_idx(card_str)
                        if idx >= 0:
                            last_play_vec[idx] = 1
                    break

        last_type_vec = np.zeros(7, dtype=np.int8)
        if self.game.last_play_type != HandType.PASS:
            last_type_vec[self.game.last_play_type] = 1

        num_cards_left = np.zeros(4 * 14, dtype=np.int8)
        for i, p in enumerate(self.game.players):
            n = len(p.hand)
            if p.player_id in self.game.winner_ranking:
                n = 0
            if n >= 14:
                n = 13
            num_cards_left[i * 14 + n] = 1

        obs = np.concatenate([
            hand_vec,
            last_play_vec,
            last_type_vec,
            num_cards_left,
        ])

        legal_actions = OrderedDict()
        for i, action_str in enumerate(state['legal_actions']):
            legal_actions[i] = self._action_to_feature(action_str)

        extracted['obs'] = obs
        extracted['legal_actions'] = legal_actions
        extracted['raw_obs'] = state
        extracted['raw_legal_actions'] = list(state['legal_actions'])
        extracted['action_record'] = self.action_recorder
        return extracted

    def _card_to_idx(self, card):
        if card.rank not in CARD_RANK_INDEX:
            return -1
        suit_idx = {'S': 0, 'H': 1, 'D': 2, 'C': 3}.get(card.suit, -1)
        if suit_idx < 0:
            return -1
        rank_idx = CARD_RANK_INDEX[card.rank]
        return suit_idx * 13 + rank_idx

    def _card_str_to_idx(self, card_str):
        if len(card_str) < 2:
            return -1
        suit = card_str[0]
        rank = card_str[1:]
        if rank not in CARD_RANK_INDEX:
            return -1
        suit_idx = {'S': 0, 'H': 1, 'D': 2, 'C': 3}.get(suit, -1)
        if suit_idx < 0:
            return -1
        rank_idx = CARD_RANK_INDEX[rank]
        return suit_idx * 13 + rank_idx

    def _action_to_feature(self, action_str):
        feat = np.zeros(53, dtype=np.int8)
        if action_str == 'pass':
            feat[52] = 1
            return feat
        parts = action_str.split()
        for part in parts:
            idx = self._card_str_to_idx(part)
            if idx >= 0:
                feat[idx] = 1
        return feat

    def get_action_feature(self, action):
        action_str = self._decode_action(action)
        return self._action_to_feature(action_str)

    def _decode_action(self, action_id):
        state = self.game.get_state(self.game.current_player_id)
        legal = state['legal_actions']
        if action_id < len(legal):
            return legal[action_id]
        return 'pass'

    def _get_legal_actions(self):
        state = self.game.get_state(self.game.current_player_id)
        return {i: self._action_to_feature(a)
                for i, a in enumerate(state['legal_actions'])}

    def get_payoffs(self):
        return self.game.get_payoffs()

    def get_perfect_information(self):
        state = {}
        state['hand_cards'] = [[c.get_index() for c in p.hand] for p in self.game.players]
        state['winner_ranking'] = list(self.game.winner_ranking)
        state['current_player'] = self.game.current_player_id
        state['last_play'] = self.game.last_play_type
        state['trace'] = list(self.game.trace)
        return state
