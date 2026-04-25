import argparse
import csv
import os
import random
from dataclasses import replace
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

METRIC_DIRECTIONS = {
    "avg_reward": "higher",
    "avg_cost_usd": "lower",
    "blackout_rate": "lower",
    "constraint_violation_rate": "lower",
    "emissions_tco2": "lower",
    "unmet_energy_mwh": "lower",
    "reserve_shortfall_rate": "lower",
    "stability_event_rate": "lower",
}

ABLATION_PROFILES = {
    "full_ldu": {
        "enable_reserve_logic": True,
        "enable_ramp_limits": True,
        "enable_startup_emissions": True,
    },
    "ablate_reserve": {
        "enable_reserve_logic": False,
        "enable_ramp_limits": True,
        "enable_startup_emissions": True,
    },
    "ablate_ramp": {
        "enable_reserve_logic": True,
        "enable_ramp_limits": False,
        "enable_startup_emissions": True,
    },
    "ablate_startup_emissions": {
        "enable_reserve_logic": True,
        "enable_ramp_limits": True,
        "enable_startup_emissions": False,
    },
}


def _std(values: List[float]) -> float:
    if len(values) <= 1:
        return 0.0
    mu = mean(values)
    return (sum((v - mu) ** 2 for v in values) / (len(values) - 1)) ** 0.5


