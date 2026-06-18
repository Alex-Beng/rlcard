# RLCard — Agent Guide

## Project
Single-package Python library (`rlcard`, v1.2.0) for RL in card games.
GitHub: `datamllab/rlcard`

## Install
```
pip install -e .           # envs only
pip install -e .[torch]    # includes DQN/NFSP/DMC
```
Requires Python 3.7+. Core deps: `numpy>=1.16.3`, `termcolor`.
With `[torch]`: `torch`, `GitPython`, `matplotlib`.

## Entry Points
- `rlcard.make(env_id, config={})` — create environment
- `rlcard.models.load(model_id)` — load pre-trained/rule-based model

## Environments (9 games)
`blackjack`, `leduc-holdem`, `limit-holdem`, `no-limit-holdem`, `doudizhu`,
`mahjong`, `uno`, `gin-rummy`, `bridge`, `zhengshangyou`

Game-specific config (prefix `game_`): supported for `blackjack`, `leduc-holdem`,
`limit-holdem`, `no-limit-holdem`, `zhengshangyou` via `default_game_config`.
Use `game_variant` to select regional presets in `zhengshangyou`.

## Agents
- **Torch required**: `DQNAgent`, `NFSPAgent`, `DMCTrainer` — imported only
  when `torch` installed (checked at runtime in `rlcard/agents/__init__.py`)
- **No torch needed**: `RandomAgent`, `CFRAgent`, human agents
- **CFR** requires `allow_step_back=True` in config

## Tests
```
py.test tests/ --cov=rlcard
```
Test dirs mirror source: `tests/envs/`, `tests/agents/`, `tests/games/`,
`tests/models/`, `tests/utils/`. Uses `unittest`. Determinism helper in
`tests/envs/determism_util.py`.

## Examples
```
python examples/run_random.py --env leduc-holdem
python examples/run_rl.py --env blackjack --algorithm dqn
python examples/run_cfr.py
python examples/run_dmc.py --env doudizhu
python examples/evaluate.py --env leduc-holdem
```
DMC multi-GPU: `examples/scripts/dmc_doudizhu_{1,4}_gpu.sh`

## Human Demos (interactive)
Scripts in `examples/human/` — play against AI or another human:
- `python examples/human/leduc_holdem_human.py` — vs CFR pre-trained model
- `python examples/human/blackjack_human.py` — vs dealer
- `python examples/human/limit_holdem_human.py` — vs RandomAgent
- `python examples/human/nolimit_holdem_human.py` — two human players
- `python examples/human/uno_human.py` — vs RandomAgent
- `python examples/human/gin_rummy_human.py` — GUI with AI
- `python examples/human/zhengshangyou_human.py` — interactive terminal play

Unit tests: `tests/agents/test_leduc_human.py`, `test_uno_human.py`.

## PettingZoo
Optional via `rlcard.utils.pettingzoo_utils`. Examples in `examples/pettingzoo/`.

## CI
GitHub Actions on push/PR to `master`. Runs `py.test tests/ --cov=rlcard`
with Python 3.7–3.11.

## Conventions
- State is a dict: `obs`, `legal_actions`, `raw_obs`, `raw_legal_actions`
- `set_seed()` seeds numpy, torch (if installed), and random
- `get_device()` prefers MPS > CUDA > CPU
- No linter/formatter/typechecker configured
