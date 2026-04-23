import os
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from smartgrid_mas.engine.policies import (
    adaptive_stackelberg_action,
    heuristic_joint_action,
    random_joint_action,
)
from smartgrid_mas.env import SmartGridMarketEnv
from smartgrid_mas.models import JointAction, ResetRequest, StepRequest


app = FastAPI(
    title="OpenEnv Smart Grid MarketSim",
    description="Multi-agent market simulator with LDU physical feasibility layer.",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

env = SmartGridMarketEnv()


class InferenceRequest(BaseModel):
    policy: str = "heuristic"
    personality: str = "balanced"
    task_id: str = "default"
    seed: Optional[int] = 42


@app.get("/")
def root():
    return {
        "name": "OpenEnv Smart Grid MarketSim",
        "status": "ready",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    return {"status": "ok", "service": "openenv-smartgrid-marketsim"}


@app.post("/reset")
def reset(request: ResetRequest):
    try:
        return env.reset(task_id=request.task_id, seed=request.seed)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/step")
def step(request: StepRequest, session_id: Optional[str] = Query(default=None)):
    try:
        return env.step(action=request.action, session_id=session_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/state")
def state(session_id: Optional[str] = Query(default=None)):
    try:
        return env.state(session_id=session_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/events")
def events(session_id: Optional[str] = Query(default=None)):
    try:
        return env.events(session_id=session_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/info")
def info():
    return env.get_schema()


@app.post("/run-inference")
def run_inference(request: InferenceRequest):
    reset_resp = env.reset(task_id=request.task_id, seed=request.seed)
    sid = reset_resp.session_id
    obs = reset_resp.observation

    rng = __import__("random").Random(request.seed)
    trajectory = []
    while True:
        if request.policy == "random":
            action = random_joint_action(obs, rng)
        elif request.policy == "adaptive":
            action = adaptive_stackelberg_action(obs, personality=request.personality)
        else:
            action = heuristic_joint_action(obs, personality=request.personality)

        result = env.step(action=action, session_id=sid)
        trajectory.append(
            {
                "step": len(trajectory) + 1,
                "action": action.model_dump(),
                "reward": result.reward.model_dump(),
                "info": result.info,
            }
        )
        obs = result.observation
        if result.done:
            break

    avg_reward = sum(t["reward"]["score"] for t in trajectory) / max(1, len(trajectory))
    return {
        "success": True,
        "policy": request.policy,
        "personality": request.personality,
        "steps": len(trajectory),
        "average_reward": round(avg_reward, 4),
        "trajectory": trajectory,
    }


def main() -> None:
    import uvicorn

    port = int(os.getenv("PORT", "7860"))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