def _quantile(values: List[float], q: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    idx = max(0, min(len(s) - 1, int(round((len(s) - 1) * q))))
    return s[idx]


def _bootstrap_ci_mean(values: List[float], samples: int, rng: random.Random) -> tuple[float, float]:
    if not values:
        return 0.0, 0.0
    if len(values) == 1:
        return values[0], values[0]
    means: List[float] = []
    for _ in range(samples):
        draw = [values[rng.randrange(0, len(values))] for _ in range(len(values))]
        means.append(sum(draw) / len(draw))
    return _quantile(means, 0.025), _quantile(means, 0.975)


def run_episode(
    env: SmartGridMarketEnv,
    policy_name: str,
    task_id: str,
    seed: int,
    task_overrides: Dict[str, bool] | None = None,
) -> Dict[str, float]:
    reset = env.reset(task_id=task_id, seed=seed)
    sid = reset.session_id
    if task_overrides:
        env._sessions[sid].task = replace(env._sessions[sid].task, **task_overrides)
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
    parser.add_argument("--bootstrap-samples", type=int, default=1000)
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    env = SmartGridMarketEnv()
    policies = ["random", "heuristic", "adaptive"]
    tasks = BENCHMARK_SCENARIOS
    rows = []
    reward_curves = {policy: [] for policy in policies}
    trials = []

    for scenario_name, task_id in tasks.items():
        for seed_idx in range(args.seeds):
            base_seed = 1000 + seed_idx * 137
            for ep in range(args.episodes):
                rollout_seed = base_seed + ep * 11
                trial_record = {
                    "scenario": scenario_name,
                    "task_id": task_id,
                    "seed_group": seed_idx,
                    "episode": ep + 1,
                    "rollout_seed": rollout_seed,
                    "policy_metrics": {},
                }
                for policy in policies:
                    result = run_episode(
                        env=env,
                        policy_name=policy,
                        task_id=task_id,
                        seed=rollout_seed,
                    )
                    row = {
                        "policy": policy,
                        "scenario": scenario_name,
                        "task_id": task_id,
                        "seed_group": seed_idx,
                        "episode": ep + 1,
                        "rollout_seed": rollout_seed,
                        **{k: round(v, 6) for k, v in result.items()},
                    }
                    rows.append(row)
                    trial_record["policy_metrics"][policy] = result
                    if scenario_name == "normal" and seed_idx == 0:
                        reward_curves[policy].append(result["avg_reward"])
                trials.append(trial_record)

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
                "rollout_seed",
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

    pair_rows = []
    ci_rng = random.Random(2026)
    pairs = [("adaptive", "heuristic"), ("adaptive", "random"), ("heuristic", "random")]
    for scenario_name, task_id in tasks.items():
        scenario_trials = [t for t in trials if t["scenario"] == scenario_name and t["task_id"] == task_id]
        for candidate, baseline in pairs:
            for metric, direction in METRIC_DIRECTIONS.items():
                deltas = []
                wins = 0
                for trial in scenario_trials:
                    c_val = trial["policy_metrics"][candidate][metric]
                    b_val = trial["policy_metrics"][baseline][metric]
                    delta = c_val - b_val
                    deltas.append(delta)
                    if direction == "higher" and c_val > b_val:
                        wins += 1
                    if direction == "lower" and c_val < b_val:
                        wins += 1

                ci_low, ci_high = _bootstrap_ci_mean(deltas, samples=args.bootstrap_samples, rng=ci_rng)
                pair_rows.append(
                    {
                        "scenario": scenario_name,
                        "task_id": task_id,
                        "candidate_policy": candidate,
                        "baseline_policy": baseline,
                        "metric": metric,
                        "direction": direction,
                        "n_trials": len(deltas),
                        "mean_delta": round(mean(deltas) if deltas else 0.0, 6),
                        "ci95_low": round(ci_low, 6),
                        "ci95_high": round(ci_high, 6),
                        "win_rate": round((wins / len(deltas)) if deltas else 0.0, 6),
                    }
                )

    pair_csv_path = os.path.join(args.outdir, "policy_pairwise_deltas.csv")
    with open(pair_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "scenario",
                "task_id",
                "candidate_policy",
                "baseline_policy",
                "metric",
                "direction",
                "n_trials",
                "mean_delta",
                "ci95_low",
                "ci95_high",
                "win_rate",
            ],
        )
        writer.writeheader()
        writer.writerows(pair_rows)

    winrate_md_path = os.path.join(args.outdir, "policy_win_rates.md")
    with open(winrate_md_path, "w", encoding="utf-8") as f:
        f.write("# Policy Win Rates and Paired Deltas\n\n")
        f.write(
            "| Scenario | Candidate | Baseline | Metric | Direction | Mean Delta | 95% CI | Win Rate | Trials |\n"
        )
        f.write("|---|---|---|---|---|---:|---:|---:|---:|\n")
        for row in sorted(
            pair_rows,
            key=lambda r: (r["scenario"], r["candidate_policy"], r["baseline_policy"], r["metric"]),
        ):
            f.write(
                f"| {row['scenario']} | {row['candidate_policy']} | {row['baseline_policy']} | {row['metric']} | "
                f"{row['direction']} | {row['mean_delta']:.4f} | [{row['ci95_low']:.4f}, {row['ci95_high']:.4f}] | "
                f"{row['win_rate']:.3f} | {row['n_trials']} |\n"
            )

    ablation_rows = []
    for scenario_name, task_id in tasks.items():
        for seed_idx in range(args.seeds):
            base_seed = 8000 + seed_idx * 137
            for ep in range(args.episodes):
                rollout_seed = base_seed + ep * 11
                for profile_name, overrides in ABLATION_PROFILES.items():
                    result = run_episode(
                        env=env,
                        policy_name="adaptive",
                        task_id=task_id,
                        seed=rollout_seed,
                        task_overrides=overrides,
                    )
                    ablation_rows.append(
                        {
                            "profile": profile_name,
                            "policy": "adaptive",
                            "scenario": scenario_name,
                            "task_id": task_id,
                            "seed_group": seed_idx,
                            "episode": ep + 1,
                            "rollout_seed": rollout_seed,
                            **{k: round(v, 6) for k, v in result.items()},
                        }
                    )

    ablation_csv_path = os.path.join(args.outdir, "ablation_metrics.csv")
    with open(ablation_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "profile",
                "policy",
                "scenario",
                "task_id",
                "seed_group",
                "episode",
                "rollout_seed",
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
        writer.writerows(ablation_rows)

    ablation_grouped = {}
    for row in ablation_rows:
        key = (row["profile"], row["scenario"], row["task_id"])
        ablation_grouped.setdefault(
            key,
            {
                metric: []
                for metric in [
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
        for metric in ablation_grouped[key]:
            ablation_grouped[key][metric].append(float(row[metric]))

    ablation_summary = []
    for (profile, scenario, task_id), metrics in ablation_grouped.items():
        ablation_summary.append(
            {
                "profile": profile,
                "scenario": scenario,
                "task_id": task_id,
                "avg_reward": round(mean(metrics["avg_reward"]), 6),
                "avg_cost_usd": round(mean(metrics["avg_cost_usd"]), 6),
                "blackout_rate": round(mean(metrics["blackout_rate"]), 6),
                "constraint_violation_rate": round(mean(metrics["constraint_violation_rate"]), 6),
                "emissions_tco2": round(mean(metrics["emissions_tco2"]), 6),
                "reserve_shortfall_rate": round(mean(metrics["reserve_shortfall_rate"]), 6),
                "stability_event_rate": round(mean(metrics["stability_event_rate"]), 6),
            }
        )

    ablation_md_path = os.path.join(args.outdir, "ablation_comparison.md")
    with open(ablation_md_path, "w", encoding="utf-8") as f:
        f.write("# LDU Ablation Comparison (adaptive policy)\n\n")
        f.write("| Scenario | Profile | Avg Reward | Avg Cost USD | Blackout Rate | Reserve Shortfall Rate | Stability Event Rate |\n")
        f.write("|---|---|---:|---:|---:|---:|---:|\n")
        for row in sorted(ablation_summary, key=lambda x: (x["scenario"], x["profile"])):
            f.write(
                f"| {row['scenario']} | {row['profile']} | {row['avg_reward']:.4f} | {row['avg_cost_usd']:.3f} | "
                f"{row['blackout_rate']:.4f} | {row['reserve_shortfall_rate']:.4f} | {row['stability_event_rate']:.4f} |\n"
            )

    report_path = os.path.join(args.outdir, "resilience_stress_benchmark.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Resilience Stress Benchmark\n\n")
        f.write("## Protocol\n")
        f.write(f"- Scenarios: {', '.join(BENCHMARK_SCENARIOS.keys())}\n")
        f.write(f"- Policies: {', '.join(policies)}\n")
        f.write(f"- Seeds per scenario: {args.seeds}\n")
        f.write(f"- Episodes per seed: {args.episodes}\n")
        f.write(f"- Bootstrap samples for paired CI: {args.bootstrap_samples}\n")
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
        f.write("- Paired deltas and confidence intervals are available in policy_pairwise_deltas.csv and policy_win_rates.md.\n")
        f.write("- LDU ablation evidence is available in ablation_metrics.csv and ablation_comparison.md.\n")

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
    print(f"Saved pairwise delta CSV: {pair_csv_path}")
    print(f"Saved policy win-rate markdown: {winrate_md_path}")
    print(f"Saved ablation metrics CSV: {ablation_csv_path}")
    print(f"Saved ablation markdown: {ablation_md_path}")
    print(f"Saved resilience benchmark markdown: {report_path}")
    print(f"Saved reward plot: {fig_path}")


if __name__ == "__main__":
    main()
