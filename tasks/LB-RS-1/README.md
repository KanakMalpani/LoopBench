# LB-RS-1 — Research Synthesis

**LoopGym env:** `loopbench/research-synthesis-v1`

Produce a research brief answering `inputs.query` with ≥3 sources, rubric score ≥ 0.85, valid citations.

## Goal function

```
G = 0.50 × coverage + 0.50 × evidence
G_target = 0.85
```

## Task instances

| Instance | Depth | ID |
|----------|-------|-----|
| Solid-state batteries | standard | `rs-001` |
| RAG vs fine-tuning | deep | `rs-002` |
| EU AI Act | quick | `rs-003` |

## Run locally

```bash
loopbench run --task LB-RS-1 --spec ../05-loopgym/envs/loopbench/research-synthesis-v1/spec.yaml
```

## LES stress

Primary: **Effectiveness**, **Cost**, **Adaptability**
