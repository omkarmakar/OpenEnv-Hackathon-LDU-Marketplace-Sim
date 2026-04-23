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
    )
}


def get_task(task_id: str) -> TaskConfig:
    if task_id not in TASKS:
        raise ValueError(f"Unknown task_id '{task_id}'. Available: {list(TASKS.keys())}")
    return TASKS[task_id]
