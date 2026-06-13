# 06 — loopbench

## One-line purpose

**LoopBench** — world's definitive loop benchmark suite, metrics, submission pipeline, and leaderboards.

## Why this repo exists

Fields need **comparable scores**. LoopBench is MLPerf for loops — tasks, rules, anti-gaming, public ranks.

## Scope (in scope)

- Task definitions (ALS v2): code-repair, research-synthesis, multi-agent-debate (+ expand)
- Oracle specifications per task
- Metrics: Success@k, LES-obs, cost, robustness (5 seeds), safety
- Submission format: container + LSS + results JSON
- Local runner CLI (`loopbench run`)
- Leaderboard schema (static JSON v0.1 → web v0.2)
- Conformance tests: "does submission follow rules?"

## Scope (out of scope)

- Gym implementation → `05-loopgym` (LoopBench *defines*, LoopGym *runs*)

## Deliverables v0.1

- [x] `tasks/` — 3 task specs (YAML + README each)
- [x] `metrics/les-compute.md` — how observed LES is computed on bench
- [x] `submit/schema.json` — results file format
- [x] `cli/loopbench.py` — local eval
- [x] `leaderboard/` — README + example entries JSON

## Task IDs (initial)

| ID | Name |
|----|------|
| `LB-CR-1` | Code repair |
| `LB-RS-1` | Research synthesis |
| `LB-MA-1` | Multi-agent debate |

## Dependencies

- **01-loop-engineering-core** — LES, LSS
- **05-loopgym** — execution engine

## Success criteria

Two different LSS specs submitted locally; leaderboard JSON ranks by composite; CI runs golden submission.

## Agent instructions

Align with existing `benchmarks/` in `Loop Engineering` repo then **move** canonical tasks here. Fixed seeds, pinned deps.

## Status

✅ v0.1 shipped (2026-06-13) — see [STATUS.md](./STATUS.md)
