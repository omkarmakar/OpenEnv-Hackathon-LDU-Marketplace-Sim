# OpenEnv Smart Grid MarketSim — Judges Quick-Start

## 5-Minute Setup

```bash
pip install -e .
python main.py
```

Open:
- Demo: `http://localhost:7860/demo`
- API Docs: `http://localhost:7860/docs`

## 90-Second Project Framing

Use this line first:

> We score grid control outcomes after physical feasibility correction, not just market bid intent.

Architecture phrase set:
- reliability-aware dispatch
- physically grounded market learning
- safety-constrained RL environment
- resilient grid control under uncertainty

## 6-Minute Demo Script

1) **Reset deterministic run**
- Task: `stress_shock`
- Policy: `adaptive`
- Seed: `42`

2) **Show operational realism**
- Step or play for a few timesteps
- Point out backend reliability signals in outputs:
  - reserve requirement/shortfall
  - ramp violations
  - startup cost
  - emissions and carbon-cost impact
  - frequency proxy and line-loading proxy

3) **Trigger stress behavior**
- Use shock injection (`/inject-shock`) or run through contingency step
- Explain that contingencies and forecast error channels are part of dynamics, not just UI.

4) **Show operator intervention**
- Toggle override in UI (or call `/operator-override`)
- Explain this compares autonomous policy vs human override control mode.

5) **Show resilience story**
- Call `/run-resilience-demo`
- Highlight `catastrophic_failure_prevented` and blackout-step comparison.

6) **Show benchmark evidence**
- Present:
  - `artifacts/policy_comparison.csv`
  - `artifacts/policy_comparison.md`
  - `artifacts/reward_comparison.png`
- Mention metrics: cost, blackout rate, constraint violations, emissions, reward.

## API Calls You Can Run Live

Reset:
```bash
curl -X POST http://localhost:7860/reset -H "Content-Type: application/json" -d "{\"task_id\":\"stress_shock\",\"seed\":42}"
```

Run inference:
```bash
curl -X POST http://localhost:7860/run-inference -H "Content-Type: application/json" -d "{\"policy\":\"adaptive\",\"personality\":\"balanced\",\"task_id\":\"stress_shock\",\"seed\":42}"
```

Operator override:
```bash
curl -X POST "http://localhost:7860/operator-override?session_id=<session_id>" -H "Content-Type: application/json" -d "{\"enabled\":true}"
```

Resilience demo:
```bash
curl -X POST http://localhost:7860/run-resilience-demo -H "Content-Type: application/json" -d "{\"task_id\":\"stress_shock\",\"seed\":314,\"baseline_policy\":\"random\",\"candidate_policy\":\"adaptive\"}"
```

## Judge Q&A (Short Answers)

- **How is this different from toy market simulators?**  
  We enforce physical feasibility and score delivered outcomes after correction.

- **How do you prevent reward hacking?**  
  Reliability-dominant reward staging and explicit anti-hacking penalties reduce gains from unsafe behavior.

- **Is this only visual polish?**  
  No. Reliability, contingency, uncertainty, startup, reserve, and emissions are computed in backend engine paths.

- **Where is the evidence?**  
  In exported cross-policy artifacts (`policy_comparison.csv`/`.md`) across tasks and seeds.

## What To Avoid Saying

- Do not claim full AC OPF or full unit commitment.
- Do not overstate Stackelberg formalism unless providing mathematical proof.
- Prefer: “leader-signal-influenced bidding.”

## Validation Before Judges Arrive

```bash
pytest -q
python -m smartgrid_mas.train_baseline --episodes 12 --seeds 3 --outdir artifacts
```

