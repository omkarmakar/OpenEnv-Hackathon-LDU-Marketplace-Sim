import random

from smartgrid_mas.models import AgentBid, JointAction, MarketObservation


def random_joint_action(obs: MarketObservation, rng: random.Random) -> JointAction:
    bids = [
        AgentBid(
            agent_id="renewable_1",
            role="renewable_prosumer",
            bid_type="supply",
            quantity_mwh=max(0.0, rng.uniform(10.0, obs.renewable_availability_mwh)),
            price_usd_per_mwh=rng.uniform(10.0, 40.0),
        ),
        AgentBid(
            agent_id="peaker_1",
            role="peaker_plant",
            bid_type="supply",
            quantity_mwh=rng.uniform(5.0, obs.peaker_capacity_mwh),
            price_usd_per_mwh=rng.uniform(35.0, 80.0),
        ),
        AgentBid(
            agent_id="industrial_1",
            role="industrial_load",
            bid_type="demand",
            quantity_mwh=rng.uniform(0.6 * obs.demand_mwh, 1.1 * obs.demand_mwh),
            price_usd_per_mwh=rng.uniform(30.0, 95.0),
        ),
    ]
    return JointAction(
        bids=bids,
        ev_charge_mwh=rng.uniform(0.0, 8.0),
        ev_discharge_mwh=rng.uniform(0.0, 8.0),
    )


def heuristic_joint_action(obs: MarketObservation, personality: str = "balanced") -> JointAction:
    demand = obs.demand_mwh
    renewable_offer = min(obs.renewable_availability_mwh, demand * 0.55)
    peaker_offer = min(obs.peaker_capacity_mwh, max(0.0, demand - renewable_offer))

    # EV SOC limits: 20%-80%
    min_soc = obs.ev_storage_capacity_mwh * 0.2
    max_soc = obs.ev_storage_capacity_mwh * 0.8
    
    chargeable = max(0, max_soc - obs.ev_storage_mwh)
    dischargeable = max(0, obs.ev_storage_mwh - min_soc)
    
    if personality == "greedy":
        industrial_price = 95.0
        peaker_price = max(62.0, obs.leader_price_signal * 1.08)
        charge = min(chargeable, 1.0)
        discharge = min(dischargeable, 5.0 if obs.scarcity_index > 0.2 else 2.0)
    elif personality == "risk_averse":
        industrial_price = 90.0
        peaker_price = max(54.0, obs.leader_price_signal * 0.98)
        charge = min(chargeable, 5.0 if obs.renewable_availability_mwh > demand else 1.0)
        discharge = min(dischargeable, 2.0 if obs.scarcity_index > 0.35 else 0.0)
    else:
        industrial_price = 85.0
        peaker_price = max(58.0, obs.leader_price_signal * 1.02)
        charge = min(chargeable, 3.0 if obs.renewable_availability_mwh > demand else 0.0)
        discharge = min(dischargeable, 4.0 if obs.renewable_availability_mwh < 0.8 * demand else 0.0)

    bids = [
        AgentBid(
            agent_id="renewable_1",
            role="renewable_prosumer",
            bid_type="supply",
            quantity_mwh=max(0.0, renewable_offer),
            price_usd_per_mwh=20.0,
        ),
        AgentBid(
            agent_id="peaker_1",
            role="peaker_plant",
            bid_type="supply",
            quantity_mwh=max(0.0, peaker_offer),
            price_usd_per_mwh=peaker_price,
        ),
        AgentBid(
            agent_id="industrial_1",
            role="industrial_load",
            bid_type="demand",
            quantity_mwh=demand,
            price_usd_per_mwh=industrial_price,
        ),
    ]

    return JointAction(bids=bids, ev_charge_mwh=charge, ev_discharge_mwh=discharge)


def adaptive_stackelberg_action(obs: MarketObservation, personality: str = "balanced") -> JointAction:
    demand = obs.demand_mwh
    scarcity = max(0.0, obs.scarcity_index)
    leader = max(1.0, obs.leader_price_signal)

    renewable_offer = min(obs.renewable_availability_mwh, demand * (0.58 + 0.20 * (1.0 - scarcity)))
    peaker_need = max(0.0, demand - renewable_offer)
    peaker_offer = min(obs.peaker_capacity_mwh, peaker_need * (1.0 + 0.18 * scarcity))

    if personality == "opportunistic":
        peaker_markup = 1.16
        load_budget = 1.42 + 0.28 * scarcity
        charge_bias = 0.5
    elif personality == "risk_averse":
        peaker_markup = 1.03
        load_budget = 1.30 + 0.18 * scarcity
        charge_bias = 1.25
    else:
        peaker_markup = 1.08 + 0.08 * scarcity
        load_budget = 1.34 + 0.22 * scarcity
        charge_bias = 1.0

    bids = [
        AgentBid(
            agent_id="renewable_1",
            role="renewable_prosumer",
            bid_type="supply",
            quantity_mwh=max(0.0, renewable_offer),
            price_usd_per_mwh=max(12.0, leader * 0.78),
        ),
        AgentBid(
            agent_id="peaker_1",
            role="peaker_plant",
            bid_type="supply",
            quantity_mwh=max(0.0, peaker_offer),
            price_usd_per_mwh=max(40.0, leader * peaker_markup),
        ),
        AgentBid(
            agent_id="industrial_1",
            role="industrial_load",
            bid_type="demand",
            quantity_mwh=demand,
            price_usd_per_mwh=leader * min(1.75, load_budget),
        ),
    ]

    # EV SOC limits: 20%-80%
    min_soc = obs.ev_storage_capacity_mwh * 0.2
    max_soc = obs.ev_storage_capacity_mwh * 0.8
    
    # Current SOC %
    current_soc_pct = obs.ev_storage_mwh / obs.ev_storage_capacity_mwh
    
    # Available headroom
    current_chargeable = max(0, max_soc - obs.ev_storage_mwh)
    current_dischargeable = max(0, obs.ev_storage_mwh - min_soc)

    # EV strategy: hold mid SOC, charge from likely surplus, discharge in scarcity windows.
    if current_soc_pct <= 0.35:
        charge = min(current_chargeable, 5.0)
        discharge = 0.0
    elif scarcity > 0.45 and current_soc_pct > 0.25:
        discharge = min(current_dischargeable, 2.5 + 5.5 * scarcity)
        charge = 0.0
    elif obs.renewable_availability_mwh > demand * 0.9 and current_soc_pct < 0.75:
        charge = min(current_chargeable, 2.5 * charge_bias + 2.0)
        discharge = 0.0
    elif scarcity < 0.15 and current_soc_pct < 0.55:
        charge = min(current_chargeable, 1.5 * charge_bias + 1.0)
        discharge = 0.0
    elif scarcity > 0.25 and current_soc_pct > 0.55:
        discharge = min(current_dischargeable, 2.0 + 3.5 * scarcity)
        charge = 0.0
    else:
        charge = 0.0
        discharge = 0.0

    if current_soc_pct >= 0.79:
        charge = 0.0
    if current_soc_pct <= 0.21:
        discharge = 0.0

    return JointAction(bids=bids, ev_charge_mwh=max(0, charge), ev_discharge_mwh=max(0, discharge))
