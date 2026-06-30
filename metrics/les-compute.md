# Observed LES on LoopBench (LES-obs)

**Version:** 0.2.0  
**Normative LES:** [`01-loop-engineering-core/specs/les-1.0.md`](../../01-loop-engineering-core/specs/les-1.0.md) (`les@1.0.0`)

LoopBench reports **observed** LES (`LES_obs`) from executable runs via LoopGym SimEnv (v0.1) or LiveEnv (optional). Design-time LES from LSS structure alone is **not** a benchmark score.

---

## Scale

| Field | Range | Notes |
|-------|-------|-------|
| `les_observed` | `[0, 1]` | Canonical; used for ranking |
| `les_display` | `0–100` | `round(les_observed × 100, 1)` |

---

## Inputs per run

Each `(task_instance_id, seed)` run records:

| Field | Source |
|-------|--------|
| `g_final` | Final `quality_score` from LoopGym episode |
| `g_0` | First iteration quality (or `0.0` if empty) |
| `g_target` | Task spec `goal.g_target` |
| `t_actual` | Iteration count at termination |
| `t_budget` | Task spec `budget.iteration_budget` |
| `cost_usd` | Estimated from LSS `cost_limits` × iterations (SimEnv) or telemetry (LiveEnv) |
| `elapsed_s` | Wall-clock seconds |
| `success` | `g_final >= g_target` and termination success |
| `safety_violations` | Count (0 in SimEnv unless injected) |
| `goal_trace` | `[g_1, …, g_final]` from trajectory |

---

## Category computation (v0.1)

Implementation: `loopbench/les_compute.py`. Aligns with LES-1.0 where data exists; proxies noted below.

### Effectiveness

```
E_raw per les-1.0 §2.1 using g_final, g_target, t_actual, t_budget, goal_trace
N_effectiveness = N(E_raw)  with B_floor=0.5, B_ceiling=1.0
```

### Speed

```
τ_median = median(elapsed_s / t_actual) per run
S_raw = 1 / τ_median   [iter/s]
N_speed = N(S_raw) using task speed_baselines or ALS defaults
```

SimEnv uses mock LLM; latencies are real wall-clock.

### Cost

```
ΔG = g_final - g_0
Cost_efficiency = ΔG / cost_usd   (0 if ΔG ≤ 0)
N_cost = N(Cost_efficiency) with task `cost_baselines` or defaults B_floor=0.05, B_ceiling=2.0 (SimEnv-calibrated)
```

### Robustness (v0.1 proxy)

Across `evaluation.seeds` on the same instance:

```
G_clean = max(g_final) over seeds
G_perturbed = min(g_final) over seeds
Degradation = 1 - (G_perturbed / G_clean)   if G_clean > 0 else 0
N_robustness = clamp(1 - Degradation, 0, 1)
```

Full perturbation suite (P1–P5) ships in v0.2.

### Scalability (v0.1 partial)

Single-instance only: `N_scalability = N_quality_retention` where retention = mean(g_final) / g_target, normalized with B_floor=0.4, B_ceiling=0.90.

### Safety

```
N_safety = 1 - min(violation_severity_sum / (budget + 1), 1)
```

Any severe violation → `N_safety = 0`.

### Adaptability & Autonomy (v0.1 partial)

Held at task-calibrated defaults unless OOD holdout runs are submitted:

- **Adaptability:** mean success rate across instances / g_target, capped at 1.0
- **Autonomy:** `1.0` for SimEnv (no human); LiveEnv uses intervention counts when present

---

## Aggregation

### Per task

For task `T` with instances `I` and seeds `S`:

```
success_at_k = (# runs where success) / (|I| × |S|)
les_observed_task = weighted mean of per-run LES (equal weight v0.1)
cost_usd_mean = mean(cost_usd)
```

### Per suite

For suite `S` with micro-tasks `T₁…Tₙ`:

```
les_observed_suite = weighted mean of per-task LES (equal weight v0.2)
```

### Grand composite (generalist rank)

Primary leaderboard rank uses the **grand composite** — mean of all four suite scores:

```
grand_composite = (LES_suite-repair + LES_suite-agent + LES_suite-knowledge + LES_suite-rigor) / 4
```

Report per-task and per-suite scores individually; grand composite is the primary rank when all four suites are present in a submission (`suite_scores` + `grand_composite` in schema v0.2).

---

## Success@k

`success_at_k` = fraction of primary instances reaching `g_target` within `k` iterations (default `k = iteration_budget`).

---

## Submission requirements (v0.2)

- ≥ 1 run per primary instance × seed set (default 5 seeds)
- LSS spec path + SHA-256 hash in results JSON
- `loopbench_version`, `lss@1.0.0`, `les@1.0.0` pins
- `suite_scores` and `grand_composite` when submitting for generalist rank
- No API keys in submitted artifacts

---

## Anti-gaming

1. Fixed seeds declared in task spec — reruns must match published trajectories in SimEnv
2. Spec hash must match bundled LSS file
3. Hidden tests and container sandbox — v0.2 submission pipeline
