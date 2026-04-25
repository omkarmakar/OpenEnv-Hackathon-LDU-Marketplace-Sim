from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


AgentRole = Literal[
    "renewable_prosumer",
    "ev_aggregator",
    "peaker_plant",
    "industrial_load",
]
BidType = Literal["supply", "demand"]


class AgentBid(BaseModel):
    agent_id: str = Field(..., description="Unique agent id")
    role: AgentRole = Field(..., description="Agent role")
    bid_type: BidType = Field(..., description="Supply or demand bid")
    quantity_mwh: float = Field(..., ge=0.0, description="Bid quantity in MWh")
    price_usd_per_mwh: float = Field(..., ge=0.0, description="Bid price")


class JointAction(BaseModel):
    bids: List[AgentBid] = Field(default_factory=list, description="Bids from all agents")
    ev_charge_mwh: float = Field(0.0, ge=0.0, description="EV fleet charge command")
    ev_discharge_mwh: float = Field(0.0, ge=0.0, description="EV fleet discharge command")


class DispatchAction(BaseModel):
    reserve_activation_mwh: float = Field(0.0, ge=0.0, description="Reserve activation target")
    peaker_adjustment_mwh: float = Field(0.0, description="Peaker redispatch adjustment")
    storage_dispatch_mwh: float = Field(0.0, description="Signed storage dispatch adjustment")
    corrective_redispatch_mwh: float = Field(0.0, description="Signed corrective redispatch adjustment")


class MarketObservation(BaseModel):
    step: int
    steps_taken: int
    max_steps: int
    demand_mwh: float
    renewable_availability_mwh: float
    peaker_capacity_mwh: float
    ev_storage_mwh: float
    ev_storage_capacity_mwh: float
    last_clearing_price: float
    leader_price_signal: float
    scarcity_index: float
    shock_active: bool
    forecast_demand_mwh: float = 0.0
    forecast_renewable_mwh: float = 0.0
    load_forecast_error_mwh: float = 0.0
    renewable_forecast_error_mwh: float = 0.0
    contingency_active: bool = False
    contingency_type: str = "none"
    operator_override_enabled: bool = False
    public_signal: str
    schema_info: str
    hint: Optional[str] = None
    error_message: Optional[str] = None


class MarketReward(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0)
    reason: str
    demand_satisfaction_score: float
    cost_efficiency_score: float
    renewable_utilization_score: float
    stability_score: float
    reserve_adequacy_score: float = 0.0
    emissions_intensity_tco2_per_mwh: float = 0.0
    infeasibility_penalty: float
    blackout_penalty: float


class ResetRequest(BaseModel):
    task_id: str = "default"
    seed: Optional[int] = None


class ResetResponse(BaseModel):
    session_id: str
    task_id: str
    task_description: str
    schema_info: str
    steps_taken: int
    observation: MarketObservation


class StepRequest(BaseModel):
    action: JointAction
    dispatch_action: Optional[DispatchAction] = None


class StepResponse(BaseModel):
    observation: MarketObservation
    reward: MarketReward
    done: bool
    truncated: bool
    info: Dict


class StateResponse(BaseModel):
    current_task_id: str
    steps_taken: int
    episode_done: bool
    observation: Optional[MarketObservation] = None


class EpisodeSummary(BaseModel):
    average_reward: float
    total_demand_met: float
    total_cost: float
    infeasible_actions: int
    corrections: int
    shock_response_score: float
