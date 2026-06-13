"""Observed LES computation for LoopBench runs (LES-1.0 aligned)."""

from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean, median

LES_WEIGHTS: dict[str, float] = {
    "effectiveness": 0.20,
    "speed": 0.15,
    "cost": 0.12,
    "robustness": 0.13,
    "scalability": 0.10,
    "safety": 0.12,
    "adaptability": 0.10,
    "autonomy": 0.08,
}


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _normalize(x: float, b_floor: float, b_ceiling: float) -> float:
    if b_ceiling <= b_floor:
        return 0.0
    return _clamp((x - b_floor) / (b_ceiling - b_floor))


def _is_improving(goal_trace: list[float]) -> bool:
    if len(goal_trace) < 3:
        return False
    start = max(1, (2 * len(goal_trace)) // 3)
    window = goal_trace[start:]
    if len(window) < 2:
        return False
    improvements = sum(1 for i in range(1, len(window)) if window[i] > window[i - 1])
    return improvements / (len(window) - 1) >= 0.6


@dataclass
class RunMetrics:
    task_instance_id: str
    seed: int
    g_final: float
    g_0: float
    g_target: float
    iterations: int
    t_budget: int
    cost_usd: float
    elapsed_s: float
    success: bool
    termination_reason: str
    safety_violations: int = 0
    goal_trace: list[float] = field(default_factory=list)


@dataclass
class LesResult:
    les_observed: float
    les_display: float
    categories: dict[str, float]


def effectiveness_score(run: RunMetrics) -> float:
    g_final, g_target = run.g_final, run.g_target
    if g_target <= 0:
        return 0.0
    if g_final >= g_target:
        e_raw = g_final / g_target
    elif _is_improving(run.goal_trace):
        e_raw = (g_final / g_target) * (run.t_budget / max(run.iterations, 1))
    else:
        e_raw = (g_final / g_target) * 0.5
    return _normalize(e_raw, 0.5, 1.0)


def speed_score(run: RunMetrics, b_floor: float = 0.001, b_ceiling: float = 0.05) -> float:
    if run.iterations <= 0 or run.elapsed_s <= 0:
        return 0.0
    tau = run.elapsed_s / run.iterations
    s_raw = 1.0 / tau
    return _normalize(s_raw, b_floor, b_ceiling)


def cost_score(
    run: RunMetrics,
    b_floor: float = 0.05,
    b_ceiling: float = 2.0,
) -> float:
    delta_g = run.g_final - run.g_0
    if delta_g <= 0 or run.cost_usd <= 0:
        return 0.0
    return _normalize(delta_g / run.cost_usd, b_floor, b_ceiling)


def safety_score(run: RunMetrics) -> float:
    if run.safety_violations >= 10:
        return 0.0
    return _clamp(1.0 - min(run.safety_violations / 10.0, 1.0))


def robustness_from_seeds(runs: list[RunMetrics]) -> float:
    finals = [r.g_final for r in runs]
    if not finals:
        return 0.0
    g_clean = max(finals)
    g_perturbed = min(finals)
    if g_clean <= 0:
        return 0.0
    degradation = 1.0 - (g_perturbed / g_clean)
    return _clamp(1.0 - degradation)


def scalability_score(runs: list[RunMetrics]) -> float:
    if not runs:
        return 0.0
    retention = mean(r.g_final / r.g_target if r.g_target > 0 else 0.0 for r in runs)
    return _normalize(retention, 0.4, 0.90)


def adaptability_score(runs: list[RunMetrics]) -> float:
    if not runs:
        return 0.0
    return _clamp(mean(1.0 if r.success else r.g_final / r.g_target if r.g_target else 0.0 for r in runs))


def autonomy_score(_runs: list[RunMetrics], backend: str = "sim") -> float:
    return 0.95 if backend == "sim" else 0.5


def compute_run_categories(
    run: RunMetrics,
    *,
    speed_baselines: tuple[float, float] | None = None,
    cost_baselines: tuple[float, float] | None = None,
) -> dict[str, float]:
    b_floor, b_ceiling = speed_baselines or (0.001, 0.05)
    c_floor, c_ceiling = cost_baselines or (0.05, 2.0)
    return {
        "effectiveness": effectiveness_score(run),
        "speed": speed_score(run, b_floor, b_ceiling),
        "cost": cost_score(run, c_floor, c_ceiling),
        "safety": safety_score(run),
    }


def compute_task_les(
    runs: list[RunMetrics],
    *,
    speed_baselines: tuple[float, float] | None = None,
    cost_baselines: tuple[float, float] | None = None,
    backend: str = "sim",
) -> LesResult:
    if not runs:
        return LesResult(0.0, 0.0, {k: 0.0 for k in LES_WEIGHTS})

    per_run = [
        compute_run_categories(
            r,
            speed_baselines=speed_baselines,
            cost_baselines=cost_baselines,
        )
        for r in runs
    ]
    categories: dict[str, float] = {
        "effectiveness": mean(c["effectiveness"] for c in per_run),
        "speed": mean(c["speed"] for c in per_run),
        "cost": mean(c["cost"] for c in per_run),
        "safety": mean(c["safety"] for c in per_run),
        "robustness": robustness_from_seeds(runs),
        "scalability": scalability_score(runs),
        "adaptability": adaptability_score(runs),
        "autonomy": autonomy_score(runs, backend),
    }
    composite = sum(LES_WEIGHTS[k] * categories[k] for k in LES_WEIGHTS)
    les_observed = round(composite, 4)
    return LesResult(
        les_observed=les_observed,
        les_display=round(les_observed * 100, 1),
        categories={k: round(v, 4) for k, v in categories.items()},
    )


def compute_composite(task_les: list[float]) -> tuple[float, float, float]:
    if not task_les:
        return 0.0, 0.0, 0.0
    avg = mean(task_les)
    return round(avg, 4), round(avg * 100, 1), round(avg, 4)
