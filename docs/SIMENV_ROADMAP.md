# LoopGym SimEnv roadmap (LoopBench v0.3)

Wave 15 micro-tasks reuse four env IDs. Wave 16+ adds targeted envs for measurement honesty.

## Current env reuse (v0.2)

| Env | Tasks |
|-----|-------|
| `loopbench/code-repair-v1` | CR, ReAct, Reflexion, OPT, SAFE, MEM, NEST |
| `loopbench/research-synthesis-v1` | RS, RAG, BOOT, AUTO, HITL |
| `loopbench/multi-agent-debate-v1` | MA, Crew, ToT, Vote |
| `loopbench/composed-swarm-v1` | COMP, Graph, SIM |

## Planned envs (v0.3) — shipped in LoopGym 0.1.3

### `loopbench/rag-retrieval-v1` ✅

- Perturbed retrieval corpora (P2 missing-source, P3 stale doc)
- Task: `LB-RAG-1`

### `loopbench/hitl-gate-v1` ✅

- Simulated human approval / rejection steps
- Task: `LB-HITL-1`

### `loopbench/safety-constrained-v1` ✅

- Tool denylist violations terminate episodes
- Task: `LB-SAFE-1`

## Perturbation suite P1–P5

Implement in LoopGym; wire robustness LES to perturbation success rate (not seed min/max proxy).

| ID | Description |
|----|-------------|
| P1 | Seed variance (existing) |
| P2 | Missing / corrupted context |
| P3 | Stale or conflicting sources |
| P4 | Budget pressure (tighter iteration cap) |
| P5 | Tool / API failure injection |

See [`metrics/les-compute.md`](../metrics/les-compute.md) for scoring once perturbations ship.
