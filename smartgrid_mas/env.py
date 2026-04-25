import random
import uuid
from dataclasses import dataclass, field
from typing import Dict, Optional

from smartgrid_mas.engine.policies import (
    adaptive_stackelberg_action,
    heuristic_joint_action,
    random_joint_action,
)
from smartgrid_mas.engine.control import ReliabilityDispatchControlAgent
from smartgrid_mas.engine.dynamics import evolve_grid
from smartgrid_mas.engine.ldu import enforce_dispatch
from smartgrid_mas.engine.market import clear_market
from smartgrid_mas.engine.reward import compute_reward
from smartgrid_mas.models import (
    DispatchAction,
    JointAction,
    MarketObservation,
    MarketReward,
    ResetResponse,
    StateResponse,
    StepResponse,
)
from smartgrid_mas.tasks import TaskConfig, get_task, list_tasks


SCHEMA_INFO = (
    "Provide a JointAction with supply and demand bids from multiple agents plus EV charge/discharge "
    "commands. Market clears bids first, then the Reliability Dispatch Control Agent proposes corrective dispatch, "
    "and the Physics-Constrained Safety Shield enforces physical feasibility and logs corrections."
)


@dataclass
class Session:
    task: TaskConfig
    rng: random.Random
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    step: int = 0
    done: bool = False
    demand_mwh: float = 0.0
    renewable_mwh: float = 0.0
    peaker_capacity_mwh: float = 0.0
    ev_storage_mwh: float = 0.0
    ev_storage_capacity_mwh: float = 0.0
    base_price: float = 0.0
    last_clearing_price: float = 0.0
    prior_gap: float = 0.0
    correction_count: int = 0
    infeasible_actions: int = 0
    total_demand_met: float = 0.0
    total_cost: float = 0.0
    reward_history: list = field(default_factory=list)
    event_log: list = field(default_factory=list)
    shock_seen: bool = False
    contingency_seen: bool = False
    contingency_type: str = "none"
    operator_override_enabled: bool = False
    forecast_demand_mwh: float = 0.0
    forecast_renewable_mwh: float = 0.0
    load_forecast_error_mwh: float = 0.0
    renewable_forecast_error_mwh: float = 0.0
    previous_peaker_dispatch_mwh: float = 0.0
    previous_ev_discharge_mwh: float = 0.0
    peaker_online: bool = False
    contingency_peaker_multiplier: float = 1.0
    contingency_loss_multiplier: float = 1.0
    total_emissions_tco2: float = 0.0
    blackout_steps: int = 0
    reserve_commitment_events: int = 0
    emergency_dispatch_events: int = 0
    stability_events: int = 0
    peaker_activation_timer: int = 0
    personalities: Dict[str, str] = field(default_factory=dict)

    def to_observation(self, hint: Optional[str] = None, error_message: Optional[str] = None) -> MarketObservation:
        public_signal = (
            "Shock regime active; renewable volatility is elevated"
            if self.shock_seen
            else "Normal regime; optimize demand satisfaction with low infeasibility"
        )
        return MarketObservation(
            step=self.step,
            steps_taken=self.step,
            max_steps=self.task.max_steps,
            demand_mwh=round(self.demand_mwh, 3),
            renewable_availability_mwh=round(self.renewable_mwh, 3),
            peaker_capacity_mwh=round(self.peaker_capacity_mwh, 3),
            ev_storage_mwh=round(self.ev_storage_mwh, 3),
            ev_storage_capacity_mwh=round(self.ev_storage_capacity_mwh, 3),
            last_clearing_price=round(self.last_clearing_price, 3),
            leader_price_signal=round(self.base_price, 3),
            scarcity_index=round(max(0.0, (self.demand_mwh - self.renewable_mwh) / max(self.demand_mwh, 1e-6)), 4),
            shock_active=self.shock_seen,
            forecast_demand_mwh=round(self.forecast_demand_mwh, 3),
            forecast_renewable_mwh=round(self.forecast_renewable_mwh, 3),
            load_forecast_error_mwh=round(self.load_forecast_error_mwh, 3),
            renewable_forecast_error_mwh=round(self.renewable_forecast_error_mwh, 3),
            contingency_active=self.contingency_seen,
            contingency_type=self.contingency_type,
            operator_override_enabled=self.operator_override_enabled,
            public_signal=public_signal,
            schema_info=SCHEMA_INFO,
            hint=hint,
            error_message=error_message,
        )


