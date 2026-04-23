from typing import Dict, List

from smartgrid_mas.models import AgentBid


def _apply_leader_signal(bids: List[AgentBid], leader_price_signal: float) -> Dict:
    adjusted = []
    adjusted_count = 0

    for bid in bids:
        price = float(bid.price_usd_per_mwh)
        if bid.bid_type == "supply":
            floor = 0.8 * leader_price_signal
            if bid.role == "peaker_plant":
                floor = 0.95 * leader_price_signal
            new_price = max(price, floor)
        else:
            cap = 1.8 * leader_price_signal
            floor = 0.9 * leader_price_signal
            new_price = min(max(price, floor), cap)

        if abs(new_price - price) > 1e-9:
            adjusted_count += 1

        adjusted.append(
            {
                "agent_id": bid.agent_id,
                "role": bid.role,
                "bid_type": bid.bid_type,
                "quantity_mwh": float(bid.quantity_mwh),
                "price_usd_per_mwh": float(new_price),
                "raw_price_usd_per_mwh": float(price),
            }
        )

    return {
        "bids": adjusted,
        "adjusted_count": adjusted_count,
    }


def clear_market(bids: List[AgentBid], leader_price_signal: float) -> Dict:
    leader_adjusted = _apply_leader_signal(bids, leader_price_signal)
    priced_bids = leader_adjusted["bids"]

    supply = [
        b for b in priced_bids if b["bid_type"] == "supply" and b["quantity_mwh"] > 0
    ]
    demand = [
        b for b in priced_bids if b["bid_type"] == "demand" and b["quantity_mwh"] > 0
    ]

    supply_sorted = sorted(supply, key=lambda x: x["price_usd_per_mwh"])
    demand_sorted = sorted(demand, key=lambda x: x["price_usd_per_mwh"], reverse=True)

    i = 0
    j = 0
    cleared_qty = 0.0
    matched = []
    clearing_price = 0.0

    while i < len(supply_sorted) and j < len(demand_sorted):
        s = supply_sorted[i]
        d = demand_sorted[j]
        if s["price_usd_per_mwh"] > d["price_usd_per_mwh"]:
            break

        qty = min(s["quantity_mwh"], d["quantity_mwh"])
        if qty <= 0:
            break

        cleared_qty += qty
        clearing_price = (s["price_usd_per_mwh"] + d["price_usd_per_mwh"]) / 2.0
        matched.append(
            {
                "supply_agent": s["agent_id"],
                "demand_agent": d["agent_id"],
                "quantity_mwh": round(qty, 3),
                "price_usd_per_mwh": round(clearing_price, 3),
            }
        )

        s["quantity_mwh"] -= qty
        d["quantity_mwh"] -= qty
        if s["quantity_mwh"] <= 1e-6:
            i += 1
        if d["quantity_mwh"] <= 1e-6:
            j += 1

    total_supply_offered = sum(float(b.quantity_mwh) for b in bids if b.bid_type == "supply")
    total_demand_bid = sum(float(b.quantity_mwh) for b in bids if b.bid_type == "demand")

    return {
        "cleared_mwh": round(cleared_qty, 3),
        "clearing_price": round(clearing_price, 3),
        "total_supply_offered": round(total_supply_offered, 3),
        "total_demand_bid": round(total_demand_bid, 3),
        "leader_price_signal": round(leader_price_signal, 3),
        "leader_adjusted_bids": leader_adjusted["adjusted_count"],
        "post_signal_book": priced_bids,
        "matches": matched,
    }
