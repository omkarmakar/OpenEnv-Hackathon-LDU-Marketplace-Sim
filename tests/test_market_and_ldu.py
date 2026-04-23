from smartgrid_mas.engine.ldu import enforce_dispatch
from smartgrid_mas.engine.market import clear_market
from smartgrid_mas.models import AgentBid


def test_market_clearing_and_leader_adjustment():
    bids = [
        AgentBid(agent_id="renewable_1", role="renewable_prosumer", bid_type="supply", quantity_mwh=40, price_usd_per_mwh=10),
        AgentBid(agent_id="peaker_1", role="peaker_plant", bid_type="supply", quantity_mwh=30, price_usd_per_mwh=35),
        AgentBid(agent_id="industrial_1", role="industrial_load", bid_type="demand", quantity_mwh=50, price_usd_per_mwh=120),
    ]
    out = clear_market(bids, leader_price_signal=50)

    assert out["cleared_mwh"] > 0
    assert out["leader_adjusted_bids"] >= 1
    assert out["total_supply_offered"] == 70
    assert out["total_demand_bid"] == 50


def test_ldu_correction_invariants():
    market_result = {"cleared_mwh": 120}
    dispatch, next_storage = enforce_dispatch(
        market_result=market_result,
        demand_mwh=100,
        renewable_available_mwh=45,
        peaker_capacity_mwh=40,
        ev_storage_mwh=5,
        ev_storage_capacity_mwh=20,
        ev_charge_mwh=8,
        ev_discharge_mwh=10,
    )

    assert dispatch["correction_count"] >= 1
    assert 0 <= next_storage <= 20
    assert dispatch["delivered_supply_mwh"] >= 0
    assert dispatch["unmet_demand_mwh"] >= 0
    assert dispatch["oversupply_mwh"] >= 0
