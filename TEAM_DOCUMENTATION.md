# OpenEnv Smart Grid MarketSim — Team Documentation Guide

**Project:** Multi-Agent Smart Grid Market Simulator with Physical Feasibility Enforcement  
**Framework:** OpenEnv (OpenAI Gymnasium-style APIs)  
**Duration:** Real-time API + async training + visualization dashboard  
**Status:** Production-ready for hackathon demo  

---

## Executive Summary for Judges

**What is this?** A reinforcement learning environment where AI agents learn grid balancing through **strategic bidding** (market layer) constrained by **physical reality** (LDU layer). Agents optimize cost, reliability, and renewable utilization while the LDU enforces feasibility and logs all corrections.

**Why it matters:** Most grid simulators score *planned strategy*. This one scores *actual delivered outcomes* after physical constraints are applied — revealing the gap between market-optimal and physically-feasible decisions.

**Key innovation:** The **Stackelberg-influenced market clearing** combined with **LDU feasibility correction** creates a realistic strategy-reality tension that trains adaptable agents.

---

## Table of Contents

1. [Team Role Assignments & Responsibilities](#team-roles)
2. [System Architecture Overview](#system-architecture)
3. [Role 1: LDU & Physics Specialist](#role-1-ldu--physics-specialist)
4. [Role 2: Agent & Strategy Specialist](#role-2-agent--strategy-specialist)
5. [Role 3: Integration, Narrative & Visualization Lead](#role-3-integration-narrative--visualization-lead)
6. [Project Execution Playbook](#project-execution-playbook)
7. [Validation & Testing](#validation--testing)
8. [Demo Scenarios for Judges](#demo-scenarios-for-judges)

---

## Team Roles

### Role 1: LDU & Physics Specialist
- **Owns:** Load Dispatch Unit physics, constraint enforcement, feasibility corrections
- **Key Files:** `smartgrid_mas/engine/ldu.py`, `smartgrid_mas/engine/dynamics.py`, `smartgrid_mas/engine/reward.py`
- **Responsibilities:**
  - Verify LDU dispatch logic (transmission loss, storage loss, capacity constraints)
  - Tune penalty weights in reward function
  - Validate correction logs and infeasibility detection
  - Optimize grid dynamics evolution (demand & renewable volatility)

### Role 2: Agent & Strategy Specialist
- **Owns:** Agent policies, bidding strategies, personality-driven behavior
- **Key Files:** `smartgrid_mas/engine/policies.py`, `smartgrid_mas/engine/market.py`, `smartgrid_mas/tasks.py`
- **Responsibilities:**
  - Develop competitive baseline policies (random, heuristic, adaptive)
  - Tune Stackelberg market clearing leader signal effects
  - Define task scenarios and difficulty progression
  - Train LLM agent behaviors or rule-based policies

### Role 3: Integration, Narrative & Visualization Lead
- **Owns:** API contracts, web UI, metrics aggregation, story for judges
- **Key Files:** `main.py`, `smartgrid_mas/demo_page.py`, `smartgrid_mas/env.py`, `tests/`
- **Responsibilities:**
  - Maintain FastAPI endpoint health and contract
  - Design intuitive 3D dashboard and real-time visualizations
  - Aggregate episode metrics and generate artifacts
  - Write narrative documentation and prepare demo script

---

## System Architecture

### High-Level Flow

```
┌──────────────────────────────────────────────────────────┐
│  Agent (Client-side)                                     │
│  • Observes market state (price, demand, renewables)     │
│  • Submits strategic bids (supply, demand, EV cmds)      │
└──────────────────────────┬───────────────────────────────┘
                           │ (async REST/WebSocket)
                           ▼
┌──────────────────────────────────────────────────────────┐
│  FastAPI Server (main.py)                                │
│  • Routes: /reset, /step, /state, /events, /demo         │
│  • CORS enabled for cross-origin requests                │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│  SmartGridMarketEnv (env.py)                             │
│  • Session management (multi-user, multi-episode)        │
│  • Orchestrates market → LDU → dynamics → reward         │
└──────────────────────────┬───────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
│ Market Clearing  │ │ LDU Dispatch │ │ Grid Dynamics    │
│ (market.py)      │ │ (ldu.py)     │ │ (dynamics.py)    │
│                  │ │              │ │                  │
│ • Leader signal  │ │ • Feasibility│ │ • Demand trend   │
│ • Price matching │ │ • Corrections│ │ • Renewable flux │
│ • Bid adjustment │ │ • Losses     │ │ • Volatility     │
└──────────────────┘ └──────────────┘ └──────────────────┘
        ▲                  ▲                  ▲
        └──────────────────┼──────────────────┘
                           │
                           ▼
                    ┌─────────────────┐
                    │ Reward Function │
                    │ (reward.py)     │
                    │ • Satisfaction  │
                    │ • Cost efficiency│
                    │ • Renewables    │
                    │ • Penalties     │
                    └─────────────────┘
```

### Data Flow (Single Step)

```
Agent submits JointAction
  ├─ bids: [AgentBid {...}, ...]
  ├─ ev_charge_mwh: float
  └─ ev_discharge_mwh: float
         ↓
  Market clears bids (leader signal applied)
  ├─ Adjust bids based on leader_price_signal
  ├─ Match supply↔demand by price
  └─ Emit clearing_price, cleared_mwh
         ↓
  LDU enforces dispatch feasibility
  ├─ Check EV constraints (charge/discharge limits)
  ├─ Allocate renewable → peaker → grid
  ├─ Calculate losses (transmission 3%, storage 8%)
  └─ Log corrections & emit dispatch details
         ↓
  Reward computed
  ├─ Satisfaction score (delivered / demand)
  ├─ Cost efficiency score
  ├─ Renewable utilization score
  ├─ Penalties for infeasibility & blackouts
  └─ Combined: 0.34×sat + 0.23×cost + 0.18×ren + ... 
         ↓
  Session updates & event log appended
         ↓
  MarketObservation returned (state for next step)
```

---

## Role 1: LDU & Physics Specialist

### Overview

The **Load Dispatch Unit (LDU)** is the heart of physical realism. It takes market-cleared quantities and enforces real-world constraints:
- Storage capacity bounds
- Transmission & storage losses
- Generation capacity limits
- Simultaneous charge/discharge prohibition

**Impact:** When agent bids are market-optimal but physically infeasible, the LDU corrects them, logs the event, and reduces reward. This teaches agents to bid *physically-aware*.

---

### File: `smartgrid_mas/engine/ldu.py`

**Purpose:** Enforce physical constraints and compute feasible dispatch

**Key Function:** `enforce_dispatch()`

```python
def enforce_dispatch(
    market_result: Dict,           # From market clearing
    demand_mwh: float,              # Current demand
    renewable_available_mwh: float, # Available renewable generation
    peaker_capacity_mwh: float,     # Max thermal generation
    ev_storage_mwh: float,          # Current battery state
    ev_storage_capacity_mwh: float, # Max battery capacity
    ev_charge_mwh: float,           # Desired charge
    ev_discharge_mwh: float,        # Desired discharge
) -> Tuple[Dict, float]:            # (dispatch details, next_storage)
```

**Physics Logic:**

1. **EV Storage Constraints**
   - No simultaneous charge & discharge → prioritize discharge
   - Charge headroom: `max_charge = storage_capacity - storage_mwh`
   - Discharge limit: `max_discharge = storage_mwh`
   - Clamp: `charge = min(desired, max_charge)`, `discharge = min(desired, max_discharge)`

2. **Generation Dispatch Priority**
   ```
   Available supply = market_cleared_mwh
   
   Renewable dispatch = min(renewable_available, available_supply)
   Residual = available_supply - renewable_dispatch
   Peaker dispatch = min(peaker_capacity, residual)
   
   If residual > peaker_capacity → correction logged (undersupply risk)
   ```

3. **Transmission & Storage Losses**
   - **Transmission loss:** 3% of gross supply (renewable + peaker + discharge)
   - **Storage loss:** 8% of charge energy (energy dissipation in battery)
   - Net delivery: `delivered = gross_supply - transmission_loss`

4. **Unmet Demand & Oversupply**
   ```
   unmet = max(0, demand - delivered)
   oversupply = max(0, delivered - demand)
   ```

5. **Next Storage State**
   ```
   next_storage = current_storage + charge - discharge - storage_loss
   Clamped to [0, storage_capacity]
   ```

**Correction Logging:**

The function tracks and logs all corrections:
```python
corrections = [
    "Simultaneous EV charge and discharge corrected by LDU",
    "EV charge exceeded storage headroom",
    "Market-cleared supply exceeded physical generation capacity",
    ...
]
```

Each correction signals to the agent: "Your bid was infeasible — penalty applied."

---

### File: `smartgrid_mas/engine/dynamics.py`

**Purpose:** Evolve grid state (demand, renewable supply, price) across time steps

**Key Function:** `evolve_grid()`

```python
def evolve_grid(
    demand_mwh: float,
    renewable_mwh: float,
    base_price_usd_per_mwh: float,
    step: int,
    task: TaskConfig,
    rng: random.Random,
) -> Tuple[float, float, float, Dict]:
    # Returns: (next_demand, next_renewable, next_price, metadata)
```

**Physics Logic:**

1. **Shock Injection**
   - If `step == task.shock_step` → sudden renewable drop
   - `next_renewable -= task.shock_renewable_drop`
   - Simulates grid faults, weather changes, line outages

2. **Stochastic Trends with Volatility**
   ```
   demand_noise ~ Gaussian(0, task.demand_volatility)
   renewable_noise ~ Gaussian(0, task.renewable_volatility)
   
   next_demand = demand + task.demand_trend + noise
   next_renewable = renewable + task.renewable_trend + noise
   (+ shock if active)
   ```

3. **Price Evolution (Supply-Demand Imbalance)**
   ```
   scarcity_ratio = (demand - renewable) / 300.0
   implied_price = base_price * (1 + max(0, scarcity_ratio))
   next_price = max(5.0, implied_price)
   ```
   - When renewable drops or demand spikes → price rises
   - This provides price signal for agent strategy adaptation

**Constraints:**
- `demand >= 20 MWh` (grid minimum)
- `renewable >= 0`
- `price >= $5/MWh`

---

### File: `smartgrid_mas/engine/reward.py`

**Purpose:** Compute multi-objective reward signal that balances grid objectives

**Key Function:** `compute_reward()`

```python
def compute_reward(
    dispatch: dict,           # From LDU (delivered, unmet, etc.)
    clearing_price: float,    # Market clearing price
    demand_mwh: float,        # Current demand
    prior_gap: float,         # Delivery gap from previous step
) -> MarketReward:
```

**Reward Components:**

| Component | Weight | Formula | Meaning |
|-----------|--------|---------|---------|
| **Demand Satisfaction** | 0.34 | `delivered / demand` (clamped ≤1) | Did we meet demand? |
| **Cost Efficiency** | 0.23 | `max(0, 1 - total_cost/12000)` | Did we minimize cost? |
| **Renewable Utilization** | 0.18 | `renewable_dispatch / delivered` | Did we use clean energy? |
| **Stability** | 0.15 | `max(0, 1 - abs(gap_change)/80)` | Was dispatch stable? |
| **Infeasibility Penalty** | -0.2 | `min(1, corrections×0.15 + storage_loss×0.01)` | How many violations? |
| **Blackout Penalty** | -0.2 | `unmet / demand` | How much unmet demand? |
| **Oversupply Penalty** | -0.03 | `oversupply / demand` | Wasted energy? |

**Final Score:**
```python
raw = 0.34×sat + 0.23×cost + 0.18×ren + 0.15×stab - 0.2×infeas - 0.2×blackout - 0.03×waste
score = clamp(raw, 0.0, 1.0)
```

**Tuning Opportunities:**

1. **Adjust weights** if you want to prioritize renewables over cost, etc.
2. **Modify penalty functions** (e.g., quadratic vs linear infeasibility)
3. **Add new metrics** (e.g., grid frequency, voltage stability)

**Example Output:**
```json
{
  "score": 0.71,
  "reason": "delivered=50.0 demand=50.0 unmet=0.0 price=45.0 corrections=1",
  "demand_satisfaction_score": 1.0,
  "cost_efficiency_score": 0.5,
  "renewable_utilization_score": 0.8,
  "stability_score": 0.95,
  "infeasibility_penalty": 0.15,
  "blackout_penalty": 0.0
}
```

---

### Responsibilities for Role 1

**Immediate Tasks (Before Demo):**

- [ ] Verify LDU constraints are correctly implemented
  - Test: Force infeasible charge/discharge → confirm correction logged
  - Test: Market-clear > generation capacity → confirm adjustment
  
- [ ] Validate loss calculations
  - Test: With 100 MWh supply, transmission loss should be ~3 MWh
  - Test: With 10 MWh charge, storage loss should be ~0.8 MWh

- [ ] Confirm reward scoring is fair
  - Run 5 deterministic episodes (seed=42) → verify reproducible scores
  - Check that random policy scores ~0.3–0.4, heuristic ~0.5–0.6

- [ ] Document physical assumptions
  - Write a 1-page brief: "Grid Physics Model" covering loss assumptions, storage dynamics, etc.

**During Demo:**

- Explain LDU layer to judges with specific corrected-bid examples
- Show event log with correction messages
- Highlight how "market-optimal" bids sometimes get corrected

**Training Phase (if continuing):**

- Experiment with asymmetric agent knowledge (e.g., one agent doesn't see losses)
- Add stochastic failures (e.g., 2% renewable generation dropout)
- Implement rolling blackout simulation

---

## Role 2: Agent & Strategy Specialist

### Overview

Agents learn to bid strategically in the market while anticipating LDU feasibility constraints. Three baseline policies provided:
1. **Random** — No strategy, random bid quantities/prices
2. **Heuristic** — Fixed rule-based strategy per personality
3. **Adaptive Stackelberg** — Responds to leader price signal and market scarcity

**Narrative:** Agents that ignore physical constraints get corrected (penalty). Agents that anticipate feasibility win.

---

### File: `smartgrid_mas/engine/market.py`

**Purpose:** Clear market bids and apply Stackelberg leader price signal

**Key Function:** `clear_market()`

```python
def clear_market(
    bids: List[AgentBid],
    leader_price_signal: float,
) -> Dict:
    # Returns: {cleared_mwh, clearing_price, matches, ...}
```

**Market Clearing Algorithm:**

1. **Apply Leader Signal** (Stackelberg influence)
   - Supply bids: floor price at `0.8×leader_signal` (peakers: `0.95×leader`)
   - Demand bids: clamp to `[0.9×leader, 1.8×leader]`
   - This models a "grid operator" (Stackelberg leader) influencing prices

2. **Sort by Price**
   - Supplies: ascending (lowest first = cheapest generation)
   - Demands: descending (highest first = most eager buyers)

3. **Bilateral Matching**
   - Match highest-priced demand with lowest-priced supply
   - Continue until no valid crosses
   - Clearing price: midpoint of matched pair

4. **Output Metrics**
   ```json
   {
     "cleared_mwh": 120.5,
     "clearing_price": 52.3,
     "leader_price_signal": 50.0,
     "leader_adjusted_bids": 3,
     "matches": [
       {"supply_agent": "renewable_1", "demand_agent": "industrial_1", 
        "quantity_mwh": 50.0, "price_usd_per_mwh": 52.3},
       ...
     ]
   }
   ```

**Why Stackelberg?** It models realistic grid operations where a central authority (TSO/ISO) influences prices to achieve policy goals (e.g., renewable preference, cost containment).

---

### File: `smartgrid_mas/engine/policies.py`

**Purpose:** Define baseline agent bidding strategies

**Policy 1: Random**

```python
def random_joint_action(obs: MarketObservation, rng: random.Random) -> JointAction:
```

- Renewable supply: `uniform(10, renewable_available)`
- Peaker supply: `uniform(5, peaker_capacity)`
- Industrial demand: `uniform(0.6×demand, 1.1×demand)`
- Prices: random within plausible ranges
- EV: random charge/discharge

**Use case:** Baseline for RL training (agents should beat random)

---

**Policy 2: Heuristic**

```python
def heuristic_joint_action(obs: MarketObservation, personality: str) -> JointAction:
    # personality in {"greedy", "risk_averse", "balanced"}
```

**Personalities:**

| Personality | Supply Offer | Price Strategy | EV Strategy |
|-------------|--------------|----------------|------------|
| **Greedy** | High; cover 55% of demand from renewables, 45% from peaker | High markup on peaker (8% above leader) | Discharge heavily if scarcity > 20% |
| **Balanced** | Medium; cover 55% from renewables, adjust peaker based on scarcity | Medium markup (~2% above leader) | Charge if renewables abundant, discharge if scarce |
| **Risk-Averse** | Conservative; bid lower quantities to avoid corrections | Low markup (~2% below leader) | Charge heavily if renewables available, rarely discharge |

**Effect:** Same observation → different bids based on personality. Enables multi-agent dynamics (competitive, collaborative, or mixed).

---

**Policy 3: Adaptive Stackelberg**

```python
def adaptive_stackelberg_action(obs: MarketObservation, personality: str) -> JointAction:
    # More sophisticated, responds to scarcity and leader signal
```

**Logic:**

1. **Scarcity Awareness**
   ```python
   scarcity = max(0, (demand - renewable_available) / demand)
   # If scarcity > 0.35, renewable is stretched → agents bid higher to compensate
   ```

2. **Dynamic Bid Quantities**
   - Renewable offer: `min(renewable_available, demand × (0.52 + 0.18×(1-scarcity)))`
   - Peaker offer: `min(peaker_capacity, (demand - renewable) × (1 + 0.25×scarcity))`
   - Under stress, peaker bids go up (higher quantities → higher cost/penalty risk)

3. **Price Response to Leader**
   - Personality-driven markup:
     - Opportunistic: `1.16× leader_signal`
     - Balanced: `1.10× leader_signal`
     - Risk-averse: `1.03× leader_signal`

4. **EV Storage Strategy**
   - If scarcity > 0.25: discharge to help grid, don't charge
   - Otherwise: charge proactively to build reserves

**Why Adaptive?** Simulates learning behavior without explicit RL. Good baseline for LLM agent fine-tuning.

---

### File: `smartgrid_mas/tasks.py`

**Purpose:** Define scenario configurations for training

**Three Tasks:**

| Task | Duration | Demand | Renewable | Difficulty | Use Case |
|------|----------|--------|-----------|------------|----------|
| **default** | 24 steps | Constant 120 → +1.2/step | Constant 70 → -0.6/step; shock at step 16 (-22 MWh) | Medium | General training & validation |
| **long_horizon** | 48 steps | 135 → +1.5/step | 78 → -0.8/step; shock at step 28 (-26 MWh) | Hard | Multi-step planning; storage foresight |
| **stress_shock** | 30 steps | 150 → +2.0/step | 85 → -1.0/step; shock at step 12 (-35 MWh) | Very Hard | Emergency response; robustness |

**Customization:**

Each task is a `TaskConfig` dataclass:
```python
@dataclass
class TaskConfig:
    task_id: str
    description: str
    max_steps: int
    initial_demand_mwh: float
    initial_renewable_mwh: float
    peaker_capacity_mwh: float
    ev_storage_mwh: float
    ev_storage_capacity_mwh: float
    base_price_usd_per_mwh: float
    demand_trend_mwh: float        # +per_step
    renewable_trend_mwh: float     # +per_step
    demand_volatility: float       # std_dev of Gaussian noise
    renewable_volatility: float    # std_dev of Gaussian noise
    shock_step: int                # When shock hits
    shock_renewable_drop: float    # MWh drop
    hint: str                      # Display to agent at reset
```

**To Add a New Task:**

```python
TASKS["my_task"] = TaskConfig(
    task_id="my_task",
    description="My custom scenario...",
    max_steps=20,
    initial_demand_mwh=110.0,
    # ... fill in rest
    shock_step=10,
    shock_renewable_drop=20.0,
    hint="Strategy: ...",
)
```

Then reference it: `env.reset(task_id="my_task")`

---

### Responsibilities for Role 2

**Immediate Tasks (Before Demo):**

- [ ] Verify all three policies produce valid actions
  - Test: Run each policy 10 steps deterministically (seed=42)
  - Check: No NaN, no negative quantities, prices in plausible range

- [ ] Validate policy personalities diverge
  - Example: Under scarcity, greedy should bid higher than risk_averse
  - Compare prices bid by each personality → confirm separation

- [ ] Run baseline episode collection
  - `python smartgrid_mas/train_baseline.py --episodes 30 --outdir artifacts`
  - Expected outputs: `baseline_metrics.csv` and `reward_comparison.png`
  - Check: Adaptive > Heuristic > Random on average

- [ ] Document agent personas
  - Write 1-page brief: "Agent Personalities & Strategies"
  - Include tables showing bid quantities/prices under different conditions

**During Demo:**

- Explain market clearing with Stackelberg example
- Show how leader signal influences bids
- Highlight scarcity-adaptive behavior (e.g., higher discharge under stress)
- Demonstrate multi-run variance (same policy, different seeds → different outcomes)

**Training Phase (if continuing):**

- Implement custom LLM agent wrapper
- Track learning curves (episode reward over time)
- Compare learned policy vs baselines
- Ablation studies: policy performance without leader signal, without storage, etc.

---

## Role 3: Integration, Narrative & Visualization Lead

### Overview

You are the **project cohesion layer**. Your role is to:
1. Keep all APIs working and contracts stable
2. Craft the story for judges (why this matters, what it demonstrates)
3. Build and maintain visualizations
4. Aggregate results into compelling narratives

---

### File: `main.py`

**Purpose:** FastAPI server exposing all environment endpoints

**Endpoints Summary:**

| Route | Method | Query/Body | Response | Purpose |
|-------|--------|-----------|----------|---------|
| `/` | GET | — | Welcome info | Health check + docs links |
| `/health` | GET | — | `{status: "ok"}` | Probe for liveness |
| `/reset` | POST | `{task_id, seed}` | `{session_id, observation, ...}` | Start new episode |
| `/step` | POST | `{action: JointAction}` | `{observation, reward, done, info}` | Execute one action |
| `/state` | GET | `?session_id=...` | `{observation, episode_done, ...}` | Query current state (no step) |
| `/events` | GET | `?session_id=...` | `{events: []}` | Fetch all events since reset |
| `/events/stream` | GET | `?session_id=..., poll_ms=650` | SSE stream | Real-time event feed |
| `/inject-shock` | POST | `{renewable_drop_mwh: 20}` | Updated observation | Trigger grid shock |
| `/demo` | GET | — | HTML page | Interactive 3D dashboard |
| `/info` | GET | — | `{tasks, schema}` | Endpoint metadata & action/obs schema |
| `/run-inference` | POST | `{policy, task_id, seed}` | Trajectory + rewards | Run built-in baseline agent deterministically |

**Session Management:**

- Each `/reset` creates a new session with unique UUID
- Subsequent `/step`, `/state`, `/events` use `?session_id=<uuid>`
- Server maintains in-memory dict: `sessions[session_id] → Session`
- Sessions persist for the lifetime of the server process

**CORS Enabled:**
```python
CORSMiddleware(
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
→ Allows cross-origin requests from frontend dashboards

---

### File: `smartgrid_mas/demo_page.py`

**Purpose:** Generate interactive HTML dashboard for judges

**Features:**

1. **Three-Pane Layout**
   - Left: Session controls (task, policy, personality, speed)
   - Center: 3D pseudo-visual of grid state (Canvas/WebGL)
   - Right: Metrics timeline + event log

2. **Session Controls**
   ```
   Task: [default | long_horizon | stress_shock]
   Policy: [adaptive | heuristic | random]
   Personality: [balanced | risk_averse | opportunistic | greedy]
   Speed: [100–1800 ms per step]
   
   Buttons: Reset | Step | Play | Pause | Inject Shock
   ```

3. **Metrics Display (Real-time)**
   - Demand (MWh)
   - Renewable available (MWh)
   - Clearing price ($/MWh)
   - Delivered supply (MWh)
   - Unmet demand (MWh)
   - Step count

4. **Event Log**
   - Timestamped events: "Bid submitted", "LDU correction", "Shock injected", etc.
   - Scrollable, max 180px height
   - Shows last 10–20 events

5. **3D Visualization** (Pseudo-3D using Canvas)
   - Grid nodes arranged in pseudo-3D perspective
   - Energy flows as animated particles
   - Color intensity = price or congestion
   - Shocks visualized as red flashes

**Browser Tech:**
- Pure HTML + inline JavaScript (no build step)
- WebSocket or SSE for real-time updates
- Canvas for visualization
- Responsive grid layout (mobile-friendly)

---

### File: `smartgrid_mas/env.py`

**Purpose:** Core environment orchestration

**Key Class: `SmartGridMarketEnv`**

```python
class SmartGridMarketEnv:
    def reset(task_id: str, seed: int) -> ResetResponse
    def step(action: JointAction, session_id: str) -> StepResponse
    def state(session_id: str) -> StateResponse
    def events(session_id: str) -> {events: [...]}
    def inject_shock(session_id: str, renewable_drop_mwh: float) -> StateResponse
    def get_schema() -> {tasks, action_schema, observation_schema, ...}
```

**Session Lifecycle:**

1. **Reset**
   - Create session with task config
   - Initialize demand, renewable, storage to task defaults
   - Assign random personalities to agents
   - Return initial observation + hint

2. **Step** (repeated)
   - Receive `JointAction` from agent
   - Call `clear_market(bids, leader_signal)`
   - Call `enforce_dispatch(market_result, ...)`
   - Call `evolve_grid(...)` → update demand/renewable/price
   - Compute `reward(...)`
   - Update session state
   - Log events
   - Check if `step >= max_steps` → set `done=True`
   - Return `StepResponse`

3. **State Query**
   - Return current observation without advancing
   - Allows agent to query without stepping

4. **Events Query**
   - Return all logged events since reset
   - Used by dashboard to replay or audit

5. **Shock Injection**
   - Manually drop renewable supply
   - Simulates grid fault during episode
   - Used in `/demo` for interactive stress testing

---

### File: `smartgrid_mas/models.py`

**Purpose:** Pydantic data models (type-safe, auto-documented)

**Key Models:**

```python
# Input
class AgentBid(BaseModel):
    agent_id: str
    role: AgentRole  # "renewable_prosumer" | "peaker_plant" | "industrial_load" | "ev_aggregator"
    bid_type: BidType  # "supply" | "demand"
    quantity_mwh: float
    price_usd_per_mwh: float

class JointAction(BaseModel):
    bids: List[AgentBid]
    ev_charge_mwh: float
    ev_discharge_mwh: float

# Output
class MarketObservation(BaseModel):
    step: int
    demand_mwh: float
    renewable_availability_mwh: float
    peaker_capacity_mwh: float
    ev_storage_mwh: float
    ev_storage_capacity_mwh: float
    last_clearing_price: float
    leader_price_signal: float
    scarcity_index: float  # (demand - renewable) / demand
    shock_active: bool
    public_signal: str  # Narrative hint ("Shock regime active", etc.)
    schema_info: str  # LLM-readable action space description
    hint: Optional[str]  # Task-specific hint at reset
    error_message: Optional[str]  # If action was invalid

class MarketReward(BaseModel):
    score: float  # [0, 1]
    reason: str
    demand_satisfaction_score: float
    cost_efficiency_score: float
    renewable_utilization_score: float
    stability_score: float
    infeasibility_penalty: float
    blackout_penalty: float

# API Requests/Responses
class ResetRequest(BaseModel): ...
class ResetResponse(BaseModel): ...
class StepRequest(BaseModel): ...
class StepResponse(BaseModel): ...
class StateResponse(BaseModel): ...
```

**Why Pydantic?**
- Auto-validation (invalid JSON rejected before business logic)
- Auto-OpenAPI documentation (Swagger UI at `/docs`)
- Type hints → IDE autocomplete
- Serialization/deserialization (JSON ↔ Python objects)

---

### File: `smartgrid_mas/train_baseline.py`

**Purpose:** Run baseline policy episodes and generate artifacts

**Usage:**
```bash
python smartgrid_mas/train_baseline.py --episodes 30 --outdir artifacts
```

**Output:**

1. **artifacts/baseline_metrics.csv**
   ```
   episode,random_avg_reward,heuristic_avg_reward,adaptive_avg_reward
   1,0.345123,0.512340,0.623451
   2,0.367890,0.524123,0.631234
   ...
   ```

2. **artifacts/reward_comparison.png**
   - Line plot: episode vs avg_reward for each policy
   - Expected pattern: Random < Heuristic < Adaptive

**Use for Demo:**
- Show judges the CSV data
- Display the plot → visual evidence that adaptive policy learns
- Mention: "We can train LLM agents on this same environment"

---

### Responsibilities for Role 3

**Immediate Tasks (Before Demo):**

- [ ] Verify API contract
  - Run: `pytest tests/test_api_contract.py`
  - Confirm all endpoints respond correctly
  - Validate JSON schemas

- [ ] Check demo dashboard
  - Open: `http://localhost:7860/demo`
  - Manually test Reset, Step, Play buttons
  - Verify metrics update in real-time
  - Check: No console errors

- [ ] Generate baseline artifacts
  - Run: `python smartgrid_mas/train_baseline.py --episodes 50 --outdir artifacts`
  - Verify CSV and PNG are generated
  - Use for slide deck + demo narrative

- [ ] Write demo script
  - 1-page bullet-point script: "What to show judges and why"
  - Example: "First reset with 'default' task, show initial observation, explain scarcity_index, click Step 5 times, point out reward increasing then dipping due to LDU correction..."

- [ ] Prepare narrative deck
  - 5–8 slides covering: problem statement, architecture, three scenarios, results
  - Include screenshots of dashboard and baseline plot

**During Demo:**

1. **Opening (1 min)**
   - "This environment tests AI agents on grid balancing"
   - "Unlike other simulators, we score *delivered outcomes* after physical constraints, not just planned strategy"
   - "Why it matters: Real grid operators face this gap daily"

2. **API & Architecture (1.5 min)**
   - Show `POST /reset` + observation (demand, renewable, etc.)
   - Show `POST /step` with sample bid
   - Explain market clearing → LDU dispatch → reward
   - Highlight: "LDU corrects infeasible bids, logs them, reduces reward"

3. **Interactive Demo (2–3 min)**
   - Open dashboard at `/demo`
   - Select "adaptive" policy, "default" task
   - Click "Play" → watch 10 steps
   - Point out: reward fluctuates, metrics update, event log shows corrections
   - Click "Inject Shock" → show renewable drop, reward response
   - Navigate to "stress_shock" scenario → show harder problem

4. **Baselines (1 min)**
   - Show `baseline_metrics.csv` + plot
   - "Random policy scores ~0.35, heuristic ~0.52, adaptive ~0.63"
   - Highlight: "This is deterministic baseline. Real RL agents can surpass this."

5. **Closing (1 min)**
   - "Three agent personas (greedy, balanced, risk-averse) enable realistic multi-agent dynamics"
   - "Stackelberg market clearing models real TSO influence"
   - "LDU constraints ensure learned policies are physically valid"
   - "Next: integrate LLM fine-tuning for emergent collective behavior"

**Post-Demo (if judges ask questions):**

- *"Can agents cheat the reward system?"* → No, LDU enforces feasibility. Physically infeasible bids are corrected and penalized.
- *"How realistic is the physics?"* → Simplified but structurally sound. Transmission loss (3%), storage loss (8%), capacity constraints, etc. are standard assumptions.
- *"Can you add feature X (e.g., voltage stability)?"* → Yes, via extending the reward function. Modular design.
- *"Training time?"* → 50 episodes of heuristic baseline takes ~10s. RL agents (with LLM) would take hours to days depending on algorithm.

---

### Visualization & Metrics Roadmap

**Current (MVP):**
- Real-time metrics display (6 KPIs)
- Event log with correction messages
- Pseudo-3D grid visualization
- Reward curve plot in artifacts

**Near-term (Post-Hackathon):**
- Animated supply/demand balance bar chart
- Price history sparkline
- Agent bid heatmap (price vs quantity per agent)
- Replay tool (step backward through history)

**Future:**
- Multi-episode comparison dashboard
- Statistical tests for policy significance
- Learned policy heat-map (which states have high reward)
- Attention visualization (if using Transformer agents)

---

## Project Execution Playbook

### Phase 1: Environment Setup (30 min before demo)

```bash
# 1. Install dependencies
cd OpenEnv-SmartGrid-MarketSim
python -m pip install -e .

# 2. Run quick validation
pytest tests/test_api_contract.py -v

# 3. Generate baseline artifacts
python smartgrid_mas/train_baseline.py --episodes 50 --outdir artifacts

# 4. Start server
python main.py
# Expected output:
#   INFO:     Uvicorn running on http://0.0.0.0:7860
#   INFO:     Application startup complete

# 5. In another terminal, verify endpoints
curl http://localhost:7860/health
# Expected: {"status":"ok","service":"openenv-smartgrid-marketsim"}

curl http://localhost:7860/info | jq .
# Expected: {tasks: {...}, action_schema: {...}, observation_schema: {...}}
```

### Phase 2: Browser Demo Setup (10 min before demo)

```bash
# 1. Open dashboard
open http://localhost:7860/demo

# 2. Verify interactive controls respond
#    - Click Reset → observation updates
#    - Click Step → metrics change
#    - Select different task/policy → display adapts

# 3. Have terminal ready for manual API calls
curl -X POST http://localhost:7860/reset \
  -H 'Content-Type: application/json' \
  -d '{"task_id":"default","seed":42}'
```

### Phase 3: During Demo

**Timeline (5–7 minutes):**

1. **(0:00–1:00)** Problem & Story
   - Problem: Grid operators balance demand/supply every 5 min; current simulators ignore physics
   - Story: "We built an RL environment where agents learn realistic tradeoffs"
   - Setup: Three agents (renewable, peaker, industrial), one market, one LDU

2. **(1:00–2:30)** Architecture Walkthrough
   - Show diagram (or draw on board): Agents → Market → LDU → Reward
   - Highlight: "Market clears bids. LDU enforces feasibility. Reward balances objectives."
   - Key insight: "Physically-infeasible bids get corrected + penalized"

3. **(2:30–4:30)** Interactive Demo
   - Open `/demo`
   - Reset with default task
   - Manually step through 5–10 steps, narrating:
     - "Renewable bid: X MWh at $Y/MWh"
     - "Market cleared Y MWh at $Z (leader signal applied)"
     - "LDU delivers (accounting for losses)"
     - "Reward: 0.68 (good demand satisfaction, but high cost)"
   - Click "Inject Shock" → renewable suddenly drops
   - Show agent response: "Higher peaker bid, more EV discharge, but still sustainable"

4. **(4:30–5:30)** Baselines & Results
   - Show `artifacts/reward_comparison.png`
   - Narrate: "Random ~0.35, Heuristic ~0.52, Adaptive ~0.63"
   - Point out: "Adaptive learns market dynamics and scarcity awareness"

5. **(5:30–6:30)** Closing
   - "Three agent personalities enable rich multi-agent dynamics"
   - "Stackelberg leader signal models realistic TSO influence"
   - "LDU ensures any trained policy is physically valid"
   - Q&A

### Phase 4: Contingency Scenarios

**If server won't start:**
```bash
# Check port conflict
lsof -i :7860

# Try alternative port (update main.py)
python main.py --port 8080
```

**If demo dashboard doesn't load:**
```bash
# Check console errors
curl http://localhost:7860/demo -s | head -50

# Fallback: Use curl commands directly
# Show judges the raw JSON instead of UI
curl -X POST http://localhost:7860/reset -d '{...}' | jq .
```

**If baseline artifacts missing:**
```bash
# Generate on the fly (takes ~30s)
python smartgrid_mas/train_baseline.py --episodes 10 --outdir artifacts

# Display metrics in terminal
cat artifacts/baseline_metrics.csv
```

---

## Validation & Testing

### Test Suite

**File: `tests/test_market_and_ldu.py`**
- Verifies market clearing (sorted bids, price matching)
- Verifies LDU corrections (storage bounds, capacity limits)

**File: `tests/test_api_contract.py`**
- Verifies all endpoints respond with correct HTTP codes
- Validates response JSON schemas
- Tests session persistence

**File: `tests/test_reward_and_determinism.py`**
- Checks reward scoring bounds [0, 1]
- Verifies deterministic reproducibility (seed=42)

**Run All Tests:**
```bash
pytest tests/ -v
# Expected: 12/12 passed ✓
```

### Reproducibility Checklist

Before demo, verify:

- [ ] Seed=42 → Same trajectory deterministically
  ```bash
  python smartgrid_mas/train_baseline.py --episodes 1 --seed 42 | tee run1.txt
  python smartgrid_mas/train_baseline.py --episodes 1 --seed 42 | tee run2.txt
  diff run1.txt run2.txt
  # Should be identical
  ```

- [ ] API responses are valid JSON
  ```bash
  curl http://localhost:7860/reset -X POST -d '{...}' | jq empty
  # No error → valid JSON
  ```

- [ ] All corrections logged
  ```bash
  curl http://localhost:7860/events?session_id=<id> | jq '.events[] | .message' | grep -i correction
  # Should see corrections if bids were infeasible
  ```

---

## Demo Scenarios for Judges

### Scenario 1: Normal Operations (3 min)

**Setup:** `default` task, `adaptive` policy, seed=42

**Narrative:**
- "Typical day: demand ~120 MWh, renewable ~70 MWh"
- "Agents bid strategically"
- "Market clears; LDU delivers with 3% transmission loss"
- "Reward ~0.60 (good balance of objectives)"

**Show:**
- Initial observation (demand, renewable, price)
- 5 steps of bidding + delivery
- Event log showing no corrections (bids were feasible)
- Reward trending upward

---

### Scenario 2: Scarcity Stress (2 min)

**Setup:** Same, but navigate to step 16 where shock hits

**Narrative:**
- "Sudden renewable drop (-22 MWh)"
- "Demand still high"
- "Scarcity index spikes"
- "Adaptive agent responds: higher peaker bid, more EV discharge"
- "Market clears at higher price"
- "Despite stress, reward stays ~0.45 (no blackout, but higher cost)"

**Show:**
- Shock event in log
- Observable change: `renewable_availability` drops
- `scarcity_index` rises
- Agent increases peaker supply
- Reward adjusts downward (cost efficiency penalty)

---

### Scenario 3: Multi-Step Comparison (2 min)

**Setup:** Run episode with each policy back-to-back

**Narrative:**
- "Let's compare strategies over 10 steps"
- "Random policy: erratic bids, frequent corrections, reward ~0.35"
- "Heuristic policy: stable bids, fewer corrections, reward ~0.52"
- "Adaptive policy: responds to scarcity, avoids corrections, reward ~0.63"

**Show:**
- Three terminal windows (or rapid switching)
- Each policy running same task, same seed
- Metrics at step 10
- Reward curves diverging

---

### Scenario 4: Manually Injected Shock (1 min)

**Setup:** Play episode, then inject shock mid-episode

**Narrative:**
- "What if grid operator wants to test agent robustness?"
- Click "Inject Shock" button
- "20 MWh renewable suddenly offline"
- "Agent must adapt within single step"
- "Good agents recover; bad agents trigger blackout"

**Show:**
- Shock confirmation in event log
- Observation updates (renewable drops)
- Agent's next bid reflects scarcity
- Unmet demand briefly rises, then stabilizes

---

## File Directory Tree (Quick Reference)

```
OpenEnv-SmartGrid-MarketSim/
├── main.py                       # FastAPI server entry point
├── pyproject.toml                # Dependencies
├── Dockerfile                    # Container image
├── openenv.yaml                  # Environment manifest
├── README.md                      # Quick start
├── TEAM_DOCUMENTATION.md         # This file
│
├── smartgrid_mas/                # Main package
│   ├── __init__.py
│   ├── env.py                    # SmartGridMarketEnv (orchestrator)
│   ├── models.py                 # Pydantic data models
│   ├── tasks.py                  # Task configurations (3 scenarios)
│   ├── demo_page.py              # HTML dashboard generator
│   ├── train_baseline.py         # Baseline policy runner
│   │
│   └── engine/                   # Core physics & market
│       ├── __init__.py
│       ├── ldu.py                # Load Dispatch Unit (Role 1)
│       ├── market.py             # Market clearing (Role 2)
│       ├── dynamics.py           # Grid evolution (Role 1)
│       ├── policies.py           # Agent policies (Role 2)
│       └── reward.py             # Reward function (Role 1)
│
├── tests/                        # Validation suite
│   ├── test_market_and_ldu.py
│   ├── test_api_contract.py
│   └── test_reward_and_determinism.py
│
├── training/                     # Training artifacts
│   └── Colab_Unsloth_HF_TRL_Training.ipynb  # LLM fine-tuning template
│
└── artifacts/                    # Generated outputs (gitignored)
    ├── baseline_metrics.csv
    └── reward_comparison.png
```

---

## Summary: Who Does What

| Role | Files | Key Metric | Demo Points |
|------|-------|-----------|------------|
| **Role 1: Physics** | `ldu.py`, `dynamics.py`, `reward.py` | Correction count, feasible dispatch | "LDU enforces reality; market-optimal bids get corrected" |
| **Role 2: Agents** | `market.py`, `policies.py`, `tasks.py` | Adaptive vs heuristic reward | "Agents learn scarcity awareness; personalities diverge" |
| **Role 3: Integration** | `main.py`, `demo_page.py`, `env.py`, `train_baseline.py` | API uptime, visualization responsiveness | "Seamless multi-agent flow; three scenarios; deterministic results" |

---

## Judging Rubric (Self-Assessment)

- **Innovation** (25%): Realistic market + LDU layer is novel ✓ Stackelberg leader signal is realistic ✓
- **Technical Depth** (25%): Multi-agent dynamics ✓ Physical constraints enforced ✓ Reward function balances objectives ✓
- **Clarity** (20%): API contracts well-documented ✓ Dashboard intuitive ✓ Code modular and readable ✓
- **Demo Quality** (15%): Smooth API responses ✓ Interactive dashboard ✓ Compelling narratives ✓
- **Reproducibility** (15%): Deterministic seeding ✓ Baseline metrics provided ✓ Tests pass ✓

---

## Quick Links & Commands

```bash
# Install & Test
pip install -e .
pytest tests/ -v

# Generate Baseline Artifacts
python smartgrid_mas/train_baseline.py --episodes 50 --outdir artifacts

# Start Server
python main.py

# Manual API Test
curl -X POST http://localhost:7860/reset \
  -H 'Content-Type: application/json' \
  -d '{"task_id":"default","seed":42}' | jq .

# Docker Build & Run
docker build -t smartgrid-marketsim .
docker run -p 7860:7860 smartgrid-marketsim

# View Dashboard
open http://localhost:7860/demo
```

---

**Document Version:** 1.0  
**Last Updated:** April 2026  
**Audience:** Technical team + judges  
**Status:** Demo-ready

