# Status

| Field | Value |
|-------|-------|
| **Phase** | v0.2 shipped |
| **Symbol** | ✅ |
| **Started** | 2026-06-13 |
| **Shipped** | 2026-06-28 |
| **Owner** | — |
| **Blockers** | — |
| **Notes** | Published at https://github.com/KanakMalpani/LoopBench; 19 micro-tasks, 4 comparison suites, generalist leaderboard |

## Completion checklist

- [x] `tasks/` — 19 micro-task specs (YAML + README each)
- [x] `tasks/suites/` — 4 comparison suites (repair, agent, knowledge, rigor)
- [x] `metrics/les-compute.md` — observed LES + 4-suite grand composite
- [x] `submit/schema.json` — results file format (v0.2 `suite_scores`, `grand_composite`)
- [x] `cli/loopbench.py` — `suite list`, `--suite run`, `rank --suite`
- [x] `leaderboard/` — README + example entries JSON
- [x] Golden submission tests + CI
- [x] `SYNC.md`, `LICENSE`, `SUITE-OVERVIEW.md`
- [x] LSS validation in CI (01-core)
- [x] Smoke tests for core tasks
- [x] PyPI publish — https://pypi.org/project/loopbench/ (v0.2.0)
- [x] GitHub Pages — generalist + suite tabs, 19-task micro-task view

## Links

- Workspace state: [../WORKSPACE_CURRENT_STATE.md](../WORKSPACE_CURRENT_STATE.md)
- Parent map: [../README.md](../README.md)
- LSS/LES: [../02-loop-core-engineering/](../02-loop-core-engineering/)
- Runtime: [../06-loopgym/](../06-loopgym/)
- Suite catalog: [SUITE-OVERVIEW.md](SUITE-OVERVIEW.md)
- Agent brief: [../AGENT_BRIEFS/loopbench.md](../AGENT_BRIEFS/loopbench.md)
