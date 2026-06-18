import unittest
import numpy as np
import rlcard
from rlcard.agents.random_agent import RandomAgent


class TestZhengshangyouEnv(unittest.TestCase):

    def test_make(self):
        env = rlcard.make('zhengshangyou')
        self.assertEqual(env.num_players, 4)

    def test_reset(self):
        env = rlcard.make('zhengshangyou')
        state, player_id = env.reset()
        self.assertIn('obs', state)
        self.assertIn('legal_actions', state)
        self.assertIn(player_id, range(4))

    def test_state_shape(self):
        env = rlcard.make('zhengshangyou')
        self.assertEqual(env.state_shape, [[167], [167], [167], [167]])

    def test_action_shape(self):
        env = rlcard.make('zhengshangyou')
        self.assertEqual(env.action_shape, [[53], [53], [53], [53]])

    def test_run(self):
        env = rlcard.make('zhengshangyou')
        agents = [RandomAgent(env.num_actions) for _ in range(env.num_players)]
        env.set_agents(agents)
        trajectories, payoffs = env.run(is_training=False)
        self.assertEqual(len(trajectories), 4)
        self.assertEqual(len(payoffs), 4)

    def test_run_multiple(self):
        env = rlcard.make('zhengshangyou')
        agents = [RandomAgent(env.num_actions) for _ in range(env.num_players)]
        env.set_agents(agents)
        for _ in range(5):
            _, payoffs = env.run()
            self.assertEqual(len(payoffs), 4)
            self.assertAlmostEqual(sum(payoffs), 0.0)

    def test_get_payoffs(self):
        env = rlcard.make('zhengshangyou')
        env.reset()
        env.game.winner_ranking = [0, 1, 2]
        payoffs = env.get_payoffs()
        self.assertEqual(len(payoffs), 4)

    def test_get_perfect_information(self):
        env = rlcard.make('zhengshangyou')
        env.reset()
        info = env.get_perfect_information()
        self.assertIn('hand_cards', info)
        self.assertIn('current_player', info)

    def test_get_action_feature(self):
        env = rlcard.make('zhengshangyou')
        env.reset()
        state = env.get_state(0)
        legal = list(state['legal_actions'].keys())
        if legal:
            feat = env.get_action_feature(legal[0])
            self.assertEqual(len(feat), 53)

    def test_decode_action(self):
        env = rlcard.make('zhengshangyou')
        env.reset()
        state = env.get_state(0)
        legal = list(state['legal_actions'].keys())
        if legal:
            action = env._decode_action(legal[0])
            self.assertIsInstance(action, str)


if __name__ == '__main__':
    unittest.main()
