import os
import json
import time
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

from smartgrid_mas.engine.policies import (
    adaptive_stackelberg_action,
    heuristic_joint_action,
    random_joint_action,
)
from smartgrid_mas.env import SmartGridMarketEnv
from smartgrid_mas.demo_page import build_demo_html
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

DEMO_MODE_CONFIG = {
    "policy": "adaptive",
    "personality": "balanced",
    "task_id": "default",
    "seed": 42,
}


class InferenceRequest(BaseModel):
    policy: str = "heuristic"
    personality: str = "balanced"
    task_id: str = "default"
    seed: Optional[int] = 42


class ShockRequest(BaseModel):
    renewable_drop_mwh: float = 20.0


def _rollout_inference(request: InferenceRequest) -> dict:
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
        "task_id": request.task_id,
        "seed": request.seed,
        "steps": len(trajectory),
        "average_reward": round(avg_reward, 4),
        "trajectory": trajectory,
    }


@app.get("/")
def root():
    return {
        "name": "OpenEnv Smart Grid MarketSim",
        "status": "ready",
        "docs": "/docs",
        "health": "/health",
        "demo": "/demo",
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


@app.get("/events/stream")
def events_stream(session_id: Optional[str] = Query(default=None), poll_ms: int = Query(default=650, ge=150, le=5000)):
    try:
        env.state(session_id=session_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    def event_generator():
        last_len = 0
        while True:
            data = env.events(session_id=session_id)
            events_list = data.get("events", [])
            if len(events_list) > last_len:
                for item in events_list[last_len:]:
                    yield f"data: {json.dumps(item)}\n\n"
                last_len = len(events_list)
            else:
                yield ": keepalive\n\n"
            time.sleep(poll_ms / 1000.0)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/inject-shock")
def inject_shock(request: ShockRequest, session_id: Optional[str] = Query(default=None)):
    try:
        return env.inject_shock(session_id=session_id, renewable_drop_mwh=request.renewable_drop_mwh)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/demo", response_class=HTMLResponse)
def demo_page():
    return HTMLResponse(build_demo_html())


@app.get("/info")
def info():
    return env.get_schema()


@app.post("/run-inference")
def run_inference(request: InferenceRequest):
    return _rollout_inference(request)


@app.post("/run-demo-mode")
def run_demo_mode():
    request = InferenceRequest(**DEMO_MODE_CONFIG)
    result = _rollout_inference(request)
    result["mode"] = "demo"
    result["deterministic"] = True
    result["governing_claim"] = (
        "Reliable grid balancing emerges when strategic bidding is constrained by physical feasibility."
    )
    return result


def main() -> None:
    import uvicorn

    port = int(os.getenv("PORT", "7860"))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
