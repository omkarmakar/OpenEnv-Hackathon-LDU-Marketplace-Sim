import random
from typing import Dict, Tuple

from smartgrid_mas.tasks import TaskConfig


def evolve_grid(
    demand_mwh: float,
    renewable_mwh: float,
    base_price_usd_per_mwh: float,
    step: int,
    task: TaskConfig,
    rng: random.Random,
) -> Tuple[float, float, float, Dict]:
    shock_active = step == task.shock_step

    demand_noise = rng.gauss(0.0, task.demand_volatility)
    renewable_noise = rng.gauss(0.0, task.renewable_volatility)

    next_demand = demand_mwh + task.demand_trend_mwh + demand_noise
    next_renewable = renewable_mwh + task.renewable_trend_mwh + renewable_noise

    if shock_active:
        next_renewable = max(0.0, next_renewable - task.shock_renewable_drop)

    next_demand = max(20.0, next_demand)
    next_renewable = max(0.0, next_renewable)

    scarcity_ratio = max(0.0, (next_demand - next_renewable) / 300.0)
    implied_price = base_price_usd_per_mwh * (1.0 + scarcity_ratio)
    next_price = min(200.0, max(5.0, implied_price))

    return (
        round(next_demand, 3),
        round(next_renewable, 3),
        round(next_price, 3),
        {
            "shock_active": shock_active,
            "demand_noise": round(demand_noise, 3),
            "renewable_noise": round(renewable_noise, 3),
        },
    )
