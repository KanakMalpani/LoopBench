# Status

| Field | Value |
|-------|-------|
| **Phase** | v0.1 shipped |
| **Symbol** | ✅ |
| **Started** | 2026-06-13 |
| **Shipped** | 2026-06-13 |
| **Owner** | — |
| **Blockers** | — |
| **Notes** | Published at https://github.com/KanakMalpani/LoopBench; LiveEnv submissions v0.2 |

## Completion checklist

- [x] `tasks/` — 3 task specs (YAML + README each)
- [x] `metrics/les-compute.md` — observed LES computation
- [x] `submit/schema.json` — results file format
- [x] `cli/loopbench.py` — local eval CLI
- [x] `leaderboard/` — README + example entries JSON
- [x] Golden submission tests + CI
- [x] `SYNC.md`, `LICENSE`, `SUITE-OVERVIEW.md`
- [x] LSS validation in CI (01-core)
- [x] Smoke tests for all 3 tasks
- [ ] PyPI publish (`pip install loopbench` — pending trusted publisher or token on PyPI)

## Links

- Parent workspace: [../README.md](../README.md)
- LSS/LES: [../01-loop-engineering-core](../01-loop-engineering-core/)
- Runtime: [../05-loopgym](../05-loopgym/)
- Agent brief: [../AGENT-BRIEF.md](../AGENT-BRIEF.md)
