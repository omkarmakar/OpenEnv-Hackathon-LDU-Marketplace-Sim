from fastapi.testclient import TestClient

from main import app


def test_api_contract_core_endpoints():
    client = TestClient(app)

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    reset = client.post("/reset", json={"task_id": "default", "seed": 7})
    assert reset.status_code == 200
    data = reset.json()
    sid = data["session_id"]

    state = client.get(f"/state?session_id={sid}")
    assert state.status_code == 200
    assert "observation" in state.json()

    obs = state.json()["observation"]
    action = {
        "action": {
            "bids": [
                {
                    "agent_id": "renewable_1",
                    "role": "renewable_prosumer",
                    "bid_type": "supply",
                    "quantity_mwh": min(obs["renewable_availability_mwh"], obs["demand_mwh"] * 0.5),
                    "price_usd_per_mwh": 22,
                },
                {
                    "agent_id": "peaker_1",
                    "role": "peaker_plant",
                    "bid_type": "supply",
                    "quantity_mwh": min(obs["peaker_capacity_mwh"], obs["demand_mwh"] * 0.5),
                    "price_usd_per_mwh": 58,
                },
                {
                    "agent_id": "industrial_1",
                    "role": "industrial_load",
                    "bid_type": "demand",
                    "quantity_mwh": obs["demand_mwh"],
                    "price_usd_per_mwh": 85,
                },
            ],
            "ev_charge_mwh": 0,
            "ev_discharge_mwh": 0,
        }
    }

    step = client.post(f"/step?session_id={sid}", json=action)
    assert step.status_code == 200
    step_j = step.json()
    assert "reward" in step_j and "info" in step_j and "observation" in step_j

    info = client.get("/info")
    assert info.status_code == 200
    assert "tasks" in info.json()

    events = client.get(f"/events?session_id={sid}")
    assert events.status_code == 200
    assert "events" in events.json()
