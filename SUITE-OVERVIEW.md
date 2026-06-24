# LoopBench Suite Overview (ALS v2)

**Version:** 0.1.0  
**Suite ID:** `loopbench-1.0`

LoopBench is the **measurement layer** of Loop Engineering: fixed tasks, fixed seeds, observed LES (`LES_obs`), public rankings.

---

## Architecture

```
┌─────────────────┐     defines      ┌─────────────────┐
│   LoopBench     │ ───────────────► │    LoopGym      │
│  tasks/         │   env_id, goal   │  SimEnv / Live  │
│  les_compute    │ ◄─────────────── │  run_episode()  │
└────────┬────────┘   trajectories   └─────────────────┘
         │
         ▼
┌─────────────────┐
│  submissions/   │  results JSON → validate → leaderboard
└─────────────────┘
```

---

## Task catalog (v0.1)

| ID | Env | Pattern | Primary stress |
|----|-----|---------|----------------|
| `LB-CR-1` | `loopbench/code-repair-v1` | verification, reflection | Effectiveness, speed, robustness |
| `LB-RS-1` | `loopbench/research-synthesis-v1` | research-loop | Effectiveness, cost |
| `LB-MA-1` | `loopbench/multi-agent-debate-v1` | debate, multi-agent | Robustness, adaptability |
| `LB-COMP-1` | `loopbench/composed-swarm-v1` | parallel composition, swarm | Autonomy, scalability |

Registry: [`tasks/index.yaml`](tasks/index.yaml)

---

## Scoring

- **Per run:** category scores → weighted LES per [`metrics/les-compute.md`](metrics/les-compute.md)
- **Per task:** aggregate across instances × seeds
- **Suite composite:** mean of three task LES (supplementary; rank by task too)

**Scale:** `les_observed ∈ [0, 1]` canonical; display `0–100`.

---

## Submission tiers (v0.1)

| Tier | Backend | Use |
|------|---------|-----|
| **Sim** | LoopGym SimEnv | CI, local dev, leaderboard prototyping |
| **Live** | LoopGym LiveEnv | Real models (API keys, v0.2 audit) |
| **Replay** | LoopNet trajectories | Analysis only — not leaderboard-eligible v0.1 |

---

## Roadmap

| Version | Deliverable |
|---------|-------------|
| v0.1 | 3 tasks, local CLI, static JSON leaderboard ✅ |
| v0.2 | Container sandbox, hidden tests, web leaderboard |
| v0.3 | LoopNet holdout split, perturbation suite P1–P5 |
