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
  - frequency and line-loading proxies
- **Uncertainty and resilience:**
  - stochastic demand/renewable evolution
  - forecast-vs-realized channels
  - contingency events (`peaker_trip`, `transmission_derate`)
- **Reward design:** reliability-first hierarchical scoring
- **Evaluation:** policy x task x seed comparison artifacts for cost/blackouts/violations/emissions
- **Demo:** operator override and resilience scenario endpoint

## Scenarios

- `default`
- `long_horizon`
- `stress_shock`

Each scenario contains task-specific reserve/ramp/startup/carbon/forecast/contingency settings.

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
python -m smartgrid_mas.train_baseline --episodes 12 --seeds 3 --outdir artifacts
```

Generated outputs:
- `artifacts/baseline_metrics.csv` (detailed rows)
- `artifacts/policy_comparison.csv` (aggregated metrics)
- `artifacts/policy_comparison.md` (judge-readable table)
- `artifacts/reward_comparison.png` (reward curves)

## Tests

```powershell
pytest -q
```

Coverage includes:
- market + dispatch invariants
- reward bounds and consistency
- deterministic seeded regression

## Notes

- UI prices may be displayed in INR-equivalent for readability.
- Internal API/economics fields remain model units (`*_usd_per_mwh`) for compatibility.
- For judging walkthrough, use `JUDGES_KICKSTART.md`.
