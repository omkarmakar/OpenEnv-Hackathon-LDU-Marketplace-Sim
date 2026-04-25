from typing import Dict, Tuple


# EV battery SOC limits to prevent battery depletion
EV_SOC_MIN = 0.2  # 20% minimum
EV_SOC_MAX = 0.8  # 80% maximum


def enforce_dispatch(
    market_result: Dict,
    demand_mwh: float,
    renewable_available_mwh: float,
    peaker_capacity_mwh: float,
    ev_storage_mwh: float,
    ev_storage_capacity_mwh: float,
    ev_charge_mwh: float,
    ev_discharge_mwh: float,
) -> Tuple[Dict, float]:
    corrections = []

    if ev_charge_mwh > 0 and ev_discharge_mwh > 0:
        ev_discharge_mwh = 0.0
        corrections.append("Simultaneous EV charge and discharge corrected by LDU")

    # SOC limits: maintain 20%-80% range
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

    if residual > peaker_capacity_mwh:
        corrections.append("Market-cleared supply exceeded physical generation capacity")

    gross_supply = renewable_dispatch + peaker_dispatch + ev_discharge_mwh

    transmission_loss = 0.03 * gross_supply
    storage_loss = 0.08 * ev_charge_mwh

    delivered_supply = max(0.0, gross_supply - transmission_loss)
    unmet_demand = max(0.0, demand_mwh - delivered_supply)
    oversupply = max(0.0, delivered_supply - demand_mwh)

    next_ev_storage = ev_storage_mwh + ev_charge_mwh - ev_discharge_mwh - storage_loss
    next_ev_storage = max(0.0, min(ev_storage_capacity_mwh, next_ev_storage))

    dispatch = {
        "renewable_dispatch_mwh": round(renewable_dispatch, 3),
        "peaker_dispatch_mwh": round(peaker_dispatch, 3),
        "ev_charge_mwh": round(ev_charge_mwh, 3),
        "ev_discharge_mwh": round(ev_discharge_mwh, 3),
        "transmission_loss_mwh": round(transmission_loss, 3),
        "storage_loss_mwh": round(storage_loss, 3),
        "delivered_supply_mwh": round(delivered_supply, 3),
        "unmet_demand_mwh": round(unmet_demand, 3),
        "oversupply_mwh": round(oversupply, 3),
        "next_ev_storage_mwh": round(next_ev_storage, 3),
        "corrections": corrections,
        "correction_count": len(corrections),
    }

    return dispatch, next_ev_storage
