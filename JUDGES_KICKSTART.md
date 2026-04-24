# OpenEnv Smart Grid MarketSim — Judges Quick-Start

**Goal:** See the full system in action with minimal setup.

---

## 5-Minute Demo (No Installation)

### Live URL
→ Deployed at: `https://huggingface.co/spaces/openenv/smartgrid-marketsim` *(update with actual HF Space URL)*

**Just open the link, click "Reset", watch metrics update, inject a shock!**

---

## Local Demo Setup (10 minutes)

**Prerequisites:** Python 3.10+, git

### Step 1: Clone & Install (2 min)
```bash
git clone https://github.com/omkarmakar/OpenEnv-SmartGrid-MarketSim.git
cd OpenEnv-SmartGrid-MarketSim
pip install -e .
```

### Step 2: Validate System (2 min)
```bash
# Run quick tests
pytest tests/test_api_contract.py -v
# Expected: ✓ All tests pass
```

### Step 3: Generate Baseline Results (3 min)
```bash
python smartgrid_mas/train_baseline.py --episodes 50 --outdir artifacts
# Outputs: baseline_metrics.csv, reward_comparison.png
cat artifacts/baseline_metrics.csv  # Shows policy performance
```

### Step 4: Start Server (2 min)
```bash
python main.py
# Wait for: "Application startup complete"
```

### Step 5: Open Interactive Dashboard (1 min)
Open browser → `http://localhost:7860/demo`

---

## 7-Minute Judge Walkthrough

### **Segment 1: Problem Statement (1 min)**
Show this image/diagram:
```
Traditional Grid Simulator:
  Agents bid → Market clears → Score awarded ✓
  
Our Simulator:
  Agents bid → Market clears → LDU enforces feasibility → Score awarded ✓
                              (↑ This gap is crucial)
```

**Key Message:** "We measure *delivered outcomes*, not just plans. Physically-infeasible bids get corrected and penalized."

---

### **Segment 2: Architecture (1.5 min)**

Show this flow (live or slide):
```
Agent Action (bids)
    ↓
Market Clearing [leader price signal applied]
    ↓ (market_result)
LDU Dispatch [feasibility enforcement, loss calculations]
    ↓ (feasible dispatch + corrections)
Grid Dynamics [evolve demand, renewable, price]
    ↓
Reward Function [multi-objective: satisfaction + cost + renewables - penalties]
    ↓
Observation (for next step)
```

**Explain:**
- Market: Strategic bidding with Stackelberg leader signal
- LDU: Physical constraints (capacity, losses, storage bounds)
- Reward: 0.34×satisfaction + 0.23×cost + 0.18×renewable - penalties

---

### **Segment 3: Interactive Demo (3 min)**

**Open `/demo` → Do this:**

1. **(0:00)** Reset with default task
   - Narrate: "Demand 120 MWh, renewable 70 MWh, peaker capacity 85 MWh"
   - Show observation: demand, renewable_availability, last_clearing_price

2. **(0:30)** Click "Play" (auto-steps for 10 steps)
   - Watch metrics update in real-time
   - Point out: "Reward fluctuates as supply/demand balance shifts"

3. **(1:30)** Click "Inject Shock"
   - Shows: renewable suddenly drops -20 MWh
   - Point out: "Agent adapts—higher peaker bid, increased EV discharge"

4. **(2:30)** Navigate to "stress_shock" task
   - Narrate: "Harder scenario—demand spikes, renewable collapses at step 12"
   - Click "Play" → watch agent handle crisis
   - Point out: "Adaptive policy prevents blackout despite stress"

---

### **Segment 4: Results & Baselines (1.5 min)**

**Show this chart** (from `artifacts/reward_comparison.png`):
```
Reward (0–1)
     1.0 ┤                     adaptive ~~~
     0.8 ┤                       /~~/
     0.6 ┤        heuristic ___/
     0.4 ┤   random ___/
     0.2 ┤ /~~/
       0 ┴────────────────────────
         1  5  10  15  20  25  30
                     Episode
```

**Narrate:**
- "Random policy: ~0.35 (baseline)"
- "Heuristic policy: ~0.52 (rule-based strategy)"
- "Adaptive policy: ~0.63 (learns market dynamics)"
- "Graph shows deterministic reproducibility (seed=42)"

---

### **Segment 5: Closing (1 min)**

**Key Takeaways:**

1. ✅ **Realistic:** Physical constraints matter. Market-optimal ≠ physically-feasible.
2. ✅ **Multi-Agent:** 4 agent personalities (greedy, balanced, risk-averse, etc.) → rich dynamics.
3. ✅ **Learnable:** Agents progressively improve as they anticipate feasibility & scarcity.
4. ✅ **Production-Ready:** FastAPI, Docker-ready, full API contract tested.

