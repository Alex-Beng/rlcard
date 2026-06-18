class ZSYJudger:
    def __init__(self, players, scoring):
        self.players = players
        self.scoring = scoring

    def judge_game_over(self, winner_ranking):
        return len(winner_ranking) >= len(self.players) - 1

    def judge_payoffs(self, winner_ranking, num_players):
        full_ranking = list(winner_ranking)
        remaining = [p.player_id for p in self.players if p.player_id not in full_ranking]
        full_ranking.extend(remaining)
        return self.scoring.compute_payoffs(full_ranking, num_players)