class SmartGridMarketEnv:
    def __init__(self):
        self._sessions: Dict[str, Session] = {}
        self._latest_session_id: Optional[str] = None

    def reset(self, task_id: str = "default", seed: Optional[int] = None) -> ResetResponse:
        task = get_task(task_id)
        rng = random.Random(seed)
        session = Session(
            task=task,
            rng=rng,
            demand_mwh=task.initial_demand_mwh,
            renewable_mwh=task.initial_renewable_mwh,
            peaker_capacity_mwh=task.peaker_capacity_mwh,
            ev_storage_mwh=task.ev_storage_mwh,
            ev_storage_capacity_mwh=task.ev_storage_capacity_mwh,
            base_price=task.base_price_usd_per_mwh,
            last_clearing_price=task.base_price_usd_per_mwh,
            personalities={
                "renewable_1": rng.choice(["opportunistic", "balanced"]),
                "peaker_1": rng.choice(["greedy", "balanced", "risk_averse"]),
                "industrial_1": rng.choice(["risk_averse", "balanced"]),
                "ev_1": rng.choice(["balanced", "risk_averse"]),
            },
            forecast_demand_mwh=task.initial_demand_mwh,
            forecast_renewable_mwh=task.initial_renewable_mwh,
        )
        self._sessions[session.session_id] = session
        self._latest_session_id = session.session_id

        return ResetResponse(
            session_id=session.session_id,
            task_id=task.task_id,
            task_description=task.description,
            schema_info=SCHEMA_INFO,
            steps_taken=0,
            observation=session.to_observation(hint=task.hint),
        )

    def step(
        self,
        action: JointAction,
        session_id: Optional[str] = None,
        dispatch_action: Optional[DispatchAction] = None,
    ) -> StepResponse:
        session = self._get_session(session_id)
        if session.done:
            return StepResponse(
                observation=session.to_observation(error_message="Episode finished. Call reset."),
                reward=compute_reward(
                    dispatch={
                        "delivered_supply_mwh": 0.0,
                        "unmet_demand_mwh": 0.0,
                        "oversupply_mwh": 0.0,
                        "correction_count": 0,
                        "storage_loss_mwh": 0.0,
                        "renewable_dispatch_mwh": 0.0,
                    },
                    clearing_price=session.last_clearing_price,
                    demand_mwh=max(1.0, session.demand_mwh),
                    prior_gap=0.0,
                ),
                done=True,
                truncated=False,
                info={"error": "episode_done"},
            )

        applied_action = action
        if session.operator_override_enabled:
            applied_action = heuristic_joint_action(session.to_observation(), personality="risk_averse")
        market = clear_market(applied_action.bids, leader_price_signal=session.base_price)
        dispatch_action = dispatch_action or self._resolve_dispatch_action(session, market, session.to_observation())
        effective_peaker_capacity = session.peaker_capacity_mwh * session.contingency_peaker_multiplier
        effective_peaker_capacity += dispatch_action.reserve_activation_mwh + dispatch_action.peaker_adjustment_mwh
        applied_ev_charge = applied_action.ev_charge_mwh
        applied_ev_discharge = applied_action.ev_discharge_mwh
        if dispatch_action.storage_dispatch_mwh >= 0.0:
            applied_ev_discharge += dispatch_action.storage_dispatch_mwh
        else:
            applied_ev_charge += abs(dispatch_action.storage_dispatch_mwh)
        expected_residual = max(0.0, market.get("cleared_mwh", 0.0) - session.renewable_mwh)
        if (
            session.task.peaker_activation_delay_steps > 0
            and not session.peaker_online
            and session.peaker_activation_timer == 0
            and expected_residual > 0.0
        ):
            session.peaker_activation_timer = session.task.peaker_activation_delay_steps
            session.event_log.append(
                {
                    "step": session.step,
                    "type": "peaker_startup_delay",
                    "delay_steps": session.task.peaker_activation_delay_steps,
                }
            )
        dispatch_override_active = (
            dispatch_action.reserve_activation_mwh > 0.0
            or dispatch_action.peaker_adjustment_mwh > 0.0
            or dispatch_action.storage_dispatch_mwh > 0.0
            or dispatch_action.corrective_redispatch_mwh > 0.0
        )
        if dispatch_override_active and session.peaker_activation_timer > 0:
            session.peaker_activation_timer = 0
        if session.peaker_activation_timer > 0:
            effective_peaker_capacity = 0.0
            session.peaker_activation_timer -= 1

        adjusted_market = dict(market)
        dispatch_target_shift = dispatch_action.corrective_redispatch_mwh
        adjusted_market["cleared_mwh"] = max(0.0, adjusted_market.get("cleared_mwh", 0.0) + dispatch_target_shift)
        adjusted_market["dispatcher_action"] = dispatch_action.model_dump()

        dispatch, next_storage = enforce_dispatch(
            market_result=adjusted_market,
            demand_mwh=session.demand_mwh,
            renewable_available_mwh=session.renewable_mwh,
            peaker_capacity_mwh=effective_peaker_capacity,
            ev_storage_mwh=session.ev_storage_mwh,
            ev_storage_capacity_mwh=session.ev_storage_capacity_mwh,
            ev_charge_mwh=applied_ev_charge,
            ev_discharge_mwh=applied_ev_discharge,
            reserve_margin_ratio=session.task.reserve_margin_ratio,
            reserve_commitment_threshold_ratio=session.task.reserve_commitment_threshold_ratio,
            peaker_ramp_limit_mwh=session.task.peaker_ramp_limit_mwh,
            ev_ramp_limit_mwh=session.task.ev_ramp_limit_mwh,
            previous_peaker_dispatch_mwh=session.previous_peaker_dispatch_mwh,
            previous_ev_discharge_mwh=session.previous_ev_discharge_mwh,
            previous_peaker_online=session.peaker_online,
            peaker_startup_cost_usd=session.task.peaker_startup_cost_usd,
            peaker_emission_factor_tco2_per_mwh=session.task.peaker_emission_factor_tco2_per_mwh,
            transmission_loss_multiplier=session.contingency_loss_multiplier,
            carbon_price_usd_per_tco2=session.task.carbon_price_usd_per_tco2,
            enable_reserve_logic=session.task.enable_reserve_logic,
            enable_ramp_limits=session.task.enable_ramp_limits,
            enable_startup_emissions=session.task.enable_startup_emissions,
        )

        reward = compute_reward(
            dispatch=dispatch,
            clearing_price=market["clearing_price"] or session.base_price,
            demand_mwh=session.demand_mwh,
            prior_gap=session.prior_gap,
            carbon_price_usd_per_tco2=session.task.carbon_price_usd_per_tco2,
        )

        session.step += 1
        session.ev_storage_mwh = next_storage
        session.last_clearing_price = market["clearing_price"] or session.base_price
        session.prior_gap = dispatch["delivered_supply_mwh"] - session.demand_mwh
        session.previous_peaker_dispatch_mwh = dispatch.get("peaker_dispatch_mwh", 0.0)
        session.previous_ev_discharge_mwh = dispatch.get("ev_discharge_mwh", 0.0)
        session.peaker_online = bool(dispatch.get("peaker_online", False))
        session.correction_count += dispatch["correction_count"]
        if dispatch["correction_count"] > 0:
            session.infeasible_actions += 1
        session.total_demand_met += min(session.demand_mwh, dispatch["delivered_supply_mwh"])
        energy_cost = dispatch["delivered_supply_mwh"] * session.last_clearing_price
        session.total_cost += energy_cost + dispatch.get("startup_cost_usd", 0.0) + dispatch.get("emissions_cost_usd", 0.0)
        session.total_emissions_tco2 += dispatch.get("emissions_tco2", 0.0)
        if dispatch["unmet_demand_mwh"] > 0.0:
            session.blackout_steps += 1
        if dispatch.get("reserve_commitment_active", False):
            session.reserve_commitment_events += 1
        if dispatch.get("emergency_dispatch_triggered", False):
            session.emergency_dispatch_events += 1
        if dispatch.get("stability_risk_index", 0.0) >= 0.45:
            session.stability_events += 1
        session.reward_history.append(reward.score)

        private_views = self._build_private_agent_views(session, market, dispatch)

        next_demand, next_renewable, next_price, dyn_info = evolve_grid(
            demand_mwh=session.demand_mwh,
            renewable_mwh=session.renewable_mwh,
            base_price_usd_per_mwh=session.base_price,
            step=session.step,
            task=session.task,
            rng=session.rng,
        )
        session.demand_mwh = next_demand
        session.renewable_mwh = next_renewable
        session.base_price = next_price
        session.shock_seen = session.shock_seen or dyn_info["shock_active"]
        session.contingency_seen = session.contingency_seen or dyn_info.get("contingency_active", False)
        session.contingency_type = dyn_info.get("contingency_type", "none")
        session.forecast_demand_mwh = dyn_info.get("forecast_demand_mwh", session.demand_mwh)
        session.forecast_renewable_mwh = dyn_info.get("forecast_renewable_mwh", session.renewable_mwh)
        session.load_forecast_error_mwh = dyn_info.get("load_forecast_error_mwh", 0.0)
        session.renewable_forecast_error_mwh = dyn_info.get("renewable_forecast_error_mwh", 0.0)
        session.contingency_peaker_multiplier = dyn_info.get("peaker_capacity_multiplier", 1.0)
        session.contingency_loss_multiplier = dyn_info.get("transmission_loss_multiplier", 1.0)

        event = {
            "step": session.step,
            "market": market,
            "dispatch_action": dispatch_action.model_dump(),
            "dispatch": dispatch,
            "reward": reward.model_dump(),
            "dynamics": dyn_info,
            "agent_private_views": private_views,
        }
        session.event_log.append(event)

        done = session.step >= session.task.max_steps
        session.done = done

        info = {
            "market": market,
            "dispatch_action": dispatch_action.model_dump(),
            "dispatch": dispatch,
            "dynamics": dyn_info,
            "agent_private_views": private_views,
            "summary": {
                "avg_reward": round(sum(session.reward_history) / len(session.reward_history), 4),
                "total_demand_met_mwh": round(session.total_demand_met, 3),
                "total_cost_usd": round(session.total_cost, 3),
                "total_emissions_tco2": round(session.total_emissions_tco2, 4),
                "blackout_steps": session.blackout_steps,
                "infeasible_actions": session.infeasible_actions,
                "ldu_corrections": session.correction_count,
                "reserve_commitment_events": session.reserve_commitment_events,
                "emergency_dispatch_events": session.emergency_dispatch_events,
                "stability_events": session.stability_events,
                "leader_adjusted_bids": market["leader_adjusted_bids"],
                "personality_map": session.personalities,
                "operator_override_enabled": session.operator_override_enabled,
            },
        }

        return StepResponse(
            observation=session.to_observation(),
            reward=reward,
            done=done,
            truncated=False,
            info=info,
        )

    def policy_action(
        self,
        policy: str = "adaptive",
        personality: str = "balanced",
        session_id: Optional[str] = None,
    ) -> JointAction:
        session = self._get_session(session_id)
        obs = session.to_observation()
        if policy == "random":
            return random_joint_action(obs, session.rng)
        if policy == "heuristic":
            return heuristic_joint_action(obs, personality=personality)
        return adaptive_stackelberg_action(obs, personality=personality)

    def dispatch_action(
        self,
        personality: str = "balanced",
        session_id: Optional[str] = None,
        cleared_mwh: Optional[float] = None,
    ) -> DispatchAction:
        session = self._get_session(session_id)
        obs = session.to_observation()
        controller = ReliabilityDispatchControlAgent(personality=personality)
        return controller.act(obs, cleared_mwh=float(cleared_mwh if cleared_mwh is not None else obs.demand_mwh))

    def state(self, session_id: Optional[str] = None) -> StateResponse:
        session = self._get_session(session_id)
        return StateResponse(
            current_task_id=session.task.task_id,
            steps_taken=session.step,
            episode_done=session.done,
            observation=session.to_observation(),
        )

    def events(self, session_id: Optional[str] = None) -> Dict:
        session = self._get_session(session_id)
        return {"session_id": session.session_id, "events": session.event_log[-50:]}

    def inject_shock(self, session_id: Optional[str] = None, renewable_drop_mwh: float = 20.0) -> Dict:
        session = self._get_session(session_id)
        before = session.renewable_mwh
        session.renewable_mwh = max(0.0, session.renewable_mwh - max(0.0, renewable_drop_mwh))
        session.shock_seen = True
        event = {
            "step": session.step,
            "type": "manual_shock",
            "renewable_before_mwh": round(before, 3),
            "renewable_after_mwh": round(session.renewable_mwh, 3),
            "drop_mwh": round(max(0.0, renewable_drop_mwh), 3),
        }
        session.event_log.append(event)
        return {
            "session_id": session.session_id,
            "shock_event": event,
            "observation": session.to_observation(),
        }

    def get_schema(self) -> Dict:
        return {
            "action_schema": JointAction.model_json_schema(),
            "dispatch_action_schema": DispatchAction.model_json_schema(),
            "observation_schema": MarketObservation.model_json_schema(),
            "reward_schema": MarketReward.model_json_schema(),
            "tasks": list_tasks(),
            "notes": "Hybrid Theme 1+2+3.1 baseline implementation with the Physics-Constrained Safety Shield as core physical layer",
        }

    def set_operator_override(self, enabled: bool, session_id: Optional[str] = None) -> Dict:
        session = self._get_session(session_id)
        session.operator_override_enabled = bool(enabled)
        event = {
            "step": session.step,
            "type": "operator_override",
            "enabled": session.operator_override_enabled,
        }
        session.event_log.append(event)
        return {
            "session_id": session.session_id,
            "operator_override_enabled": session.operator_override_enabled,
            "event": event,
        }

    def _get_session(self, session_id: Optional[str]) -> Session:
        sid = session_id or self._latest_session_id
        if sid is None or sid not in self._sessions:
            raise KeyError("No active session. Call /reset first.")
        return self._sessions[sid]

    def _build_private_agent_views(self, session: Session, market: Dict, dispatch: Dict) -> Dict[str, Dict]:
        scarcity = max(0.0, (session.demand_mwh - session.renewable_mwh) / max(session.demand_mwh, 1e-6))
        spread = max(0.0, session.base_price - session.last_clearing_price)
        return {
            "renewable_1": {
                "personality": session.personalities.get("renewable_1", "balanced"),
                "curtailment_risk": round(max(0.0, session.renewable_mwh - market.get("cleared_mwh", 0.0)), 3),
                "forecast_bias": round(session.rng.uniform(-3.0, 3.0), 3),
            },
            "peaker_1": {
                "personality": session.personalities.get("peaker_1", "balanced"),
                "scarcity_index": round(scarcity, 4),
                "margin_signal": round(market.get("clearing_price", session.base_price) - 42.0, 3),
            },
            "industrial_1": {
                "personality": session.personalities.get("industrial_1", "balanced"),
                "budget_pressure": round(
                    market.get("clearing_price", session.base_price) / max(session.base_price, 1e-6),
                    4,
                ),
                "unmet_demand_mwh": dispatch["unmet_demand_mwh"],
            },
            "ev_1": {
                "personality": session.personalities.get("ev_1", "balanced"),
                "soc_ratio": round(session.ev_storage_mwh / max(session.ev_storage_capacity_mwh, 1e-6), 4),
                "arbitrage_spread": round(spread, 3),
            },
        }

    def _resolve_dispatch_action(
        self,
        session: Session,
        market: Dict,
        observation: MarketObservation,
        personality: str = "balanced",
    ) -> DispatchAction:
        controller = ReliabilityDispatchControlAgent(personality=personality)
        return controller.act(observation, cleared_mwh=float(market.get("cleared_mwh", observation.demand_mwh)))
