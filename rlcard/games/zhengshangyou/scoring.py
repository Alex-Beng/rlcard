import numpy as np

class StandardScoring:
    def compute_payoffs(self, winner_ranking, num_players):
        payoffs = [0] * num_players
        for pos, player_id in enumerate(winner_ranking):
            if pos == 0:
                payoffs[player_id] = 2
            elif pos == num_players - 1:
                payoffs[player_id] = -2
            else:
                payoffs[player_id] = 1 if pos < num_players // 2 else -1
        return np.array(payoffs)

SCORING_REGISTRY = {
    'standard': StandardScoring,
}

def create_scoring(name='standard'):
    cls = SCORING_REGISTRY.get(name)
    if cls is None:
        raise ValueError('Unknown scoring: {}'.format(name))
    return cls()
