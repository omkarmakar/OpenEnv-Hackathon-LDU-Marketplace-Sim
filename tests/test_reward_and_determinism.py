from smartgrid_mas.engine.policies import adaptive_stackelberg_action, heuristic_joint_action
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
        "reserve_requirement_mwh": 12.0,
        "reserve_shortfall_mwh": 2.0,
        "reserve_commitment_penalty_mwh": 1.0,
        "reserve_commitment_active": True,
        "ramp_violation_mwh": 1.0,
        "startup_cost_usd": 50.0,
        "emissions_tco2": 8.0,
        "frequency_hz": 49.7,
        "line_loading_ratio": 1.04,
        "emergency_dispatch_triggered": True,
        "stability_risk_index": 0.5,
    }
    reward = compute_reward(
        dispatch=dispatch,
        clearing_price=52,
        demand_mwh=100,
        prior_gap=-3,
        carbon_price_usd_per_tco2=50.0,
    )
    assert 0.0 <= reward.score <= 1.0
    assert reward.blackout_penalty >= 0.0
    assert reward.infeasibility_penalty >= 0.0
    assert reward.reserve_adequacy_score >= 0.0
    assert reward.emissions_intensity_tco2_per_mwh >= 0.0


def test_unsafe_trajectory_scores_lower_than_stable():
    stable_dispatch = {
        "delivered_supply_mwh": 100.0,
        "unmet_demand_mwh": 0.0,
        "oversupply_mwh": 0.0,
        "correction_count": 0,
        "storage_loss_mwh": 0.2,
        "transmission_loss_mwh": 2.8,
        "renewable_dispatch_mwh": 62.0,
        "peaker_dispatch_mwh": 25.0,
        "ev_discharge_mwh": 13.0,
        "reserve_requirement_mwh": 12.0,
        "reserve_shortfall_mwh": 0.0,
        "reserve_commitment_penalty_mwh": 0.0,
        "reserve_commitment_active": False,
        "ramp_violation_mwh": 0.0,
        "startup_cost_usd": 0.0,
        "emissions_tco2": 10.0,
        "frequency_hz": 49.98,
        "line_loading_ratio": 0.88,
        "emergency_dispatch_triggered": False,
        "stability_risk_index": 0.1,
    }
    unsafe_dispatch = {
        "delivered_supply_mwh": 80.0,
        "unmet_demand_mwh": 20.0,
        "oversupply_mwh": 0.0,
        "correction_count": 4,
        "storage_loss_mwh": 1.3,
        "transmission_loss_mwh": 5.2,
        "renewable_dispatch_mwh": 22.0,
        "peaker_dispatch_mwh": 58.0,
        "ev_discharge_mwh": 0.0,
        "reserve_requirement_mwh": 12.0,
        "reserve_shortfall_mwh": 8.5,
        "reserve_commitment_penalty_mwh": 9.0,
        "reserve_commitment_active": True,
        "ramp_violation_mwh": 5.0,
        "startup_cost_usd": 180.0,
        "emissions_tco2": 26.0,
        "frequency_hz": 49.42,
        "line_loading_ratio": 1.18,
        "emergency_dispatch_triggered": True,
        "stability_risk_index": 0.87,
    }
    stable = compute_reward(stable_dispatch, clearing_price=50, demand_mwh=100, prior_gap=0.0, carbon_price_usd_per_tco2=50)
    unsafe = compute_reward(unsafe_dispatch, clearing_price=50, demand_mwh=100, prior_gap=0.0, carbon_price_usd_per_tco2=50)
    assert stable.score > unsafe.score


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


def test_seeded_adaptive_episode_regression_deterministic():
    env_a = SmartGridMarketEnv()
    env_b = SmartGridMarketEnv()

    ra = env_a.reset(task_id="default", seed=42)
    rb = env_b.reset(task_id="default", seed=42)

    sid_a = ra.session_id
    sid_b = rb.session_id

    rewards_a = []
    rewards_b = []

    for _ in range(8):
        obs_a = env_a.state(sid_a).observation
        obs_b = env_b.state(sid_b).observation
        action_a = adaptive_stackelberg_action(obs_a, personality="balanced")
        action_b = adaptive_stackelberg_action(obs_b, personality="balanced")
        step_a = env_a.step(action_a, sid_a)
        step_b = env_b.step(action_b, sid_b)
        rewards_a.append(round(step_a.reward.score, 6))
        rewards_b.append(round(step_b.reward.score, 6))

    assert rewards_a == rewards_b
