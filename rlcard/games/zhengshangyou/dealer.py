import numpy as np
from rlcard.games.base import Card

SUITS = ['S', 'H', 'D', 'C']
RANKS = ['3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A', '2']

class ZSYDealer:
    def __init__(self, np_random):
        self.np_random = np_random
        self.deck = []
        self.shuffle()

    def shuffle(self):
        self.deck = [Card(suit, rank) for suit in SUITS for rank in RANKS]
        self.np_random.shuffle(self.deck)

    def deal_cards(self, players):
        num_players = len(players)
        cards_per_player = len(self.deck) // num_players
        for i, player in enumerate(players):
            start = i * cards_per_player
            end = start + cards_per_player
            player.set_hand(self.deck[start:end])
