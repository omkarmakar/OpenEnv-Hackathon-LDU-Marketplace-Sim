# OpenEnv Smart Grid MarketSim — One-Page Reference

## The Problem We Solve
Grid balancing is **two-layer**: Market optimality ≠ Physical feasibility. Most simulators score planned strategy; we score *delivered outcomes after constraints*.

---

## Three Roles, One Goal

| **Role 1: Physics & LDU** | **Role 2: Agents & Strategy** | **Role 3: Integration & Narrative** |
|---|---|---|
| **Owns:** Constraints, losses, feasibility | **Owns:** Bidding policies, personalities | **Owns:** APIs, dashboard, story |
| **Files:** `ldu.py`, `dynamics.py`, `reward.py` | **Files:** `market.py`, `policies.py`, `tasks.py` | **Files:** `main.py`, `demo_page.py`, `env.py` |
| **Demo Talk:** "LDU corrects infeasible bids" | **Demo Talk:** "Adaptive agents learn scarcity" | **Demo Talk:** "Deterministic, reproducible results" |
| **Metric:** Corrections, delivered MWh | **Metric:** Reward per policy | **Metric:** API uptime, test pass % |

---

## System Flow (One Step)

```
┌─ Agent Bids ─────────────────────────────────────┐
│ {renewable: 50MW@$20, peaker: 30MW@$58, ...}    │
└──────────────┬──────────────────────────────────┘
               │ JointAction
               ▼
┌─ Market Clearing ──────────────────────────────┐
│ • Apply leader price signal ($50/MW)           │
│ • Match supply & demand                        │
│ • Output: 80 MW cleared @ $55                  │
└──────────────┬──────────────────────────────────┘
               │ market_result
               ▼
┌─ LDU Dispatch ──────────────────────────────────┐
│ • 80 MW = 50 renewable + 30 peaker             │
│ • -3% transmission loss                        │
│ • Check storage bounds                         │
│ • Output: 77.6 MW delivered, 2 corrections     │
└──────────────┬──────────────────────────────────┘
               │ dispatch
               ▼
┌─ Reward ───────────────────────────────────────┐
│ 0.34×satisfaction + 0.23×cost + ...            │
│ - 0.2×infeasibility - 0.2×blackout            │
│ → Score: 0.68                                  │
└──────────────┬──────────────────────────────────┘
               │ MarketReward
               ▼
        Next Observation
      (for agent's next bid)
```

---

## Key Numbers (Baseline Results)

```
Policy          Episodes    Avg Reward    Notes
────────────────────────────────────────────────
Random          50          0.347         Baseline
Heuristic       50          0.524         Rule-based
Adaptive        50          0.628         Learns scarcity
```

→ **Interpretation:** Adaptive agent learns market dynamics 81% better than random.

---

## Reward Decomposition (Example Step)

```
Demand: 120 MWh
Delivered: 115 MWh (3% transmission loss)
Unmet: 5 MWh
Clearing Price: $52/MW
Corrections: 1 (simultaneous charge+discharge)

Score Calculation:
  Satisfaction:  115/120 = 0.958 × 0.34 = 0.326
  Cost Eff.:     1 - (115×52/12000) = 0.499 × 0.23 = 0.115
  Renewables:    0.60 × 0.18 = 0.108
  Stability:     0.95 × 0.15 = 0.142
  Penalties:     -0.2×0.15 - 0.2×0.04 = -0.038
  ────────────────────────────────────────
  Raw Score:     0.653 → Clamped to [0,1] = 0.653
```

---

## Three Scenarios for Demo

| Scenario | Duration | Difficulty | What It Shows |
|----------|----------|------------|---------------|
| **Default** | 24 steps | Medium | Balanced grid; steady market dynamics |
| **Long Horizon** | 48 steps | Hard | Multi-step planning; storage foresight |
| **Stress Shock** | 30 steps | Very Hard | Early shock (-35 MW); emergency response |

Each tests a different aspect of agent adaptability.

---

## Event Log Examples

```
Step 0:    RESET: default task, seed=42
Step 1:    Market cleared: 80 MWh @ $52/MWh
Step 1:    LDU dispatch: 77.6 MWh delivered (3% loss)
Step 5:    LDU correction: EV discharge exceeded SOC
Step 10:   SHOCK INJECTED: -22 MWh renewable
Step 10:   Scarcity index jumped: 0.18 → 0.42
Step 11:   Market cleared: 95 MWh @ $68/MWh (high scarcity)
Step 15:   Episode done: avg_reward=0.58, total_cost=$8,920
```

→ **Why show logs?** Proves transparency—agents and judges can audit every decision.

---

## 5-Minute Demo Checklist

- [ ] Server running: `python main.py` (http://localhost:7860)
- [ ] Tests passing: `pytest tests/ -v` (≥12 tests)
- [ ] Baseline artifacts: `artifacts/baseline_metrics.csv`, `*.png`
- [ ] Dashboard loads: Open `/demo`, click Reset
- [ ] Manual API call works: `curl /reset` → JSON response
- [ ] Shock injection works: `/inject-shock` endpoint responds
- [ ] Event log populated: Events visible in dashboard

---

## Docker Quick Deploy

```bash
docker build -t smartgrid-sim .
docker run -p 7860:7860 smartgrid-sim
# Open browser → localhost:7860/demo
```

---

## Judge Questions → Quick Answers

| Q | A |
|---|---|
| **Can agents cheat?** | No. LDU enforces hard physical constraints; corrections are unavoidable. |
| **Realistic physics?** | Simplified but sound. 3% transmission loss, 8% storage loss, capacity limits. Standard assumptions. |
| **Training time?** | Baseline: 10s/50 episodes. RL agents: 2–24h depending on algo & hardware. |
| **Extensible?** | Yes. Add new tasks, constraints, objectives, or agent types easily. |
| **Deployment?** | FastAPI → Cloud ready. Docker, Kubernetes, HF Spaces all supported. |

---

## File Map (For Digging Deeper)

```
Core Physics        → engine/ldu.py, engine/reward.py
Market Mechanism    → engine/market.py
Agent Policies      → engine/policies.py
Task Definitions    → tasks.py
API & Orchestration → main.py, env.py
Visualization       → demo_page.py
Validation          → tests/
Training            → train_baseline.py
```

→ See **TEAM_DOCUMENTATION.md** for deep dives on each.

---

## Success Criteria (Judges Will Check)

✅ **Innovation** — Market + LDU dual layer is novel  
✅ **Technical Depth** — Multi-objective reward, Stackelberg market, realistic constraints  
✅ **Code Quality** — Modular, tested, documented  
✅ **Demo Polish** — Smooth API, responsive UI, clear narrative  
✅ **Reproducibility** — Deterministic seeding, test suite passes  

---

## Next Phase (Post-Hackathon)

1. **Train LLM agents** via TRL/Unsloth (Llama, Mistral)
2. **Add stability constraints** (frequency, voltage)
3. **Multi-agent communication** (broadcast bids, negotiation)
4. **Real market data integration** (CAISO, ERCOT)
5. **Hardware-in-the-loop** (real PLC firmware testing)

---

**Print This + JUDGES_KICKSTART.md for faster onboarding!**

