# OpenEnv Smart Grid MarketSim

Hybrid hackathon submission aligned to:
- Theme 1: Multi-Agent Interactions
- Theme 2: Long-Horizon Planning
- Theme 3.1: Professional World Modeling

## 1) Problem

LLM agents can optimize symbolic bids but still fail when actions must obey physical grid constraints.
This environment closes that gap by forcing economic strategy through a physical dispatch layer.

## 2) Environment

Pipeline:
1. Multi-agent bid submission (supply and demand)
2. Stackelberg-influenced market clearing
3. Load Dispatching Unit (LDU) feasibility correction
4. Grid dynamics evolution with volatility and shocks
5. Reward computed on physically delivered outcomes

Key mechanics:
- Agent personalities and partially private state views
- Leader price signal influencing market behavior
- Physical constraints: capacity, SOC, losses, correction logs
- Fixed loss model in baseline: 3% transmission + 8% storage loss
- Long-horizon and stress-shock scenarios

## 3) Why This Is Novel

Most market simulations score planned strategy only.
This simulator scores consequences after physical feasibility correction, creating a measurable strategy-vs-reality tension.

## 4) Implemented Features

- Restored baseline simulator flow (market clearing -> LDU correction -> reward -> dynamics)
- Core simulator, API, packaging, and baseline artifact generation
- Interactive immersive demo route at `/demo` with:
  - pseudo-3D multi-agent scene
  - play/pause/step/speed controls
  - shock injection control
  - synchronized metrics timeline
- Live event APIs:
  - `GET /events`
  - `GET /events/stream` (SSE)
  - `POST /inject-shock`
- Multi-scenario tasks:
  - `default`
  - `long_horizon`
  - `stress_shock`

## 5) API Contract

- `GET /health`
- `POST /reset`
- `POST /step`
- `POST /act`
- `GET /state`
- `GET /events`
- `GET /events/stream`
- `POST /inject-shock`
- `GET /info`
- `POST /run-inference`
- `POST /run-demo-mode`
- `GET /demo`

## 6) Quickstart

### Local run

```powershell
pip install -e .
python main.py
```

### Optional extras

```powershell
pip install -e .[openenv]
pip install -e .[dev]
```

### Baseline and improved policy artifacts

```powershell
python -m smartgrid_mas.train_baseline --episodes 30 --outdir artifacts
```

Outputs:
- [artifacts/baseline_metrics.csv](artifacts/baseline_metrics.csv)
- [artifacts/reward_comparison.png](artifacts/reward_comparison.png)

### Docker

```powershell
docker build -t openenv-smartgrid-marketsim .
docker run -p 7860:7860 openenv-smartgrid-marketsim
```

## 7) Training Notebook (Phase 3)

Colab-ready notebook:
- [training/Colab_Unsloth_HF_TRL_Training.ipynb](training/Colab_Unsloth_HF_TRL_Training.ipynb)

Notebook covers:
- endpoint-connected rollouts
- baseline vs adaptive comparisons
- Unsloth/HF TRL fine-tuning scaffold

## 8) Results and Evidence

Current evidence artifacts:
- reward curve plot
- per-episode metric CSV
- deterministic regression + API contract tests

Recommended additions before final judging:
- trained policy checkpoints
- multi-run mean/std plots
- ablation (without leader signal / without LDU correction)

## 9) HF Space and Public Artifacts

Replace placeholders before final submission:
- HF Space URL: `https://huggingface.co/spaces/YOUR_ORG/openenv-smartgrid-marketsim`
- Mini-blog URL: `https://huggingface.co/blog/YOUR_POST`
- Demo video URL (<2 min): `https://youtube.com/watch?v=YOUR_VIDEO`
- Slides URL: `https://docs.google.com/presentation/d/YOUR_DECK`

## 10) Reproducibility Checklist

1. Install dependencies and run server.
2. Run baseline artifact script.
3. Open `/demo` and run controlled scenario with shock injection.
4. Run tests and include pass output in PR/submission notes.

## 11) Tests (Phase 4)

```powershell
pytest -q
```

Test coverage includes:
- market clearing correctness and leader signal behavior
- LDU correction invariants
- reward bound and consistency checks
- deterministic seeded regression
- API contract checks for core endpoints
- deterministic demo mode regression (`/run-demo-mode`)

Notes:
- Dashboard prices are shown in INR-equivalent for readability.
- Internal market fields remain model units (`*_usd_per_mwh`) for API compatibility.

## 12) Submission Notes

- Keep media external by URL (no large video binaries in repo)
- Ensure HF Space URL is present and public
- Freeze final commit before deadline
- README reflects current restored baseline state after local git restore
