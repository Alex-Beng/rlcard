import rlcard

def run():
    env = rlcard.make('zhengshangyou')
    state, player_id = env.reset()
    print('>> 争上游 (Zheng Shang You)')
    print('输入卡片串打出，例如 "D3 D4 D5 D6 D7" 表示 3-7 顺子')
    print('输入 "pass" 过牌')
    print()

    while not env.is_over():
        print('\n=============== Current State ===============')
        player = env.game.players[player_id]
        print('Your hand:', ', '.join(c.get_index() for c in player.hand))
        print('Cards left:', [len(p.hand) for p in env.game.players])
        print('Legal actions:', state['raw_legal_actions'])
        print('=============================================\n')

        action = input('>> Your action: ').strip()
        while action not in state['raw_legal_actions']:
            print('Invalid action. Legal actions:', state['raw_legal_actions'])
            action = input('>> Your action: ').strip()

        state, player_id = env.step(action, raw_action=True)

    print('\n=============== Game Over ===============')
    print('Final ranking:', env.game.winner_ranking)
    payoffs = env.get_payoffs()
    for i, p in enumerate(payoffs):
        print('Player {}: {}'.format(i, p))

if __name__ == '__main__':
    run()
