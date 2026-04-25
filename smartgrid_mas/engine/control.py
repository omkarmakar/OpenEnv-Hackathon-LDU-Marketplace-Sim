from __future__ import annotations

from dataclasses import dataclass

from smartgrid_mas.models import DispatchAction, MarketObservation


@dataclass
class ReliabilityDispatchControlAgent:
    """Reduced-order dispatcher that turns market state into corrective dispatch."""

    personality: str = "balanced"

    def act(self, obs: MarketObservation, cleared_mwh: float) -> DispatchAction:
        forecast_gap = max(0.0, obs.forecast_demand_mwh - obs.forecast_renewable_mwh)
        actual_gap = max(0.0, obs.demand_mwh - obs.renewable_availability_mwh)
        scarcity = max(0.0, obs.scarcity_index)
        reserve_pressure = min(1.0, max(0.0, scarcity - 0.15))

        if self.personality == "risk_averse":
            reserve_scale = 0.62
            peaker_scale = 1.08
            storage_scale = 0.82
            redispatch_scale = 0.38
        elif self.personality == "opportunistic":
            reserve_scale = 0.34
            peaker_scale = 0.72
            storage_scale = 0.52
            redispatch_scale = 0.22
        else:
            reserve_scale = 0.48
            peaker_scale = 0.92
            storage_scale = 0.68
            redispatch_scale = 0.30

        reserve_activation_mwh = max(0.0, forecast_gap * reserve_scale * (0.75 + 0.25 * reserve_pressure))
        peaker_adjustment_mwh = max(0.0, actual_gap * peaker_scale * (0.85 + 0.15 * reserve_pressure))

        storage_dispatch_mwh = 0.0
        if scarcity > 0.25:
            storage_dispatch_mwh = min(obs.ev_storage_mwh, actual_gap * storage_scale)
        elif obs.renewable_availability_mwh > obs.demand_mwh * 0.95:
            storage_dispatch_mwh = -min(
                max(0.0, obs.ev_storage_capacity_mwh - obs.ev_storage_mwh),
                (obs.renewable_availability_mwh - obs.demand_mwh) * 0.25,
            )

        corrective_redispatch_mwh = max(0.0, (cleared_mwh - obs.demand_mwh + actual_gap) * redispatch_scale)
        if scarcity > 0.40:
            corrective_redispatch_mwh += actual_gap * 0.20
        elif scarcity < 0.12:
            corrective_redispatch_mwh -= min(corrective_redispatch_mwh, obs.demand_mwh * 0.03)

        return DispatchAction(
            reserve_activation_mwh=round(reserve_activation_mwh, 3),
            peaker_adjustment_mwh=round(peaker_adjustment_mwh, 3),
            storage_dispatch_mwh=round(storage_dispatch_mwh, 3),
            corrective_redispatch_mwh=round(corrective_redispatch_mwh, 3),
        )
