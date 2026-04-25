from typing import Dict, Tuple


EV_SOC_MIN = 0.2
EV_SOC_MAX = 0.8


def enforce_dispatch(
    market_result: Dict,
    demand_mwh: float,
    renewable_available_mwh: float,
    peaker_capacity_mwh: float,
    ev_storage_mwh: float,
    ev_storage_capacity_mwh: float,
    ev_charge_mwh: float,
    ev_discharge_mwh: float,
    reserve_margin_ratio: float = 0.1,
    reserve_commitment_threshold_ratio: float = 1.0,
    peaker_ramp_limit_mwh: float = 1e9,
    ev_ramp_limit_mwh: float = 1e9,
    previous_peaker_dispatch_mwh: float = 0.0,
    previous_ev_discharge_mwh: float = 0.0,
    previous_peaker_online: bool = False,
    peaker_startup_cost_usd: float = 0.0,
    peaker_emission_factor_tco2_per_mwh: float = 0.0,
    transmission_loss_multiplier: float = 1.0,
    carbon_price_usd_per_tco2: float = 0.0,
    enable_reserve_logic: bool = True,
    enable_ramp_limits: bool = True,
    enable_startup_emissions: bool = True,
) -> Tuple[Dict, float]:
    corrections = []
    requested_ev_charge = ev_charge_mwh

    if ev_charge_mwh > 0 and ev_discharge_mwh > 0:
        ev_discharge_mwh = 0.0
        corrections.append("Simultaneous EV charge and discharge corrected by LDU")

    min_storage = ev_storage_capacity_mwh * EV_SOC_MIN
    max_storage = ev_storage_capacity_mwh * EV_SOC_MAX
    max_charge = max(0.0, max_storage - ev_storage_mwh)
    max_discharge = max(0.0, ev_storage_mwh - min_storage)

    if ev_charge_mwh > max_charge:
        corrections.append("EV charge exceeded SOC 80% limit")
        ev_charge_mwh = max_charge
    if ev_discharge_mwh > max_discharge:
        corrections.append("EV discharge below SOC 20% limit")
        ev_discharge_mwh = max_discharge

    dispatch_from_market = market_result.get("cleared_mwh", 0.0)
    renewable_dispatch = min(renewable_available_mwh, dispatch_from_market)
    residual = max(0.0, dispatch_from_market - renewable_dispatch)
    peaker_dispatch = min(peaker_capacity_mwh, residual)

    ramp_violation = 0.0
    peaker_ramp = max(0.0, peaker_ramp_limit_mwh) if enable_ramp_limits else 1e9
    peaker_delta = peaker_dispatch - previous_peaker_dispatch_mwh
    if abs(peaker_delta) > peaker_ramp:
        peaker_dispatch = previous_peaker_dispatch_mwh + (peaker_ramp if peaker_delta > 0 else -peaker_ramp)
        peaker_dispatch = max(0.0, min(peaker_capacity_mwh, peaker_dispatch))
        ramp_violation += abs(peaker_delta) - peaker_ramp
        corrections.append("Peaker ramp-rate limit applied")

    ev_ramp = max(0.0, ev_ramp_limit_mwh) if enable_ramp_limits else 1e9
    ev_delta = ev_discharge_mwh - previous_ev_discharge_mwh
    if abs(ev_delta) > ev_ramp:
        ev_discharge_mwh = previous_ev_discharge_mwh + (ev_ramp if ev_delta > 0 else -ev_ramp)
        ev_discharge_mwh = max(0.0, min(max_discharge, ev_discharge_mwh))
        ramp_violation += abs(ev_delta) - ev_ramp
        corrections.append("EV discharge ramp-rate limit applied")

    renewable_surplus = max(0.0, renewable_available_mwh - renewable_dispatch)
    if ev_discharge_mwh > 0.0 and ev_charge_mwh > 0.0:
        corrections.append("EV charge request ignored while discharging")
        ev_charge_mwh = 0.0
    if ev_charge_mwh > renewable_surplus:
        if ev_charge_mwh > 0.0:
            corrections.append("EV charging limited to available renewable surplus")
        ev_charge_mwh = min(ev_charge_mwh, renewable_surplus)

    remaining_charge_headroom = max(0.0, max_charge - ev_charge_mwh)
    auto_ev_charge = min(remaining_charge_headroom, max(0.0, renewable_surplus - ev_charge_mwh))
    total_ev_charge = ev_charge_mwh + auto_ev_charge

    if residual > peaker_capacity_mwh:
        corrections.append("Market-cleared supply exceeded physical generation capacity")

    gross_supply = renewable_dispatch + peaker_dispatch + ev_discharge_mwh
    transmission_loss = 0.03 * gross_supply * max(0.5, transmission_loss_multiplier)
    storage_loss = 0.08 * total_ev_charge
    delivered_supply = max(0.0, gross_supply - transmission_loss)
    unmet_demand = max(0.0, demand_mwh - delivered_supply)
    oversupply = max(0.0, delivered_supply - demand_mwh)

    reserve_requirement = max(0.0, demand_mwh * max(0.0, reserve_margin_ratio)) if enable_reserve_logic else 0.0
    spinning_reserve = max(0.0, peaker_capacity_mwh - peaker_dispatch) + max(0.0, max_discharge - ev_discharge_mwh)
    reserve_shortfall = max(0.0, reserve_requirement - spinning_reserve) if enable_reserve_logic else 0.0
    reserve_commitment_active = (
        spinning_reserve < reserve_requirement * max(1.0, reserve_commitment_threshold_ratio)
        if enable_reserve_logic
        else False
    )
    reserve_commitment_penalty = (
        max(0.0, (reserve_requirement * max(1.0, reserve_commitment_threshold_ratio)) - spinning_reserve)
        if enable_reserve_logic
        else 0.0
    )
    if enable_reserve_logic and reserve_shortfall > 0.0:
        corrections.append("Reserve margin shortfall")
    if enable_reserve_logic and reserve_commitment_active:
        corrections.append("Reserve commitment gate activated")

    reserve_ratio = reserve_shortfall / max(reserve_requirement, 1.0)
    frequency_hz = max(49.0, min(50.2, 50.0 - 0.7 * (unmet_demand / max(demand_mwh, 1e-6)) - 0.25 * reserve_ratio))
    branch_loading_ratio = max(
        _safe_ratio(renewable_dispatch, max(1.0, renewable_available_mwh)),
        _safe_ratio(peaker_dispatch, max(1.0, peaker_capacity_mwh)),
        _safe_ratio(ev_discharge_mwh, max(1.0, max_discharge)),
        _safe_ratio(gross_supply, max(1.0, demand_mwh)),
    )
    emergency_dispatch_triggered = frequency_hz < 49.75 or branch_loading_ratio > 1.02 or reserve_commitment_active
    emergency_support_mwh = 0.0
    if emergency_dispatch_triggered and unmet_demand > 0.0:
        peaker_headroom = max(0.0, peaker_capacity_mwh - peaker_dispatch)
        ev_headroom = max(0.0, max_discharge - ev_discharge_mwh)
        emergency_support_mwh = min(unmet_demand, peaker_headroom + ev_headroom)
        extra_peaker = min(peaker_headroom, emergency_support_mwh)
        extra_ev = min(ev_headroom, emergency_support_mwh - extra_peaker)
        peaker_dispatch += extra_peaker
        ev_discharge_mwh += extra_ev
        gross_supply = renewable_dispatch + peaker_dispatch + ev_discharge_mwh
        transmission_loss = 0.03 * gross_supply * max(0.5, transmission_loss_multiplier)
        delivered_supply = max(0.0, gross_supply - transmission_loss)
        unmet_demand = max(0.0, demand_mwh - delivered_supply)
        oversupply = max(0.0, delivered_supply - demand_mwh)
        spinning_reserve = max(0.0, peaker_capacity_mwh - peaker_dispatch) + max(0.0, max_discharge - ev_discharge_mwh)
        reserve_shortfall = max(0.0, reserve_requirement - spinning_reserve)
        reserve_ratio = reserve_shortfall / max(reserve_requirement, 1.0)
        frequency_hz = max(49.0, min(50.2, 50.0 - 0.7 * (unmet_demand / max(demand_mwh, 1e-6)) - 0.25 * reserve_ratio))
        branch_loading_ratio = max(
            _safe_ratio(renewable_dispatch, max(1.0, renewable_available_mwh)),
            _safe_ratio(peaker_dispatch, max(1.0, peaker_capacity_mwh)),
            _safe_ratio(ev_discharge_mwh, max(1.0, max_discharge)),
            _safe_ratio(gross_supply, max(1.0, demand_mwh)),
        )
        corrections.append("Emergency dispatch support activated")

    next_ev_storage = ev_storage_mwh + total_ev_charge - ev_discharge_mwh - storage_loss
    next_ev_storage = max(0.0, min(ev_storage_capacity_mwh, next_ev_storage))
    curtailed_renewable = max(0.0, renewable_surplus - total_ev_charge)
    peaker_online = peaker_dispatch > 0.0
    startup_cost = (
        peaker_startup_cost_usd if (enable_startup_emissions and peaker_online and not previous_peaker_online) else 0.0
    )
    emissions_tco2 = (
        peaker_dispatch * max(0.0, peaker_emission_factor_tco2_per_mwh) if enable_startup_emissions else 0.0
    )
    emissions_cost_usd = emissions_tco2 * max(0.0, carbon_price_usd_per_tco2)
    stability_risk_index = _clamp01(
        0.35 * (unmet_demand / max(demand_mwh, 1.0))
        + 0.25 * (reserve_shortfall / max(reserve_requirement, 1.0))
        + 0.20 * max(0.0, 49.95 - frequency_hz)
        + 0.20 * max(0.0, branch_loading_ratio - 0.9)
    )

    dispatch = {
        "renewable_dispatch_mwh": round(renewable_dispatch, 3),
        "peaker_dispatch_mwh": round(peaker_dispatch, 3),
        "ev_charge_mwh": round(total_ev_charge, 3),
        "requested_ev_charge_mwh": round(requested_ev_charge, 3),
        "scheduled_ev_charge_mwh": round(ev_charge_mwh, 3),
        "auto_ev_charge_mwh": round(auto_ev_charge, 3),
        "ev_discharge_mwh": round(ev_discharge_mwh, 3),
        "transmission_loss_mwh": round(transmission_loss, 3),
        "storage_loss_mwh": round(storage_loss, 3),
        "renewable_surplus_mwh": round(renewable_surplus, 3),
        "curtailed_renewable_mwh": round(curtailed_renewable, 3),
        "reserve_requirement_mwh": round(reserve_requirement, 3),
        "spinning_reserve_mwh": round(spinning_reserve, 3),
        "reserve_shortfall_mwh": round(reserve_shortfall, 3),
        "reserve_commitment_active": reserve_commitment_active,
        "reserve_commitment_penalty_mwh": round(reserve_commitment_penalty, 3),
        "ramp_limit_mwh": round(peaker_ramp, 3),
        "ramp_violation_mwh": round(ramp_violation, 3),
        "startup_cost_usd": round(startup_cost, 3),
        "emissions_tco2": round(emissions_tco2, 5),
        "emissions_cost_usd": round(emissions_cost_usd, 3),
        "frequency_hz": round(frequency_hz, 4),
        "line_loading_ratio": round(branch_loading_ratio, 4),
        "branch_loading_ratio": round(branch_loading_ratio, 4),
        "emergency_dispatch_triggered": emergency_dispatch_triggered,
        "emergency_support_mwh": round(emergency_support_mwh, 3),
        "stability_risk_index": round(stability_risk_index, 4),
        "peaker_online": peaker_online,
        "delivered_supply_mwh": round(delivered_supply, 3),
        "unmet_demand_mwh": round(unmet_demand, 3),
        "oversupply_mwh": round(oversupply, 3),
        "next_ev_storage_mwh": round(next_ev_storage, 3),
        "corrections": corrections,
        "correction_count": len(corrections),
    }
    return dispatch, next_ev_storage


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator <= 0:
        return 0.0
    return max(0.0, min(1.5, numerator / denominator))


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))
