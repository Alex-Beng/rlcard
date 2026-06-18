STANDARD_RANK_ORDER = ['3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A', '2']
CARD_RANK_STR = ['3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A', '2']

class StandardRanking:
    def rank_value(self, rank):
        return STANDARD_RANK_ORDER.index(rank)

    @property
    def all_ranks(self):
        return list(STANDARD_RANK_ORDER)

    @property
    def deck_size(self):
        return 52

RANKING_REGISTRY = {
    'standard': StandardRanking,
}

def create_ranking(name='standard'):
    cls = RANKING_REGISTRY.get(name)
    if cls is None:
        raise ValueError('Unknown ranking: {}'.format(name))
    return cls()
