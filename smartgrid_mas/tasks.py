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
    reserve_margin_ratio: float
    reserve_commitment_threshold_ratio: float
    peaker_ramp_limit_mwh: float
    peaker_activation_delay_steps: int
    ev_ramp_limit_mwh: float
    peaker_startup_cost_usd: float
    peaker_emission_factor_tco2_per_mwh: float
    carbon_price_usd_per_tco2: float
    load_forecast_sigma: float
    renewable_forecast_sigma: float
    contingency_type: str
    contingency_step: int
    contingency_derate_pct: float
    hint: str
    enable_reserve_logic: bool = True
    enable_ramp_limits: bool = True
    enable_startup_emissions: bool = True


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
        reserve_margin_ratio=0.12,
        reserve_commitment_threshold_ratio=1.0,
        peaker_ramp_limit_mwh=14.0,
        peaker_activation_delay_steps=0,
        ev_ramp_limit_mwh=9.0,
        peaker_startup_cost_usd=180.0,
        peaker_emission_factor_tco2_per_mwh=0.45,
        carbon_price_usd_per_tco2=50.0,
        load_forecast_sigma=4.0,
        renewable_forecast_sigma=6.0,
        contingency_type="none",
        contingency_step=-1,
        contingency_derate_pct=0.0,
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
        reserve_margin_ratio=0.14,
        reserve_commitment_threshold_ratio=1.0,
        peaker_ramp_limit_mwh=12.0,
        peaker_activation_delay_steps=1,
        ev_ramp_limit_mwh=8.0,
        peaker_startup_cost_usd=210.0,
        peaker_emission_factor_tco2_per_mwh=0.45,
        carbon_price_usd_per_tco2=60.0,
        load_forecast_sigma=5.5,
        renewable_forecast_sigma=7.0,
        contingency_type="transmission_derate",
        contingency_step=30,
        contingency_derate_pct=0.18,
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
        reserve_margin_ratio=0.16,
        reserve_commitment_threshold_ratio=1.05,
        peaker_ramp_limit_mwh=10.0,
        peaker_activation_delay_steps=1,
        ev_ramp_limit_mwh=7.0,
        peaker_startup_cost_usd=260.0,
        peaker_emission_factor_tco2_per_mwh=0.47,
        carbon_price_usd_per_tco2=70.0,
        load_forecast_sigma=8.0,
        renewable_forecast_sigma=10.0,
        contingency_type="peaker_trip",
        contingency_step=13,
        contingency_derate_pct=0.55,
        hint=(
            "Expect early shock and repeated scarcity. Policies must adapt quickly while keeping LDU corrections low."
        ),
    ),
    "normal": TaskConfig(
        task_id="normal",
        description="Normal operations benchmark with mild variability and no forced shock.",
        max_steps=24,
        initial_demand_mwh=118.0,
        initial_renewable_mwh=74.0,
        peaker_capacity_mwh=86.0,
        ev_storage_mwh=28.0,
        ev_storage_capacity_mwh=62.0,
        base_price_usd_per_mwh=44.0,
        demand_trend_mwh=1.0,
        renewable_trend_mwh=-0.4,
        demand_volatility=3.0,
        renewable_volatility=4.5,
        shock_step=-1,
        shock_renewable_drop=0.0,
        reserve_margin_ratio=0.12,
        reserve_commitment_threshold_ratio=1.0,
        peaker_ramp_limit_mwh=15.0,
        peaker_activation_delay_steps=0,
        ev_ramp_limit_mwh=9.0,
        peaker_startup_cost_usd=170.0,
        peaker_emission_factor_tco2_per_mwh=0.44,
        carbon_price_usd_per_tco2=45.0,
        load_forecast_sigma=3.5,
        renewable_forecast_sigma=5.0,
        contingency_type="none",
        contingency_step=-1,
        contingency_derate_pct=0.0,
        hint="Normal benchmark mode: prioritize efficient, low-correction dispatch.",
    ),
    "outage": TaskConfig(
        task_id="outage",
        description="Outage benchmark with N-1 generator-or-feeder contingency and delayed thermal recovery.",
        max_steps=30,
        initial_demand_mwh=142.0,
        initial_renewable_mwh=82.0,
        peaker_capacity_mwh=95.0,
        ev_storage_mwh=26.0,
        ev_storage_capacity_mwh=68.0,
        base_price_usd_per_mwh=53.0,
        demand_trend_mwh=1.8,
        renewable_trend_mwh=-0.9,
        demand_volatility=6.0,
        renewable_volatility=8.0,
        shock_step=-1,
        shock_renewable_drop=0.0,
        reserve_margin_ratio=0.16,
        reserve_commitment_threshold_ratio=1.08,
        peaker_ramp_limit_mwh=9.0,
        peaker_activation_delay_steps=1,
        ev_ramp_limit_mwh=7.0,
        peaker_startup_cost_usd=255.0,
        peaker_emission_factor_tco2_per_mwh=0.47,
        carbon_price_usd_per_tco2=70.0,
        load_forecast_sigma=7.5,
        renewable_forecast_sigma=9.0,
        contingency_type="n_minus_one",
        contingency_step=10,
        contingency_derate_pct=0.6,
        hint="Outage mode: N-1 resilience, reserve, and startup realism dominate.",
    ),
    "renewable_collapse": TaskConfig(
        task_id="renewable_collapse",
        description="Renewable collapse benchmark with severe forecast error and large drop event.",
        max_steps=30,
        initial_demand_mwh=146.0,
        initial_renewable_mwh=88.0,
        peaker_capacity_mwh=96.0,
        ev_storage_mwh=24.0,
        ev_storage_capacity_mwh=70.0,
        base_price_usd_per_mwh=56.0,
        demand_trend_mwh=1.9,
        renewable_trend_mwh=-1.2,
        demand_volatility=7.0,
        renewable_volatility=10.0,
        shock_step=8,
        shock_renewable_drop=48.0,
        reserve_margin_ratio=0.18,
        reserve_commitment_threshold_ratio=1.1,
        peaker_ramp_limit_mwh=9.0,
        peaker_activation_delay_steps=1,
        ev_ramp_limit_mwh=6.5,
        peaker_startup_cost_usd=270.0,
        peaker_emission_factor_tco2_per_mwh=0.48,
        carbon_price_usd_per_tco2=75.0,
        load_forecast_sigma=9.0,
        renewable_forecast_sigma=12.0,
        contingency_type="transmission_derate",
        contingency_step=12,
        contingency_derate_pct=0.22,
        hint="Renewable collapse mode: recover from severe uncertainty and scarcity.",
    ),
}


def get_task(task_id: str) -> TaskConfig:
    if task_id not in TASKS:
        raise ValueError(f"Unknown task_id '{task_id}'. Available: {list(TASKS.keys())}")
    return TASKS[task_id]


def list_tasks() -> list[str]:
    return list(TASKS.keys())
