from smartgrid_mas.engine.policies import heuristic_joint_action
from smartgrid_mas.engine.reward import compute_reward
from smartgrid_mas.env import SmartGridMarketEnv


def test_reward_bounds_and_consistency():
    dispatch = {
        "delivered_supply_mwh": 95.0,
        "unmet_demand_mwh": 5.0,
        "oversupply_mwh": 0.0,
        "correction_count": 2,
        "storage_loss_mwh": 0.4,
        "renewable_dispatch_mwh": 50.0,
    }
    reward = compute_reward(dispatch=dispatch, clearing_price=52, demand_mwh=100, prior_gap=-3)
    assert 0.0 <= reward.score <= 1.0
    assert reward.blackout_penalty >= 0.0
    assert reward.infeasibility_penalty >= 0.0


def test_seeded_episode_regression_deterministic():
    env_a = SmartGridMarketEnv()
    env_b = SmartGridMarketEnv()

    ra = env_a.reset(task_id="default", seed=123)
    rb = env_b.reset(task_id="default", seed=123)

    sid_a = ra.session_id
    sid_b = rb.session_id

    rewards_a = []
    rewards_b = []

    for _ in range(6):
        obs_a = env_a.state(sid_a).observation
        obs_b = env_b.state(sid_b).observation
        action_a = heuristic_joint_action(obs_a, personality="balanced")
        action_b = heuristic_joint_action(obs_b, personality="balanced")
        step_a = env_a.step(action_a, sid_a)
        step_b = env_b.step(action_b, sid_b)
        rewards_a.append(round(step_a.reward.score, 6))
        rewards_b.append(round(step_b.reward.score, 6))

    assert rewards_a == rewards_b
