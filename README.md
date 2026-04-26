---
title: OpenEnv SmartGrid MarketSim
emoji: ⚡
colorFrom: green
colorTo: blue
sdk: docker
pinned: false
---
# OpenEnv SmartGrid MarketSim

## In this market, physics has veto power.

**Power markets optimize economics. Grid operators preserve stability. Physics enforces hard limits.**
**OpenEnv SmartGrid MarketSim is a reinforcement learning environment where all three collide — and agents learn whether the grid survives.**

OpenEnv SmartGrid MarketSim is a **multi-agent reinforcement learning environment** for training reliability-aware agents in strategic electricity markets under uncertainty, contingencies, and physical constraints.

This is not a toy market simulator.

It is a **training ground for resilient infrastructure intelligence.**

Agents do not merely learn how to maximize reward.
They learn how to:

* Coordinate under conflicting incentives
* Respond to shocks and outages
* Preserve grid reliability under stress
* Optimize within physical feasibility limits
* Balance economic strategy with system resilience

---

# Why This Environment Exists

Modern power systems face a structural intelligence problem.

Markets optimize price.
Control systems optimize stability.
Operators manage emergencies.

Real grids require all three simultaneously.

Most existing learning environments isolate these challenges.
This environment combines them.

## Core Hypothesis

**If agents train in a world where economic strategy is filtered through dispatch intelligence and hard physical constraints, they can learn reliability-aware strategic behavior instead of brittle reward maximization.**

That is the problem this benchmark targets.

---

# What Makes This Environment Novel

This environment combines three interacting intelligence layers.

## 1. Strategic Multi-Agent Electricity Market

Agents participate as:

* Renewable prosumers
* Industrial load participants
* Peaker generators
* Flexible EV storage resources

Agents submit bids and interact through strategic market clearing influenced by leader price signals.

This creates a partially cooperative, partially competitive game.

---

## 2. Reliability Dispatch Control Agent

A dedicated dispatch intelligence layer observes:

* Scarcity conditions
* Forecast gaps
* Reserve risks
* Contingencies
* Renewable uncertainty

It intervenes through:

* Reserve activation
* Corrective redispatch
* Storage balancing
* Peaker adjustments
* Emergency support actions

This turns the environment into more than a market.
It becomes a reliability coordination game.

---

## 3. Physics-Constrained Safety Shield

All proposed actions pass through a safety layer enforcing:

* EV SOC bounds
* Ramp-rate constraints
* Reserve adequacy
* Frequency and line-loading proxies
* Emergency support logic
* Constraint correction and feasibility enforcement

Policies may propose.
Physics decides.

Unsafe strategies cannot exploit the environment.

---

# Environment Architecture

Each environment step executes:

1. Policy Action Selection
2. Market Clearing
3. Dispatch Control Decision
4. Physics Safety Enforcement
5. Reward Computation
6. State Evolution Under Uncertainty

This creates a closed-loop strategic learning system.

```text
Policy Actions
   ↓
Market Clearing
   ↓
Dispatch Control Agent
   ↓
Physics Safety Shield
   ↓
Reward Computation
   ↓
State Evolution
```

---

# What Agents Learn

Agents are not trained to optimize price alone.

They learn tradeoffs among:

* Reliability
* Cost efficiency
* Stability
* Reserve adequacy
* Renewable utilization
* Constraint compliance

Sometimes the profitable move loses.
The resilient move wins.

That is deliberate.

---

# Reward Design

Reward is structured as staged rubrics.

## Reliability Stage

Can the grid remain operational?

## Service Stage

Is demand satisfied?

## Optimization Stage

Is dispatch economically efficient?

## Stability Stage

Are system risks controlled?

Final rewards incorporate anti-hacking penalties for:

* Blackouts
* Constraint violations
* Reserve shortfalls
* Unsafe exploitation
* Stability failures

High-level reward structure:

```text
Reward = Reliability
       + Service
       + Optimization
       + Stability
       - Safety Penalties
```

This prevents single-metric reward hacking.
Agents must learn robust behavior.

---

# RL Training in the Environment

This environment is built not only for simulation, but for training.

Current training stack includes:

* OpenEnv interaction loop
* Hugging Face TRL
* GRPO-style reinforcement optimization
* Curriculum learning across stress scenarios
* Multi-agent policy benchmarking

Policy comparisons include:

* Random baseline
* Heuristic policies
* Adaptive policies
* Trained RL agents

Training evaluates improvement through:

* Cumulative reward growth
* Blackout reduction
* Reserve shortfall reduction
* Stability-event reduction
* Candidate vs baseline win rates

Success is defined by improved behavior inside the environment.

Not better text outputs.
Better policies.

---

# OpenEnv Themes Alignment

This environment spans multiple OpenEnv hackathon themes.

## Theme #1 — Multi-Agent Interactions

Strategic bidding, negotiation, competition and coordination.

