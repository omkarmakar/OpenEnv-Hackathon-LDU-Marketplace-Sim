import random
import math
from typing import Dict, Tuple

from smartgrid_mas.tasks import TaskConfig


def _daily_profile(step: int, max_steps: int) -> Tuple[float, float]:
    phase = (step % max_steps) / max_steps

    morning_peak = math.exp(-((phase - 0.33) / 0.10) ** 2)
    evening_peak = math.exp(-((phase - 0.75) / 0.12) ** 2)
    demand_multiplier = 0.90 + 0.18 * morning_peak + 0.35 * evening_peak

    midday_solar = math.exp(-((phase - 0.50) / 0.18) ** 2)
    renewable_multiplier = max(0.05, 0.15 + 1.15 * midday_solar)

    return demand_multiplier, renewable_multiplier


def evolve_grid(
    demand_mwh: float,
    renewable_mwh: float,
    base_price_usd_per_mwh: float,
    step: int,
    task: TaskConfig,
    rng: random.Random,
) -> Tuple[float, float, float, Dict]:
    shock_active = step == task.shock_step
    contingency_active = step == task.contingency_step and task.contingency_type != "none"

    demand_noise = rng.gauss(0.0, task.demand_volatility)
    renewable_noise = rng.gauss(0.0, task.renewable_volatility)
    demand_multiplier, renewable_multiplier = _daily_profile(step=step, max_steps=task.max_steps)

    next_demand = demand_mwh * demand_multiplier + task.demand_trend_mwh + demand_noise
    next_renewable = renewable_mwh * renewable_multiplier + task.renewable_trend_mwh + renewable_noise

    if shock_active:
        next_renewable = max(0.0, next_renewable - task.shock_renewable_drop)

    next_demand = max(20.0, next_demand)
    next_renewable = max(0.0, next_renewable)

    forecast_demand = max(20.0, next_demand + rng.gauss(0.0, task.load_forecast_sigma))
    forecast_renewable = max(0.0, next_renewable + rng.gauss(0.0, task.renewable_forecast_sigma))
    peaker_capacity_multiplier = 1.0
    transmission_loss_multiplier = 1.0
    n1_component = "none"
    if contingency_active:
        derate = max(0.0, min(task.contingency_derate_pct, 0.95))
        if task.contingency_type == "peaker_trip":
            peaker_capacity_multiplier = 1.0 - derate
        elif task.contingency_type == "transmission_derate":
            transmission_loss_multiplier = 1.0 + derate
        elif task.contingency_type in {"n_minus_one", "n1_outage"}:
            n1_component = rng.choice(["generator", "feeder"])
            if n1_component == "generator":
                peaker_capacity_multiplier = 1.0 - derate
            else:
                transmission_loss_multiplier = 1.0 + derate

    scarcity_ratio = max(0.0, (next_demand - next_renewable) / 300.0)
    implied_price = base_price_usd_per_mwh * (1.0 + scarcity_ratio)
    next_price = min(200.0, max(5.0, implied_price))

    return (
        round(next_demand, 3),
        round(next_renewable, 3),
        round(next_price, 3),
        {
            "shock_active": shock_active,
            "contingency_active": contingency_active,
            "contingency_type": task.contingency_type if contingency_active else "none",
            "n1_component": n1_component,
            "peaker_capacity_multiplier": round(peaker_capacity_multiplier, 4),
            "transmission_loss_multiplier": round(transmission_loss_multiplier, 4),
            "demand_noise": round(demand_noise, 3),
            "renewable_noise": round(renewable_noise, 3),
            "demand_multiplier": round(demand_multiplier, 4),
            "renewable_multiplier": round(renewable_multiplier, 4),
            "forecast_demand_mwh": round(forecast_demand, 3),
            "forecast_renewable_mwh": round(forecast_renewable, 3),
            "load_forecast_error_mwh": round(forecast_demand - next_demand, 3),
            "renewable_forecast_error_mwh": round(forecast_renewable - next_renewable, 3),
        },
    )
