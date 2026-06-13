# LB-CR-1 — Code Repair

**LoopGym env:** `loopbench/code-repair-v1` (`lg/loopbench/code-repair-v1`)

Given a repository snapshot with failing tests and a bug description, the loop must produce a minimal patch until tests pass and quality rubric ≥ 0.80.

## Goal function

```
G = 0.70 × test_pass_rate + 0.15 × type_clean + 0.15 × diff_score
G_target = 0.80
```

In SimEnv v0.1, `G_final` is approximated by the LSS `primary_quality` metric at termination.

## Task instances

| Instance | Difficulty | ID |
|----------|------------|-----|
| parse_int bug | easy | `cr-001` |
| binary search | medium | `cr-002` |
| async cache race | hard | `cr-003` |

## Run locally

```bash
loopbench run --task LB-CR-1 --spec ../05-loopgym/envs/loopbench/code-repair-v1/spec.yaml --output /tmp/cr-results.json
```

## LES stress

Primary: **Effectiveness**, **Speed**, **Robustness**

## Reference

Canonical execution lives in `05-loopgym/envs/loopbench/code-repair-v1/`. Narrative ALS doc: `Loop Engineering/benchmarks/tasks/code-repair.md`.
