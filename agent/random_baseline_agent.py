"""
Random Baseline Agent
======================

The lower-bound comparison point for the ablation study (research/REVISION_PLAN_incit2026.md,
Phase 4). Picks a uniformly random action every step -- no learning, no
memory, no state. This is what "the agent found nothing meaningful because
it's smart" needs to be measured against: if Extended D3QN can't beat this,
the paper has nothing to claim.

Implements the same act/remember/replay/save/load interface as
ImprovedDQNAgent and the legacy DQNAgent so it plugs into the same training
harness without special-casing -- remember/replay are no-ops (there's
nothing to learn), save/load just persist enough to keep the harness happy.
"""

import json
import os
import random

import numpy as np


class RandomBaselineAgent:
    def __init__(self, state_dim: int, action_dim: int, seed=None):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.rng = random.Random(seed)

    def act(self, state: np.ndarray, training: bool = True) -> int:
        return self.rng.randrange(self.action_dim)

    def remember(self, state, action, reward, next_state, done) -> None:
        pass  # no learning -- nothing to store

    def replay(self):
        return None  # no loss -- nothing is ever trained

    def save(self, filepath: str) -> None:
        # No weights to save; write a small marker so downstream tooling
        # (checkpoint listing, resume logic) doesn't choke on a missing file.
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(
                {"agent": "random_baseline", "state_dim": self.state_dim, "action_dim": self.action_dim},
                f,
            )

    def load(self, filepath: str) -> None:
        pass  # nothing to load -- policy is stateless


if __name__ == "__main__":
    # Standalone self-test, same spirit as agent/improved_dqn_agent.py's.
    print("RandomBaselineAgent standalone self-test")
    agent = RandomBaselineAgent(state_dim=15, action_dim=50, seed=0)
    state = np.zeros(15, dtype=np.float32)
    actions = [agent.act(state) for _ in range(1000)]
    assert all(0 <= a < 50 for a in actions), "action out of range"
    assert len(set(actions)) > 1, "not actually random"
    agent.remember(state, 0, 1.0, state, False)
    assert agent.replay() is None
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "random.json")
        agent.save(path)
        agent.load(path)
    print(f"✅ ALL CHECKS PASSED -- {len(set(actions))}/50 unique actions seen in 1000 draws")
