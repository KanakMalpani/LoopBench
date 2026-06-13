"""Run LoopBench evaluations via LoopGym."""

from __future__ import annotations

import hashlib
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import loopgym as lg
import yaml

from loopbench import __version__
from loopbench.les_compute import LES_WEIGHTS, LesResult, RunMetrics, compute_composite, compute_task_les
from loopbench.tasks import cost_baselines, load_task, speed_baselines


def spec_hash(path: Path) -> str:
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return f"sha256:{digest}"


def estimate_cost_usd(spec: dict, iterations: int) -> float:
    cost = spec.get("cost_limits") or {}
    per_iter = float(cost.get("per_iteration_usd", 0.05))
    return round(per_iter * iterations, 4)


def run_task(
    task_id: str,
    spec_path: Path,
    *,
    seeds: list[int] | None = None,
    instances: list[str] | None = None,
    backend: str = "sim",
) -> dict:
    task = load_task(task_id)
    env_id = task["loopgym_env"]
    g_target = float(task["goal"]["g_target"])
    t_budget = int(task["budget"]["iteration_budget"])
    eval_cfg = task.get("evaluation") or {}
    seed_list = seeds if seeds is not None else list(eval_cfg.get("seeds", [0]))
    instance_list = instances if instances is not None else list(eval_cfg.get("primary_instances", []))

    with spec_path.open(encoding="utf-8") as fh:
        spec = yaml.safe_load(fh)

    env = lg.make(env_id, spec_path=spec_path, backend=backend)
    runs: list[RunMetrics] = []

    for instance_id in instance_list:
        for seed in seed_list:
            t0 = time.perf_counter()
            result = env.run_episode(task_id=instance_id, seed=seed)
            elapsed = time.perf_counter() - t0
            trace = [s["quality_score"] for s in result.get("trajectory", [])]
            g_0 = trace[0] if trace else 0.0
            g_final = float(result.get("quality_score", 0.0))
            iterations = int(result.get("steps", 1))
            runs.append(
                RunMetrics(
                    task_instance_id=instance_id,
                    seed=seed,
                    g_final=g_final,
                    g_0=g_0,
                    g_target=g_target,
                    iterations=iterations,
                    t_budget=t_budget,
                    cost_usd=estimate_cost_usd(spec, iterations),
                    elapsed_s=round(elapsed, 4),
                    success=bool(result.get("success")) or g_final >= g_target,
                    termination_reason="goal_met" if (bool(result.get("success")) or g_final >= g_target) else "budget_exhausted",
                    goal_trace=trace,
                )
            )

    les: LesResult = compute_task_les(
        runs,
        speed_baselines=speed_baselines(task),
        cost_baselines=cost_baselines(task),
        backend=backend,
    )
    success_at_k = sum(1 for r in runs if r.success) / len(runs) if runs else 0.0

    return {
        "task_id": task_id,
        "env_id": env_id,
        "runs": [
            {
                "task_instance_id": r.task_instance_id,
                "seed": r.seed,
                "success": r.success,
                "g_final": round(r.g_final, 4),
                "g_0": round(r.g_0, 4),
                "g_target": r.g_target,
                "iterations": r.iterations,
                "cost_usd": r.cost_usd,
                "elapsed_s": r.elapsed_s,
                "termination_reason": r.termination_reason,
                "safety_violations": r.safety_violations,
                "goal_trace": [round(g, 4) for g in r.goal_trace],
            }
            for r in runs
        ],
        "aggregate": {
            "success_at_k": round(success_at_k, 4),
            "les_observed": les.les_observed,
            "les_display": les.les_display,
            "categories": les.categories,
            "cost_usd_mean": round(sum(r.cost_usd for r in runs) / len(runs), 4) if runs else 0.0,
            "robustness_seeds": len(seed_list),
        },
    }


def build_submission(
    submitter: str,
    spec_path: Path,
    task_results: list[dict],
    *,
    backend: str = "sim",
) -> dict:
    les_values = [tr["aggregate"]["les_observed"] for tr in task_results]
    les_obs, les_disp, rank = compute_composite(les_values)
    return {
        "submission_id": str(uuid4()),
        "submitter": submitter,
        "loopbench_version": __version__,
        "lss_version": "1.0.0",
        "les_version": "1.0.0",
        "spec_path": spec_path.as_posix(),
        "spec_hash": spec_hash(spec_path),
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "backend": backend,
        "results": task_results,
        "composite": {
            "les_observed": les_obs,
            "les_display": les_disp,
            "rank_score": rank,
        },
    }