## Theme #2 — Long-Horizon Planning

Delayed consequences, contingency response and long-horizon resilience.

## Theme #3 — World Modeling

Partial observability, tool-like control interaction, dynamic infrastructure simulation.

---

# Environment Tasks

## default

Standard strategic bidding with reliability-aware dispatch.

## long_horizon

Longer planning horizons with delayed system effects.

## stress_shock

Shock-heavy reliability stress testing.

## outage

N-1 style outage and contingency scenarios.

## renewable_collapse

Severe renewable drop and forecast error regimes.

These scenarios test both optimization and resilience.

---

# Example Observation Signals

Agents observe:

* Demand levels
* Renewable availability
* Scarcity index
* Clearing prices
* Reserve conditions
* Forecast errors
* Contingency flags
* Stability risk indicators

This supports strategic reasoning under uncertainty.

---

# Example Action Space

Joint actions include:

* Strategic supply and demand bids
* EV charge / discharge decisions
* Reserve activation
* Storage dispatch
* Corrective redispatch

Multi-agent strategy and operational control coexist.

---

# Safety Constraints Enforced

Physics shield enforces:

* No infeasible dispatch
* No simultaneous charge/discharge exploits
* Ramp limits respected
* Reserve commitments maintained
* Emergency support triggered when necessary

Learned policies cannot bypass safety.

---

# Benchmark Evidence

Evaluation artifacts include:

* Reward curves
* Policy comparisons
* Ablation results
* Resilience stress benchmarks
* Pairwise policy win-rate analysis
* Trajectory and metrics artifacts

## Example Metrics

| Metric                | Baseline | Trained Agent | Goal     |
| --------------------- | -------- | ------------- | -------- |
| Average Reward        | --       | --            | Increase |
| Blackout Rate         | --       | --            | Reduce   |
| Reserve Shortfalls    | --       | --            | Reduce   |
| Stability Events      | --       | --            | Reduce   |
| Constraint Violations | --       | --            | Reduce   |

---

# Demo Walkthrough

Recommended judge walkthrough:

## 1. Normal Market Scenario

Show strategic equilibrium and reliability telemetry.

## 2. Inject Shock

Trigger renewable collapse or contingency.

Show stress emergence.

## 3. Safety Shield Intervention

Demonstrate physics-corrected behavior.

## 4. Baseline vs Trained Agent

Show measurable improvement.

The objective is not only to show the environment runs.

It is to show learning.

---

# Why This Matters

This environment studies a broader question:

**Can intelligent agents learn strategic behavior under economic incentives while respecting hard safety constraints?**

Power systems are the domain.
Reliability-aware intelligence is the larger problem.

Potential applications:

* Smart-grid autonomy
* Infrastructure agents
* Safe multi-agent RL
* Cyber-physical agent training
* Reliability-constrained autonomous systems

---

# Repository Layout

```text
main.py
openenv.yaml
smartgrid_mas/
 ├── env.py
 ├── tasks.py
 ├── models.py
 ├── engine/
 │    ├── market.py
 │    ├── control.py
 │    ├── ldu.py
 │    ├── reward.py
 │    └── dynamics.py
tests/
artifacts/
```

---

# Quick Start

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

---

## Start Server

```bash
python main.py
```

Default endpoints:

* API: [http://localhost:7860](http://localhost:7860)
* Docs: [http://localhost:7860/docs](http://localhost:7860/docs)
* Demo: [http://localhost:7860/demo](http://localhost:7860/demo)

---

# Run Example

Reset environment:

```bash
curl -X POST http://localhost:7860/reset \
-H "Content-Type: application/json" \
-d '{"task_id":"stress_shock","seed":42}'
```

Run deterministic demo:

```bash
curl -X POST http://localhost:7860/run-demo-mode
```

Run resilience comparison:

```bash
curl -X POST http://localhost:7860/run-resilience-demo
```

---

# Training & Benchmarking

Generate deterministic artifacts:

```bash
generate-demo-artifacts
```

Run resilience benchmark:

```bash
train-baseline
```

Run tests:

```bash
pytest -q
```

---

# OpenEnv Compliance

Includes:

* OpenEnv-compatible environment interface
* reset / step / state API
* openenv.yaml metadata
* Hosted Space deployment
* RL training integration support
* Reproducible benchmark artifacts

---

# Research Framing

This project can be viewed as a benchmark for:

* Safety-shielded RL
* Reliability-aware multi-agent intelligence
* Strategic infrastructure world modeling
* Reward-hacking resistant environment design

It is not merely a simulator.

It is a trainable environment for studying resilient intelligence.

---

# Closing Thought

Most reinforcement learning environments teach agents how to optimize.

This environment asks whether agents can learn how to preserve critical systems under uncertainty.

That is the benchmark.
That is the experiment.
That is OpenEnv SmartGrid MarketSim.

