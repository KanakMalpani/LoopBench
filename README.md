# LoopBench

[![test](https://github.com/KanakMalpani/LoopBench/actions/workflows/test.yml/badge.svg)](https://github.com/KanakMalpani/LoopBench/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Suite v0.1](https://img.shields.io/badge/suite-v0.1-blue.svg)](SUITE-OVERVIEW.md)

**LoopBench** — benchmark suite, metrics, submission pipeline, and leaderboards for Loop Engineering (MLPerf for loops).

LoopBench **defines** tasks and scoring; [LoopGym](https://github.com/KanakMalpani/LoopGym) **runs** them.

---

## Ecosystem

| Repo | Purpose |
|------|---------|
| [Loop Core Engineering](https://github.com/KanakMalpani/Loop-Core-Engineering) | LSS / LES specs |
| [LoopNet](https://github.com/KanakMalpani/loopnet) | Trajectory dataset |
| [LoopGym](https://github.com/KanakMalpani/LoopGym) | Execution engine |
| **LoopBench** (this repo) | Tasks, scoring, submissions, leaderboard |

---

## Quick start

Clone LoopGym alongside this repo (or install from git):

```bash
git clone https://github.com/KanakMalpani/LoopBench.git
git clone https://github.com/KanakMalpani/LoopGym.git ../LoopGym

cd LoopBench
pip install -e ../LoopGym
pip install -e ".[dev]"
```

```bash
loopbench list
loopbench run --task LB-CR-1 --spec submissions/examples/spec-fast-loop.yaml \
  --seeds 0,1,2,3,4 -o results.json
loopbench validate results.json
loopbench rank leaderboard/entries.json
```

On Windows, use `py -3.12` if the default Python lacks pip.

---

## Tasks (v0.1)

| ID | Name | LoopGym env |
|----|------|-------------|
| `LB-CR-1` | Code repair | `loopbench/code-repair-v1` |
| `LB-RS-1` | Research synthesis | `loopbench/research-synthesis-v1` |
| `LB-MA-1` | Multi-agent debate | `loopbench/multi-agent-debate-v1` |

Task specs: [`tasks/`](tasks/)

---

## Layout

| Path | Purpose |
|------|---------|
| `SUITE-OVERVIEW.md` | ALS v2 suite architecture |
| `tasks/` | ALS v2 task definitions (YAML + README) |
| `metrics/les-compute.md` | Observed LES (`LES_obs`) computation |
| `submit/schema.json` | Submission results JSON schema |
| `loopbench/` | Python package (runner, LES compute, conformance) |
| `leaderboard/` | Static JSON rankings v0.1 |
| `submissions/examples/` | Reference LSS specs for local eval |
| `SYNC.md` | Cross-repo sync policy |

---

## Metrics

- **Success@k** — fraction of instances reaching `g_target`
- **LES_obs** — observed composite per [`metrics/les-compute.md`](metrics/les-compute.md)
- **Cost** — estimated USD per run
- **Robustness** — cross-seed quality retention (5 seeds default)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Submit benchmark results via PR to `leaderboard/entries.json` after `loopbench validate`.

---

## Status

v0.1 shipped — see [`STATUS.md`](STATUS.md).
