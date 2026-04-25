from smartgrid_mas.models import MarketReward


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def compute_reward(dispatch: dict, clearing_price: float, demand_mwh: float, prior_gap: float) -> MarketReward:
    delivered = dispatch["delivered_supply_mwh"]
    unmet = dispatch["unmet_demand_mwh"]
    oversupply = dispatch["oversupply_mwh"]
    correction_count = dispatch["correction_count"]

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
    # Smooth economic score: near 1 at low prices, gradually lower at expensive clearings.
    cost_efficiency = _clamp(1.0 / (1.0 + ((unit_cost - 48.0) / 30.0) ** 2))

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

    infeasibility_penalty = _clamp(correction_count * 0.06 + loss_ratio * 0.55)
    blackout_penalty = _clamp(shortfall_ratio ** 0.85)

    positive = (
        0.34 * demand_satisfaction
        + 0.15 * cost_efficiency
        + 0.14 * renewable_utilization
        + 0.10 * clean_flex_share
        + 0.12 * stability_score
        + 0.08 * (1.0 - loss_ratio)
        + 0.07 * recovery_score
    )
    penalties = (
        0.45 * blackout_penalty
        + 0.28 * infeasibility_penalty
        + 0.17 * oversupply_ratio
        + 0.10 * curtailment_ratio
    )
    score = _clamp(positive * (1.0 - 0.62 * penalties) - 0.05 * peaker_dependence)

    reason = (
        f"delivered={delivered:.1f} demand={demand_mwh:.1f} unmet={unmet:.1f} "
        f"price={unit_cost:.1f} gap={current_gap:.1f} losses={total_losses:.2f} corrections={correction_count}"
    )

    return MarketReward(
        score=score,
        reason=reason,
        demand_satisfaction_score=demand_satisfaction,
        cost_efficiency_score=cost_efficiency,
        renewable_utilization_score=renewable_utilization,
        stability_score=stability_score,
        infeasibility_penalty=infeasibility_penalty,
        blackout_penalty=blackout_penalty,
    )
