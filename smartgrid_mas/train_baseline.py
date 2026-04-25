import argparse
import csv
import os
import random
from statistics import mean
from typing import Dict, List

import matplotlib.pyplot as plt

from smartgrid_mas.engine.policies import adaptive_stackelberg_action, heuristic_joint_action, random_joint_action
from smartgrid_mas.env import SmartGridMarketEnv
from smartgrid_mas.tasks import list_tasks


def run_episode(env: SmartGridMarketEnv, policy_name: str, task_id: str, seed: int) -> Dict[str, float]:
    reset = env.reset(task_id=task_id, seed=seed)
    sid = reset.session_id
    obs = reset.observation
    rng = random.Random(seed)
    rewards: List[float] = []
    blackout_steps = 0
    total_steps = 0
    total_unmet = 0.0
    total_corrections = 0

    while True:
        if policy_name == "random":
            action = random_joint_action(obs, rng)
        elif policy_name == "adaptive":
            action = adaptive_stackelberg_action(obs, personality="balanced")
        else:
            action = heuristic_joint_action(obs, personality="balanced")

        step = env.step(action=action, session_id=sid)
        rewards.append(step.reward.score)
        total_steps += 1
        dispatch = step.info["dispatch"]
        total_unmet += dispatch["unmet_demand_mwh"]
        total_corrections += dispatch["correction_count"]
        if dispatch["unmet_demand_mwh"] > 0.0:
            blackout_steps += 1
        obs = step.observation
        if step.done:
            summary = step.info["summary"]
            break

    return {
        "avg_reward": sum(rewards) / max(1, len(rewards)),
        "avg_cost_usd": summary["total_cost_usd"] / max(1, total_steps),
        "blackout_rate": blackout_steps / max(1, total_steps),
        "constraint_violation_rate": total_corrections / max(1, total_steps),
        "emissions_tco2": summary.get("total_emissions_tco2", 0.0),
        "unmet_energy_mwh": total_unmet,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Judge-ready baseline evaluation runner")
    parser.add_argument("--episodes", type=int, default=12)
    parser.add_argument("--seeds", type=int, default=3)
    parser.add_argument("--outdir", type=str, default="artifacts")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    env = SmartGridMarketEnv()
    policies = ["random", "heuristic", "adaptive"]
    tasks = list_tasks()
    rows = []
    reward_curves = {policy: [] for policy in policies}

    for task_id in tasks:
        for seed_idx in range(args.seeds):
            base_seed = 1000 + seed_idx * 137
            for ep in range(args.episodes):
                for policy in policies:
                    result = run_episode(
                        env=env,
                        policy_name=policy,
                        task_id=task_id,
                        seed=base_seed + ep * 11 + (0 if policy == "random" else 100 if policy == "heuristic" else 200),
                    )
                    row = {
                        "policy": policy,
                        "task_id": task_id,
                        "seed_group": seed_idx,
                        "episode": ep + 1,
                        **{k: round(v, 6) for k, v in result.items()},
                    }
                    rows.append(row)
                    if task_id == "default" and seed_idx == 0:
                        reward_curves[policy].append(result["avg_reward"])

    detailed_csv_path = os.path.join(args.outdir, "baseline_metrics.csv")
    with open(detailed_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "policy",
                "task_id",
                "seed_group",
                "episode",
                "avg_reward",
                "avg_cost_usd",
                "blackout_rate",
                "constraint_violation_rate",
                "emissions_tco2",
                "unmet_energy_mwh",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    grouped = {}
    for row in rows:
        key = (row["policy"], row["task_id"])
        grouped.setdefault(
            key,
            {k: [] for k in ["avg_reward", "avg_cost_usd", "blackout_rate", "constraint_violation_rate", "emissions_tco2"]},
        )
        for metric in grouped[key]:
            grouped[key][metric].append(float(row[metric]))

    summary_rows = []
    for (policy, task_id), metrics in grouped.items():
        summary_rows.append(
            {
                "policy": policy,
                "task_id": task_id,
                "avg_reward": round(mean(metrics["avg_reward"]), 6),
                "avg_cost_usd": round(mean(metrics["avg_cost_usd"]), 6),
                "blackout_rate": round(mean(metrics["blackout_rate"]), 6),
                "constraint_violation_rate": round(mean(metrics["constraint_violation_rate"]), 6),
                "emissions_tco2": round(mean(metrics["emissions_tco2"]), 6),
            }
        )

    policy_csv_path = os.path.join(args.outdir, "policy_comparison.csv")
    with open(policy_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "policy",
                "task_id",
                "avg_reward",
                "avg_cost_usd",
                "blackout_rate",
                "constraint_violation_rate",
                "emissions_tco2",
            ],
        )
        writer.writeheader()
        writer.writerows(summary_rows)

    policy_md_path = os.path.join(args.outdir, "policy_comparison.md")
    with open(policy_md_path, "w", encoding="utf-8") as f:
        f.write("# Policy Comparison\n\n")
        f.write("| Policy | Task | Avg Reward | Avg Cost USD | Blackout Rate | Constraint Violation Rate | Emissions tCO2 |\n")
        f.write("|---|---:|---:|---:|---:|---:|---:|\n")
        for row in sorted(summary_rows, key=lambda x: (x["task_id"], x["policy"])):
            f.write(
                f"| {row['policy']} | {row['task_id']} | {row['avg_reward']:.4f} | "
                f"{row['avg_cost_usd']:.3f} | {row['blackout_rate']:.4f} | "
                f"{row['constraint_violation_rate']:.4f} | {row['emissions_tco2']:.4f} |\n"
            )

    plt.figure(figsize=(10, 5))
    plt.plot(range(1, len(reward_curves["random"]) + 1), reward_curves["random"], label="Random baseline")
    plt.plot(range(1, len(reward_curves["heuristic"]) + 1), reward_curves["heuristic"], label="Heuristic improved")
    plt.plot(range(1, len(reward_curves["adaptive"]) + 1), reward_curves["adaptive"], label="Adaptive leader-signal")
    plt.xlabel("Episode")
    plt.ylabel("Average reward")
    plt.title("Policy Reward Curves (default task, seed group 0)")
    plt.legend()
    plt.grid(alpha=0.25)
    fig_path = os.path.join(args.outdir, "reward_comparison.png")
    plt.tight_layout()
    plt.savefig(fig_path, dpi=160)

    print(f"Saved detailed metrics CSV: {detailed_csv_path}")
    print(f"Saved policy comparison CSV: {policy_csv_path}")
    print(f"Saved policy comparison markdown: {policy_md_path}")
    print(f"Saved reward plot: {fig_path}")


if __name__ == "__main__":
    main()
