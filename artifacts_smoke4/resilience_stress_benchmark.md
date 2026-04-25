# Resilience Stress Benchmark

## Protocol
- Scenarios: normal, shock, outage, renewable_collapse
- Policies: random, heuristic, adaptive
- Seeds per scenario: 1
- Episodes per seed: 1
- Bootstrap samples for paired CI: 20
- Deterministic seed base: 1000 + 137 * seed_group

## Findings
- **normal**: top avg reward policy = `adaptive` (0.5773).
- **outage**: top avg reward policy = `random` (0.5575).
- **renewable_collapse**: top avg reward policy = `random` (0.5698).
- **shock**: top avg reward policy = `heuristic` (0.5683).

## Trade-off Notes
- Compare reward leadership with blackout-rate and reserve-shortfall metrics before declaring policy winners.
- Lower emissions can conflict with outage resilience under peaker constraints.
- Stability-event-rate highlights policies that appear good on cost but degrade operational robustness.
- Paired deltas and confidence intervals are available in policy_pairwise_deltas.csv and policy_win_rates.md.
- LDU ablation evidence is available in ablation_metrics.csv and ablation_comparison.md.
