from smartgrid_mas.models import MarketReward


def compute_reward(dispatch: dict, clearing_price: float, demand_mwh: float, prior_gap: float) -> MarketReward:
    delivered = dispatch["delivered_supply_mwh"]
    unmet = dispatch["unmet_demand_mwh"]
    oversupply = dispatch["oversupply_mwh"]
    correction_count = dispatch["correction_count"]

    demand_satisfaction = min(1.0, delivered / max(demand_mwh, 1e-6))

    unit_cost = clearing_price if clearing_price > 0 else 45.0
    total_cost = delivered * unit_cost
    cost_efficiency = max(0.0, 1.0 - total_cost / 12000.0)

    renewable_utilization = min(1.0, dispatch["renewable_dispatch_mwh"] / max(delivered, 1e-6))

    current_gap = delivered - demand_mwh
    stability_delta = abs(current_gap - prior_gap)
    stability_score = max(0.0, 1.0 - stability_delta / 80.0)

    infeasibility_penalty = min(1.0, correction_count * 0.15 + dispatch["storage_loss_mwh"] * 0.01)
    blackout_penalty = min(1.0, unmet / max(demand_mwh, 1e-6))

    raw = (
        0.34 * demand_satisfaction
        + 0.23 * cost_efficiency
        + 0.18 * renewable_utilization
        + 0.15 * stability_score
        - 0.2 * infeasibility_penalty
        - 0.2 * blackout_penalty
        - 0.03 * min(1.0, oversupply / max(demand_mwh, 1e-6))
    )
    score = max(0.0, min(1.0, raw))

    reason = (
        f"delivered={delivered:.1f} demand={demand_mwh:.1f} unmet={unmet:.1f} "
        f"price={unit_cost:.1f} corrections={correction_count}"
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
