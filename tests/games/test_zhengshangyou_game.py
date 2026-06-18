import unittest
from rlcard.games.zhengshangyou import Game
from rlcard.games.zhengshangyou.hand_checker import HandChecker, HandType
from rlcard.games.zhengshangyou.ranking import create_ranking

class TestZSYGame(unittest.TestCase):

    def test_init_game(self):
        game = Game()
        state, player_id = game.init_game()
        self.assertIsNotNone(state)
        self.assertIn(player_id, range(4))
        total_cards = sum(len(p.hand) for p in game.players)
        self.assertEqual(total_cards, 52)

    def test_configure(self):
        game = Game()
        game.configure({'game_num_players': 4})
        self.assertEqual(game.num_players, 4)

    def test_get_num_players(self):
        game = Game()
        self.assertEqual(game.get_num_players(), 4)

    def test_get_player_id(self):
        game = Game()
        game.init_game()
        pid = game.get_player_id()
        self.assertIn(pid, range(4))

    def test_first_player_has_3d(self):
        game = Game()
        game.init_game()
        first_player = game.players[game.current_player_id]
        found_3d = any(c.suit == 'D' and c.rank == '3' for c in first_player.hand)
        self.assertTrue(found_3d)

    def test_step_pass(self):
        game = Game()
        state, pid = game.init_game()
        state, next_pid = game.step('pass')
        self.assertIsNotNone(state)

    def test_is_over_initially(self):
        game = Game()
        game.init_game()
        self.assertFalse(game.is_over())

    def test_get_payoffs(self):
        game = Game()
        game.init_game()
        game.winner_ranking = [0, 1, 2]
        payoffs = game.get_payoffs()
        self.assertEqual(len(payoffs), 4)


class TestHandChecker(unittest.TestCase):

    def setUp(self):
        self.checker = HandChecker(create_ranking('standard'))
        from rlcard.games.base import Card
        self.Card = Card

    def test_single(self):
        cards = [self.Card('S', '3')]
        result = self.checker.classify(cards)
        self.assertEqual(result[0], HandType.SINGLE)

    def test_pair(self):
        cards = [self.Card('S', '5'), self.Card('H', '5')]
        result = self.checker.classify(cards)
        self.assertEqual(result[0], HandType.PAIR)

    def test_triple(self):
        cards = [self.Card('S', 'K'), self.Card('H', 'K'), self.Card('D', 'K')]
        result = self.checker.classify(cards)
        self.assertEqual(result[0], HandType.TRIPLE)

    def test_bomb(self):
        cards = [self.Card('S', '8'), self.Card('H', '8'), self.Card('D', '8'), self.Card('C', '8')]
        result = self.checker.classify(cards)
        self.assertEqual(result[0], HandType.BOMB)

    def test_straight(self):
        cards = [self.Card('S', '3'), self.Card('H', '4'), self.Card('D', '5'),
                 self.Card('C', '6'), self.Card('S', '7')]
        result = self.checker.classify(cards)
        self.assertEqual(result[0], HandType.STRAIGHT)

    def test_short_straight_invalid(self):
        cards = [self.Card('S', '3'), self.Card('H', '4'), self.Card('D', '5'),
                 self.Card('C', '6')]
        result = self.checker.classify(cards)
        self.assertIsNone(result)

    def test_can_beat_bomb_vs_single(self):
        self.assertTrue(self.checker.can_beat(
            HandType.BOMB, 0, 4, HandType.SINGLE, 0, 1))

    def test_can_beat_higher_single(self):
        self.assertTrue(self.checker.can_beat(
            HandType.SINGLE, 2, 1, HandType.SINGLE, 1, 1))

    def test_cannot_beat_lower_single(self):
        self.assertFalse(self.checker.can_beat(
            HandType.SINGLE, 1, 1, HandType.SINGLE, 2, 1))

    def test_cannot_beat_different_type(self):
        self.assertFalse(self.checker.can_beat(
            HandType.SINGLE, 5, 1, HandType.PAIR, 3, 2))

    def test_get_legal_actions_lead(self):
        cards = [self.Card('S', '3'), self.Card('H', '3'), self.Card('D', '5')]
        actions = self.checker.get_legal_actions(cards, HandType.PASS, -1, 0)
        self.assertTrue(len(actions) > 0)


if __name__ == '__main__':
    unittest.main()
