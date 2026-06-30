# LoopBench Suite Overview (ALS v2)

**Version:** 0.2.0  
**Suite ID:** `loopbench-1.0`

LoopBench is the **measurement layer** of Loop Engineering: fixed tasks, fixed seeds, observed LES (`LES_obs`), public rankings.

**Wave 15:** 19 micro-tasks feed **4 comparison suites**. Leaderboard primary rank = **generalist** (grand mean of suite scores).

---

## Comparison suites

| Suite ID | Label | Micro-tasks |
|----------|-------|-------------|
| `suite-repair` | Repair & Verify | LB-CR-1, LB-REACT-1, LB-REFLEX-1, LB-OPT-1, LB-SAFE-1 |
| `suite-agent` | Multi-Agent | LB-MA-1, LB-CREW-1, LB-GRAPH-1, LB-TOT-1, LB-VOTE-1 |
| `suite-knowledge` | Research & RAG | LB-RS-1, LB-RAG-1, LB-BOOT-1, LB-AUTO-1 |
| `suite-rigor` | Composition & Safety | LB-COMP-1, LB-NEST-1, LB-SIM-1, LB-HITL-1, LB-MEM-1 |

Registry: [`tasks/suites/index.yaml`](tasks/suites/index.yaml)

```bash
loopbench suite list
loopbench run --suite suite-repair --spec my.yaml --seeds 0,1,2,3,4 -o results.json
```

---

## Task catalog (v0.2 — 19 tasks)

| ID | Env | Pattern |
|----|-----|---------|
| `LB-CR-1` | code-repair-v1 | verification |
| `LB-RS-1` | research-synthesis-v1 | research |
| `LB-MA-1` | multi-agent-debate-v1 | debate |
| `LB-COMP-1` | composed-swarm-v1 | parallel composition |
| `LB-REACT-1` | code-repair-v1 | ReAct |
| `LB-GRAPH-1` | composed-swarm-v1 | state-graph |
| `LB-CREW-1` | multi-agent-debate-v1 | crew |
| `LB-REFLEX-1` | code-repair-v1 | reflexion |
| `LB-AUTO-1` | research-synthesis-v1 | plan-execute |
| `LB-RAG-1` | rag-retrieval-v1 | agentic-rag |
| `LB-OPT-1` | code-repair-v1 | bootstrap-optimize |
| `LB-TOT-1` | multi-agent-debate-v1 | tree-search |
| `LB-VOTE-1` | multi-agent-debate-v1 | self-consistency |
| `LB-HITL-1` | hitl-gate-v1 | human-gate |
| `LB-SAFE-1` | safety-constrained-v1 | safety-constrained |
| `LB-MEM-1` | code-repair-v1 | episodic-memory |
| `LB-BOOT-1` | research-synthesis-v1 | few-shot-bootstrap |
| `LB-SIM-1` | composed-swarm-v1 | simulation-loop |
| `LB-NEST-1` | code-repair-v1 | nested-composition |

Registry: [`tasks/index.yaml`](tasks/index.yaml)

---

## Scoring

- **Per run:** category scores → weighted LES per [`metrics/les-compute.md`](metrics/les-compute.md)
- **Per task:** aggregate across instances × seeds
- **Per suite:** weighted mean of suite micro-tasks
- **Grand composite:** mean of 4 suite scores → **generalist rank**

Submission JSON includes `suite_scores` and `grand_composite` (schema v0.2).

---

## Mix → suite workflow

Pair LoopBench suites with `le-loop-stack` mix recipes:

| Recipe | Default suite |
|--------|---------------|
| `dev-agent` | suite-repair |
| `research-pipeline` | suite-knowledge |
| `swarm-review` | suite-agent |
| `safe-repair` | suite-rigor |
| `full-stack` | all suites (grand) |

```bash
loop mix dev-agent -o mixed.yaml --json
loopctl bench suite suite-repair --spec mixed.yaml -o results.json
```
