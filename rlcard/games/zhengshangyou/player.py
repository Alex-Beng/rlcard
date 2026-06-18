class ZSYPlayer:
    def __init__(self, player_id, np_random):
        self.np_random = np_random
        self.player_id = player_id
        self.hand = []
        self.rank = None

    def set_hand(self, cards):
        self.hand = list(cards)

    def remove_cards(self, cards_to_remove):
        for card in cards_to_remove:
            self.hand.remove(card)

    def get_state(self, last_play_info, num_cards_left, pass_count, legal_actions):
        state = {}
        state['hand'] = [c.get_index() for c in self.hand]
        state['last_play'] = last_play_info
        state['num_cards_left'] = num_cards_left
        state['pass_count'] = pass_count
        state['legal_actions'] = legal_actions
        state['current_player'] = self.player_id
        return state
