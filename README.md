# OpenEnv Smart Grid MarketSim

A new OpenEnv-compatible project for a hybrid hackathon narrative:
- Theme 1: Multi-agent interactions
- Theme 2: Long-horizon planning
- Theme 3.1: Professional world modeling

## Core idea

The simulator is intentionally multi-layered:
1. Agents submit strategic market bids.
2. A market-clearing engine computes tentative allocations and prices.
3. A Load Dispatching Unit (LDU) enforces physical feasibility.
4. Grid dynamics evolve with volatility and shock events.
5. Reward is computed from physically delivered outcomes.

This creates tension between strategy and reality, which is the main differentiator.

## What is implemented in this first slice

- Multi-agent bid object with supply/demand bids.
- Market clearing with matched quantities and clearing price.
- Stackelberg-style leader price signal that reshapes bid books before clearing.
- LDU feasibility corrections:
  - power balance accounting
  - EV storage constraints
  - transmission/storage losses
  - infeasibility correction logs
- Long-horizon episode flow with shock event support.
- Personality-aware strategy behavior (greedy, risk-averse, balanced, opportunistic).
- Per-agent private view metrics in step/event outputs for richer multi-actor analysis.
- Reward decomposition including infeasibility and blackout penalties.
- REST API:
  - GET /health
  - POST /reset
  - POST /step
  - GET /state
  - GET /events
  - GET /info
  - POST /run-inference
- Baseline metric generation script with reward plot output.

## Quickstart

### Local run

```powershell
pip install -e .
python main.py
```

Server starts on port 7860.

If you also want the OpenEnv framework package locally:

```powershell
pip install -e .[openenv]
```

### Baseline metrics and plot

```powershell
python -m smartgrid_mas.train_baseline --episodes 30 --outdir artifacts
```

Outputs:
- artifacts/baseline_metrics.csv
- artifacts/reward_comparison.png

Alternative (after editable install):

```powershell
train-baseline --episodes 30 --outdir artifacts
```

### Inference policy modes

The `/run-inference` endpoint supports:
- `random`
- `heuristic`
- `adaptive` (Stackelberg-aware)

You can also pass `personality` such as `balanced`, `risk_averse`, or `opportunistic`.

### Docker

```powershell
docker build -t openenv-smartgrid-marketsim .
docker run -p 7860:7860 openenv-smartgrid-marketsim
```

## Next implementation milestones

1. Add interactive 3D frontend scene synchronized to /events stream.
2. Add Unsloth or HF TRL Colab training notebook with real policy updates.
3. Add full judging artifact checklist in README (HF Space link, mini-blog/video, plots).
