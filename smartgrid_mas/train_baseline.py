import argparse
import csv
import os
import random
from statistics import mean
from typing import Dict, List

import matplotlib.pyplot as plt

from smartgrid_mas.engine.policies import adaptive_stackelberg_action, heuristic_joint_action, random_joint_action
from smartgrid_mas.env import SmartGridMarketEnv
BENCHMARK_SCENARIOS = {
    "normal": "normal",
    "shock": "stress_shock",
    "outage": "outage",
    "renewable_collapse": "renewable_collapse",
}


def _std(values: List[float]) -> float:
    if len(values) <= 1:
        return 0.0
    mu = mean(values)
    return (sum((v - mu) ** 2 for v in values) / (len(values) - 1)) ** 0.5


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
    reserve_shortfall_steps = 0
    stability_events = 0

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
        if dispatch.get("reserve_shortfall_mwh", 0.0) > 0.0:
            reserve_shortfall_steps += 1
        if dispatch.get("stability_risk_index", 0.0) >= 0.45:
            stability_events += 1
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
        "reserve_shortfall_rate": reserve_shortfall_steps / max(1, total_steps),
        "stability_event_rate": stability_events / max(1, total_steps),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Resilience Stress Benchmark runner")
    parser.add_argument("--episodes", type=int, default=12)
    parser.add_argument("--seeds", type=int, default=3)
    parser.add_argument("--outdir", type=str, default="artifacts")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    env = SmartGridMarketEnv()
    policies = ["random", "heuristic", "adaptive"]
    tasks = BENCHMARK_SCENARIOS
    rows = []
    reward_curves = {policy: [] for policy in policies}

    for scenario_name, task_id in tasks.items():
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
                        "scenario": scenario_name,
                        "task_id": task_id,
                        "seed_group": seed_idx,
                        "episode": ep + 1,
                        **{k: round(v, 6) for k, v in result.items()},
                    }
                    rows.append(row)
                    if scenario_name == "normal" and seed_idx == 0:
                        reward_curves[policy].append(result["avg_reward"])

    detailed_csv_path = os.path.join(args.outdir, "baseline_metrics.csv")
    with open(detailed_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "policy",
                "scenario",
                "task_id",
                "seed_group",
                "episode",
                "avg_reward",
                "avg_cost_usd",
                "blackout_rate",
                "constraint_violation_rate",
                "emissions_tco2",
                "unmet_energy_mwh",
                "reserve_shortfall_rate",
                "stability_event_rate",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    grouped = {}
    for row in rows:
        key = (row["policy"], row["scenario"], row["task_id"])
        grouped.setdefault(
            key,
            {
                k: []
                for k in [
                    "avg_reward",
                    "avg_cost_usd",
                    "blackout_rate",
                    "constraint_violation_rate",
                    "emissions_tco2",
                    "reserve_shortfall_rate",
                    "stability_event_rate",
                ]
            },
        )
        for metric in grouped[key]:
            grouped[key][metric].append(float(row[metric]))

    summary_rows = []
    for (policy, scenario, task_id), metrics in grouped.items():
        summary_rows.append(
            {
                "policy": policy,
                "scenario": scenario,
                "task_id": task_id,
                "avg_reward": round(mean(metrics["avg_reward"]), 6),
                "avg_reward_std": round(_std(metrics["avg_reward"]), 6),
                "avg_cost_usd": round(mean(metrics["avg_cost_usd"]), 6),
                "avg_cost_usd_std": round(_std(metrics["avg_cost_usd"]), 6),
                "blackout_rate": round(mean(metrics["blackout_rate"]), 6),
                "blackout_rate_std": round(_std(metrics["blackout_rate"]), 6),
                "constraint_violation_rate": round(mean(metrics["constraint_violation_rate"]), 6),
                "constraint_violation_rate_std": round(_std(metrics["constraint_violation_rate"]), 6),
                "emissions_tco2": round(mean(metrics["emissions_tco2"]), 6),
                "emissions_tco2_std": round(_std(metrics["emissions_tco2"]), 6),
                "reserve_shortfall_rate": round(mean(metrics["reserve_shortfall_rate"]), 6),
                "reserve_shortfall_rate_std": round(_std(metrics["reserve_shortfall_rate"]), 6),
                "stability_event_rate": round(mean(metrics["stability_event_rate"]), 6),
                "stability_event_rate_std": round(_std(metrics["stability_event_rate"]), 6),
            }
        )

    policy_csv_path = os.path.join(args.outdir, "policy_comparison.csv")
    with open(policy_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "policy",
                "scenario",
                "task_id",
                "avg_reward",
                "avg_reward_std",
                "avg_cost_usd",
                "avg_cost_usd_std",
                "blackout_rate",
                "blackout_rate_std",
                "constraint_violation_rate",
                "constraint_violation_rate_std",
                "emissions_tco2",
                "emissions_tco2_std",
                "reserve_shortfall_rate",
                "reserve_shortfall_rate_std",
                "stability_event_rate",
                "stability_event_rate_std",
            ],
        )
        writer.writeheader()
        writer.writerows(summary_rows)

    policy_md_path = os.path.join(args.outdir, "policy_comparison.md")
    with open(policy_md_path, "w", encoding="utf-8") as f:
        f.write("# Policy Comparison\n\n")
        f.write("| Policy | Scenario | Task | Avg Reward | Avg Cost USD | Blackout Rate | Constraint Violation Rate | Emissions tCO2 | Reserve Shortfall Rate | Stability Event Rate |\n")
        f.write("|---|---|---|---:|---:|---:|---:|---:|---:|---:|\n")
        for row in sorted(summary_rows, key=lambda x: (x["scenario"], x["policy"])):
            f.write(
                f"| {row['policy']} | {row['scenario']} | {row['task_id']} | {row['avg_reward']:.4f} | "
                f"{row['avg_cost_usd']:.3f} | {row['blackout_rate']:.4f} | "
                f"{row['constraint_violation_rate']:.4f} | {row['emissions_tco2']:.4f} | "
                f"{row['reserve_shortfall_rate']:.4f} | {row['stability_event_rate']:.4f} |\n"
            )

    report_path = os.path.join(args.outdir, "resilience_stress_benchmark.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Resilience Stress Benchmark\n\n")
        f.write("## Protocol\n")
        f.write(f"- Scenarios: {', '.join(BENCHMARK_SCENARIOS.keys())}\n")
        f.write(f"- Policies: {', '.join(policies)}\n")
        f.write(f"- Seeds per scenario: {args.seeds}\n")
        f.write(f"- Episodes per seed: {args.episodes}\n")
        f.write("- Deterministic seed base: 1000 + 137 * seed_group\n\n")
        f.write("## Findings\n")
        best = sorted(summary_rows, key=lambda x: (x["scenario"], -x["avg_reward"]))
        current_scenario = None
        for row in best:
            if row["scenario"] != current_scenario:
                current_scenario = row["scenario"]
                f.write(f"- **{current_scenario}**: top avg reward policy = `{row['policy']}` ({row['avg_reward']:.4f}).\n")
        f.write("\n")
        f.write("## Trade-off Notes\n")
        f.write("- Compare reward leadership with blackout-rate and reserve-shortfall metrics before declaring policy winners.\n")
        f.write("- Lower emissions can conflict with outage resilience under peaker constraints.\n")
        f.write("- Stability-event-rate highlights policies that appear good on cost but degrade operational robustness.\n")

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
    print(f"Saved resilience benchmark markdown: {report_path}")
    print(f"Saved reward plot: {fig_path}")


if __name__ == "__main__":
    main()
