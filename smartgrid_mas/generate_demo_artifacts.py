import argparse
import csv
import json
import os
import random
from typing import Dict, List

from smartgrid_mas.engine.policies import (
    adaptive_stackelberg_action,
    heuristic_joint_action,
    random_joint_action,
)
from smartgrid_mas.env import SmartGridMarketEnv


def _select_action(policy: str, obs, rng: random.Random, personality: str):
    if policy == "random":
        return random_joint_action(obs, rng)
    if policy == "adaptive":
        return adaptive_stackelberg_action(obs, personality=personality)
    return heuristic_joint_action(obs, personality=personality)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic demo artifacts")
    parser.add_argument("--outdir", type=str, default="artifacts")
    parser.add_argument("--task-id", type=str, default="default")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--policy", type=str, default="adaptive", choices=["random", "heuristic", "adaptive"])
    parser.add_argument(
        "--personality",
        type=str,
        default="balanced",
        choices=["balanced", "risk_averse", "opportunistic", "greedy"],
    )
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    env = SmartGridMarketEnv()
    reset = env.reset(task_id=args.task_id, seed=args.seed)
    sid = reset.session_id
    obs = reset.observation
    rng = random.Random(args.seed)

    trajectory: List[Dict] = []
    metrics_rows: List[List] = []

    while True:
        action = _select_action(args.policy, obs, rng, args.personality)
        result = env.step(action=action, session_id=sid)

        dispatch = result.info["dispatch"]
        market = result.info["market"]

        trajectory.append(
            {
                "step": len(trajectory) + 1,
                "action": action.model_dump(),
                "reward": result.reward.model_dump(),
                "observation": result.observation.model_dump(),
                "info": result.info,
            }
        )

        metrics_rows.append(
            [
                len(trajectory),
                round(result.reward.score, 6),
                dispatch["delivered_supply_mwh"],
                dispatch["unmet_demand_mwh"],
                market["clearing_price"],
                dispatch["correction_count"],
                result.observation.scarcity_index,
                result.observation.demand_mwh,
                result.observation.renewable_availability_mwh,
            ]
        )

        obs = result.observation
        if result.done:
            break

    avg_reward = sum(item["reward"]["score"] for item in trajectory) / max(1, len(trajectory))
    summary = {
        "mode": "demo",
        "deterministic": True,
        "task_id": args.task_id,
        "seed": args.seed,
        "policy": args.policy,
        "personality": args.personality,
        "steps": len(trajectory),
        "average_reward": round(avg_reward, 6),
        "governing_claim": "Reliable grid balancing emerges when strategic bidding is constrained by physical feasibility.",
    }

    stem = f"demo_{args.task_id}_{args.policy}_seed{args.seed}"
    trajectory_path = os.path.join(args.outdir, f"{stem}_trajectory.json")
    summary_path = os.path.join(args.outdir, f"{stem}_summary.json")
    metrics_path = os.path.join(args.outdir, f"{stem}_metrics.csv")

    with open(trajectory_path, "w", encoding="utf-8") as f:
        json.dump(trajectory, f, indent=2)

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    with open(metrics_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "step",
                "reward_score",
                "delivered_supply_mwh",
                "unmet_demand_mwh",
                "clearing_price",
                "ldu_corrections",
                "scarcity_index",
                "next_demand_mwh",
                "next_renewable_mwh",
            ]
        )
        writer.writerows(metrics_rows)

    print(f"Saved trajectory: {trajectory_path}")
    print(f"Saved summary: {summary_path}")
    print(f"Saved metrics: {metrics_path}")


if __name__ == "__main__":
    main()
