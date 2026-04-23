import argparse
import csv
import os
import random
from typing import List

import matplotlib.pyplot as plt

from smartgrid_mas.engine.policies import (
    adaptive_stackelberg_action,
    heuristic_joint_action,
    random_joint_action,
)
from smartgrid_mas.env import SmartGridMarketEnv


def run_episode(env: SmartGridMarketEnv, policy_name: str, seed: int) -> float:
    reset = env.reset(task_id="default", seed=seed)
    sid = reset.session_id
    obs = reset.observation
    rng = random.Random(seed)

    rewards: List[float] = []
    while True:
        if policy_name == "random":
            action = random_joint_action(obs, rng)
        elif policy_name == "adaptive":
            action = adaptive_stackelberg_action(obs, personality="balanced")
        else:
            action = heuristic_joint_action(obs, personality="balanced")

        step = env.step(action=action, session_id=sid)
        rewards.append(step.reward.score)
        obs = step.observation
        if step.done:
            break

    return sum(rewards) / max(1, len(rewards))


def main() -> None:
    parser = argparse.ArgumentParser(description="Minimal baseline training/eval runner")
    parser.add_argument("--episodes", type=int, default=30)
    parser.add_argument("--outdir", type=str, default="artifacts")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    env = SmartGridMarketEnv()
    random_curve = []
    heuristic_curve = []
    adaptive_curve = []

    for ep in range(args.episodes):
        random_curve.append(run_episode(env, "random", seed=1000 + ep))
        heuristic_curve.append(run_episode(env, "heuristic", seed=2000 + ep))
        adaptive_curve.append(run_episode(env, "adaptive", seed=3000 + ep))

    csv_path = os.path.join(args.outdir, "baseline_metrics.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["episode", "random_avg_reward", "heuristic_avg_reward", "adaptive_avg_reward"])
        for i, (r, h, a) in enumerate(zip(random_curve, heuristic_curve, adaptive_curve), start=1):
            writer.writerow([i, round(r, 6), round(h, 6), round(a, 6)])

    plt.figure(figsize=(10, 5))
    plt.plot(range(1, args.episodes + 1), random_curve, label="Random baseline")
    plt.plot(range(1, args.episodes + 1), heuristic_curve, label="Heuristic improved")
    plt.plot(range(1, args.episodes + 1), adaptive_curve, label="Adaptive Stackelberg")
    plt.xlabel("Episode")
    plt.ylabel("Average reward")
    plt.title("Baseline vs Improved Policy Reward")
    plt.legend()
    plt.grid(alpha=0.25)

    fig_path = os.path.join(args.outdir, "reward_comparison.png")
    plt.tight_layout()
    plt.savefig(fig_path, dpi=160)

    print(f"Saved metrics CSV: {csv_path}")
    print(f"Saved reward plot: {fig_path}")


if __name__ == "__main__":
    main()
