# Sync policy — LoopBench

**Defines tasks and scoring; LoopGym runs them.**

| Artifact | Canonical source | This repo |
|----------|------------------|-----------|
| LSS / LES specs | [Loop Core Engineering](https://github.com/KanakMalpani/Loop-Core-Engineering) | Pin `lss@1.0.0`, `les@1.0.0` in submissions |
| Execution | [LoopGym](https://github.com/KanakMalpani/LoopGym) | `loopbench.runner.run_task` → `loopgym.make()` |
| Env IDs | Loop Core Engineering `specs/loop-ids.md` | Task `loopgym_env` must match registry |
| Holdout data (v0.2) | [LoopNet](https://github.com/KanakMalpani/loopnet) | Optional eval splits |

**Repository:** https://github.com/KanakMalpani/LoopBench

## Validation before submit

```bash
# LSS spec (submission examples)
python deps/loop-core/tools/validate_lss.py submissions/examples/spec-fast-loop.yaml

# Results JSON
loopbench validate results.json
```

## Do not duplicate

- LSS schema — validate against Loop Core Engineering
- LoopGym env implementations — reference env IDs only
- LES formulas — implement in `les_compute.py` per Loop Core Engineering `specs/les-1.0.md`

## CI dependency order

```
Loop Core Engineering (schema)
LoopGym (runtime)
LoopBench (this repo)
```
