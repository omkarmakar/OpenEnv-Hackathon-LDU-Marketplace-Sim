# OpenEnv Smart Grid MarketSim

Multi-agent electricity market simulation with physical feasibility correction, reliability constraints, contingency handling, forecast uncertainty, and emissions-aware optimization.

## What Makes This Different

Most market environments score bid intent.  
This environment scores **physically delivered outcomes after dispatch correction**.

Core loop:
1. Agents submit bids and EV actions
2. Market clearing produces economic intent
3. LDU enforces physical feasibility (including reserve/ramp/startup constraints)
4. Reward is computed with reliability-first hierarchy
5. Dynamics evolve demand/renewables/price with uncertainty and contingencies

## Current Capability Snapshot

- **Market layer:** leader-signal-influenced bid clearing
- **Physical layer (LDU):**
  - SOC limits and charge/discharge consistency
  - transmission/storage losses
  - reserve requirement and reserve shortfall tracking
  - ramp-rate constraints for peaker and EV discharge
  - peaker startup cost accounting
  - emissions and carbon-cost accounting
  - frequency and line-loading consequence coupling
  - reserve commitment gate and emergency dispatch trigger path
  - peaker activation delay semantics (task-configurable)
- **Uncertainty and resilience:**
  - stochastic demand/renewable evolution
  - forecast-vs-realized channels
  - contingency events (`peaker_trip`, `transmission_derate`)
- **Reward design:** reliability-first hierarchical scoring
- **Evaluation:** policy x scenario x seed comparison artifacts for cost/blackouts/violations/emissions/reserve shortfall/stability events
- **Demo:** operator override and resilience scenario endpoint

## Scenarios

- `default`
- `long_horizon`
- `stress_shock`
- `normal`
- `outage`
- `renewable_collapse`

Each scenario contains task-specific reserve/ramp/startup/carbon/forecast/contingency settings.

Benchmark protocol labels used in reports:
- `normal` -> task `normal`
- `shock` -> task `stress_shock`
- `outage` -> task `outage`
- `renewable_collapse` -> task `renewable_collapse`

## API Endpoints

- `GET /health`
- `POST /reset`
- `POST /step`
- `POST /act`
- `GET /state`
- `GET /events`
- `GET /events/stream`
- `POST /inject-shock`
- `POST /operator-override`
- `GET /info`
- `POST /run-inference`
- `POST /run-demo-mode`
- `POST /run-resilience-demo`
- `GET /demo`

`/run-resilience-demo` now reports trajectory-level resilience deltas:
- `blackout_step_delta`
- `reserve_activation_delta`
- `emergency_dispatch_delta`
- `stability_event_delta`

## Quickstart

```powershell
pip install -e .
python main.py
```

Open:
- API docs: `http://localhost:7860/docs`
- Demo UI: `http://localhost:7860/demo`

## Evaluation Artifacts

Run baseline evaluation matrix:

```powershell
python -m smartgrid_mas.train_baseline --episodes 12 --seeds 10 --bootstrap-samples 1000 --outdir artifacts
```

Generated outputs:
- `artifacts/baseline_metrics.csv` (detailed rows)
- `artifacts/policy_comparison.csv` (aggregated metrics with mean/std)
- `artifacts/policy_comparison.md` (judge-readable table)
- `artifacts/policy_pairwise_deltas.csv` (paired deltas + bootstrap 95% CI)
- `artifacts/policy_win_rates.md` (scenario-wise win-rate table)
- `artifacts/ablation_metrics.csv` (adaptive policy under LDU ablation profiles)
- `artifacts/ablation_comparison.md` (full-vs-ablated summary table)
- `artifacts/resilience_stress_benchmark.md` (protocol + findings)
- `artifacts/reward_comparison.png` (reward curves)

## Tests

```powershell
pytest -q
```

Coverage includes:
- market + dispatch invariants
- reward bounds and consistency
- unsafe trajectory scoring lower than stable trajectory
- deterministic seeded regression

## Notes

- UI prices may be displayed in INR-equivalent for readability.
- Internal API/economics fields remain model units (`*_usd_per_mwh`) for compatibility.
- For judging walkthrough, use `JUDGES_KICKSTART.md`.
