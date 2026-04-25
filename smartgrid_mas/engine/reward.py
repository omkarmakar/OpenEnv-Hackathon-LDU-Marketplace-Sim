from smartgrid_mas.models import MarketReward


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def compute_reward(
    dispatch: dict, clearing_price: float, demand_mwh: float, prior_gap: float, carbon_price_usd_per_tco2: float = 0.0
) -> MarketReward:
    delivered = dispatch["delivered_supply_mwh"]
    unmet = dispatch["unmet_demand_mwh"]
    oversupply = dispatch["oversupply_mwh"]
    correction_count = dispatch["correction_count"]
    reserve_shortfall = max(0.0, dispatch.get("reserve_shortfall_mwh", 0.0))
    reserve_requirement = max(0.0, dispatch.get("reserve_requirement_mwh", demand_mwh * 0.1))
    ramp_violation = max(0.0, dispatch.get("ramp_violation_mwh", 0.0))
    startup_cost_usd = max(0.0, dispatch.get("startup_cost_usd", 0.0))
    emissions_tco2 = max(0.0, dispatch.get("emissions_tco2", 0.0))

    demand_safe = max(demand_mwh, 1e-6)
    current_gap = delivered - demand_mwh

    demand_satisfaction = _clamp(delivered / demand_safe)
    shortfall_ratio = _clamp(unmet / demand_safe)
    oversupply_ratio = _clamp(oversupply / demand_safe)

    renewable_dispatch = dispatch.get("renewable_dispatch_mwh", 0.0)
    peaker_dispatch = dispatch.get("peaker_dispatch_mwh", 0.0)
    ev_discharge = max(0.0, dispatch.get("ev_discharge_mwh", 0.0))
    ev_charge = max(0.0, dispatch.get("ev_charge_mwh", 0.0))

    renewable_utilization = _clamp(renewable_dispatch / max(delivered, 1e-6))
    clean_flex_share = _clamp((renewable_dispatch + ev_discharge) / max(delivered, 1e-6))
    peaker_dependence = _clamp(peaker_dispatch / max(delivered, 1e-6))

    unit_cost = min(abs(clearing_price), 240.0) if clearing_price > 0 else 45.0
    startup_unit_cost = startup_cost_usd / max(delivered, 1e-6)
    emissions_unit_cost = emissions_tco2 * max(0.0, carbon_price_usd_per_tco2) / max(delivered, 1e-6)
    effective_unit_cost = unit_cost + startup_unit_cost + emissions_unit_cost
    # Smooth economic score: near 1 at low prices, gradually lower at expensive clearings.
    cost_efficiency = _clamp(1.0 / (1.0 + ((effective_unit_cost - 52.0) / 34.0) ** 2))

    gap_ratio = _clamp(abs(current_gap) / demand_safe)
    ramp_change = _clamp(abs(current_gap - prior_gap) / max(0.6 * demand_safe, 1.0))
    stability_score = _clamp(1.0 - 0.65 * gap_ratio - 0.35 * ramp_change)
    recovery_progress = _clamp((abs(prior_gap) - abs(current_gap)) / max(0.35 * demand_safe, 1.0), -1.0, 1.0)
    recovery_score = _clamp(0.5 + 0.5 * recovery_progress)

    transmission_loss = max(0.0, dispatch.get("transmission_loss_mwh", 0.0))
    storage_loss = max(0.0, dispatch.get("storage_loss_mwh", 0.0))
    total_losses = transmission_loss + storage_loss
    loss_ratio = _clamp(total_losses / max(delivered + ev_charge, 1e-6))

    curtailed_renewable = max(0.0, dispatch.get("curtailed_renewable_mwh", 0.0))
    curtailment_ratio = _clamp(curtailed_renewable / demand_safe)
    reserve_shortfall_ratio = _clamp(reserve_shortfall / max(reserve_requirement, 1.0))
    reserve_adequacy_score = _clamp(1.0 - reserve_shortfall_ratio)
    ramp_penalty = _clamp(ramp_violation / max(0.25 * demand_safe, 1.0))
    emissions_intensity = emissions_tco2 / max(delivered, 1e-6)
    emissions_penalty = _clamp(emissions_intensity / 0.65)

    infeasibility_penalty = _clamp(correction_count * 0.05 + loss_ratio * 0.50 + reserve_shortfall_ratio * 0.25)
    blackout_penalty = _clamp(shortfall_ratio ** 0.85)
    hard_reliability_penalty = _clamp(
        0.52 * blackout_penalty + 0.22 * reserve_shortfall_ratio + 0.16 * infeasibility_penalty + 0.10 * ramp_penalty
    )
    reliability_stage = _clamp((1.0 - hard_reliability_penalty) * (0.85 + 0.15 * reserve_adequacy_score))
    service_stage = _clamp(
        0.55 * demand_satisfaction + 0.20 * stability_score + 0.15 * recovery_score + 0.10 * (1.0 - oversupply_ratio)
    )
    optimization_stage = _clamp(
        0.46 * cost_efficiency
        + 0.28 * renewable_utilization
        + 0.16 * clean_flex_share
        + 0.10 * (1.0 - emissions_penalty)
    )
    base_score = 0.55 * reliability_stage + 0.30 * service_stage + 0.15 * optimization_stage
    anti_hacking_penalty = _clamp(
        0.45 * curtailment_ratio + 0.25 * peaker_dependence + 0.15 * oversupply_ratio + 0.15 * ramp_penalty
    )
    score = _clamp(base_score * (1.0 - 0.55 * anti_hacking_penalty))

    reason = (
        f"delivered={delivered:.1f} demand={demand_mwh:.1f} unmet={unmet:.1f} "
        f"price={effective_unit_cost:.1f} gap={current_gap:.1f} reserve_shortfall={reserve_shortfall:.2f} "
        f"emissions={emissions_tco2:.3f} corrections={correction_count}"
    )

    return MarketReward(
        score=score,
        reason=reason,
        demand_satisfaction_score=demand_satisfaction,
        cost_efficiency_score=cost_efficiency,
        renewable_utilization_score=renewable_utilization,
        stability_score=stability_score,
        reserve_adequacy_score=reserve_adequacy_score,
        emissions_intensity_tco2_per_mwh=round(emissions_intensity, 5),
        infeasibility_penalty=infeasibility_penalty,
        blackout_penalty=blackout_penalty,
    )
