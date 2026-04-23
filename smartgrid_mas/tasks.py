from dataclasses import dataclass
from typing import Dict


@dataclass
class TaskConfig:
    task_id: str
    description: str
    max_steps: int
    initial_demand_mwh: float
    initial_renewable_mwh: float
    peaker_capacity_mwh: float
    ev_storage_mwh: float
    ev_storage_capacity_mwh: float
    base_price_usd_per_mwh: float
    demand_trend_mwh: float
    renewable_trend_mwh: float
    demand_volatility: float
    renewable_volatility: float
    shock_step: int
    shock_renewable_drop: float
    hint: str


TASKS: Dict[str, TaskConfig] = {
    "default": TaskConfig(
        task_id="default",
        description=(
            "Hybrid multi-agent smart-grid market simulation. Agents submit strategic bids, "
            "market clears, and LDU enforces physical feasibility with correction logs."
        ),
        max_steps=24,
        initial_demand_mwh=120.0,
        initial_renewable_mwh=70.0,
        peaker_capacity_mwh=85.0,
        ev_storage_mwh=25.0,
        ev_storage_capacity_mwh=60.0,
        base_price_usd_per_mwh=45.0,
        demand_trend_mwh=1.2,
        renewable_trend_mwh=-0.6,
        demand_volatility=4.0,
        renewable_volatility=6.0,
        shock_step=16,
        shock_renewable_drop=22.0,
        hint=(
            "Coordinate bids with expected dispatch feasibility. Market-optimal bids that violate "
            "physical constraints are corrected by LDU and reduce reward."
        ),
    ),
    "long_horizon": TaskConfig(
        task_id="long_horizon",
        description=(
            "Extended 48-step planning regime with recurring scarcity windows and delayed consequences. "
            "This task emphasizes long-horizon stability and storage foresight."
        ),
        max_steps=48,
        initial_demand_mwh=135.0,
        initial_renewable_mwh=78.0,
        peaker_capacity_mwh=90.0,
        ev_storage_mwh=32.0,
        ev_storage_capacity_mwh=75.0,
        base_price_usd_per_mwh=48.0,
        demand_trend_mwh=1.5,
        renewable_trend_mwh=-0.8,
        demand_volatility=5.0,
        renewable_volatility=7.0,
        shock_step=28,
        shock_renewable_drop=26.0,
        hint=(
            "Favor smooth dispatch and avoid repeated infeasible corrections. Battery misuse early in the "
            "episode causes compounding penalties later."
        ),
    ),
    "stress_shock": TaskConfig(
        task_id="stress_shock",
        description=(
            "Shock-heavy reliability scenario. Market remains strategic, but severe renewable drop and high "
            "demand volatility test emergency balancing behavior."
        ),
        max_steps=30,
        initial_demand_mwh=150.0,
        initial_renewable_mwh=85.0,
        peaker_capacity_mwh=96.0,
        ev_storage_mwh=24.0,
        ev_storage_capacity_mwh=70.0,
        base_price_usd_per_mwh=55.0,
        demand_trend_mwh=2.0,
        renewable_trend_mwh=-1.0,
        demand_volatility=7.5,
        renewable_volatility=9.0,
        shock_step=12,
        shock_renewable_drop=35.0,
        hint=(
            "Expect early shock and repeated scarcity. Policies must adapt quickly while keeping LDU corrections low."
        ),
    ),
}


def get_task(task_id: str) -> TaskConfig:
    if task_id not in TASKS:
        raise ValueError(f"Unknown task_id '{task_id}'. Available: {list(TASKS.keys())}")
    return TASKS[task_id]


def list_tasks() -> list[str]:
    return list(TASKS.keys())