**Next Steps (if funded):**
- Train LLM agents (Llama, Mistral) via TRL/Unsloth
- Add voltage/frequency stability constraints
- Deploy to Hugging Face Spaces
- Integrate with robotics gym for hardware-in-the-loop

---

## Key Files to Reference

| File | Role | Purpose |
|------|------|---------|
| [TEAM_DOCUMENTATION.md](TEAM_DOCUMENTATION.md) | All | 📖 Deep-dive technical guide (30 min read) |
| [main.py](main.py) | Integration | FastAPI server (all endpoints) |
| [smartgrid_mas/env.py](smartgrid_mas/env.py) | Core | Environment orchestration |
| [smartgrid_mas/engine/ldu.py](smartgrid_mas/engine/ldu.py) | Physics | Physical feasibility enforcement |
| [smartgrid_mas/engine/market.py](smartgrid_mas/engine/market.py) | Market | Market clearing + Stackelberg signal |
| [smartgrid_mas/engine/policies.py](smartgrid_mas/engine/policies.py) | Agents | Baseline strategies (random, heuristic, adaptive) |
| [smartgrid_mas/demo_page.py](smartgrid_mas/demo_page.py) | Viz | Interactive 3D dashboard |
| [tests/](tests/) | Validation | Full test suite (run with `pytest`) |

---

## Troubleshooting

### "Port 7860 already in use"
```bash
# Kill existing process
lsof -i :7860 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Or use different port
python main.py --port 8080
```

### "Dashboard not loading"
```bash
# Check server health
curl http://localhost:7860/health

# View raw HTML
curl http://localhost:7860/demo | head -100
```

### "Baseline artifacts missing"
```bash
# Generate quickly (takes ~30s)
python smartgrid_mas/train_baseline.py --episodes 10 --outdir artifacts
```

### "Tests failing"
```bash
# Install dev dependencies
pip install -e ".[dev]"

# Re-run
pytest tests/ -v --tb=short
```

---

## Questions Judges Might Ask

**Q: Is this realistic to real grid operations?**  
A: Simplified but structurally sound. Real grids have voltage/frequency stability, transmission constraints, and dispatch coordination—all modelable here. This is a training ground.

**Q: Can agents "cheat" by learning to game the reward?**  
A: No. The LDU enforces hard physical constraints (capacity, losses). Infeasible bids are corrected regardless of learned policy.

**Q: What's the training time for RL agents?**  
A: 50 baseline episodes = 10 seconds. RL training (e.g., PPO) would take 1–24 hours depending on model size and hardware. LLM fine-tuning via TRL: 2–8 hours.

**Q: Can you integrate real market data?**  
A: Yes. Replace task configs with historical CAISO/ERCOT data. Demand/price patterns already modeled stochastically.

**Q: Multi-agent coordination?**  
A: Currently agents are symmetric within roles. Could add communication layer (e.g., broadcast bids early). See RFC 005 in main OpenEnv repo.

---

## API Reference (Quick)

### Reset Environment
```bash
curl -X POST http://localhost:7860/reset \
  -H 'Content-Type: application/json' \
  -d '{"task_id":"default","seed":42}'
```

### Execute One Step
```bash
curl -X POST http://localhost:7860/step?session_id=<uuid> \
  -H 'Content-Type: application/json' \
  -d '{
    "action": {
      "bids": [
        {"agent_id":"renewable_1","role":"renewable_prosumer","bid_type":"supply","quantity_mwh":50,"price_usd_per_mwh":20},
        {"agent_id":"peaker_1","role":"peaker_plant","bid_type":"supply","quantity_mwh":30,"price_usd_per_mwh":58},
        {"agent_id":"industrial_1","role":"industrial_load","bid_type":"demand","quantity_mwh":80,"price_usd_per_mwh":85}
      ],
      "ev_charge_mwh":3.0,
      "ev_discharge_mwh":0.0
    }
  }'
```

### Query State (no step)
```bash
curl http://localhost:7860/state?session_id=<uuid>
```

### Get Events
```bash
curl http://localhost:7860/events?session_id=<uuid> | jq .
```

### Inject Grid Shock
```bash
curl -X POST http://localhost:7860/inject-shock?session_id=<uuid> \
  -H 'Content-Type: application/json' \
  -d '{"renewable_drop_mwh":20}'
```

---

## What Judges See on Deployment

✅ **Scalability:** Server handles multiple concurrent sessions (in-memory sessions dict)  
✅ **Determinism:** Seeded RNG ensures reproducible episodes for validation  
✅ **Extensibility:** Modular design (can add new tasks, policies, constraints)  
✅ **Transparency:** Event log shows every market clearing, LDU correction, shock  
✅ **Usability:** Web dashboard + REST API + Python SDK  

---

**Version:** 1.0  
**Last Updated:** April 2026  
**Status:** Demo-Ready for Judges  

**Questions?** See [TEAM_DOCUMENTATION.md](TEAM_DOCUMENTATION.md) or `pytest tests/` for validation.

