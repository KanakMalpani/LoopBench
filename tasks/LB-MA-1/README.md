# LB-MA-1 — Multi-Agent Debate

**LoopGym env:** `loopbench/multi-agent-debate-v1`

Given a proposal, advocate and critic agents debate; a judge produces consensus with score ≥ 0.88.

## Goal function

```
G = 0.40 × balance + 0.60 × actionability
G_target = 0.88
```

## Task instances

| Instance | Risk tier | ID |
|----------|-----------|-----|
| Refresh token rotation | high | `ma-001` |
| Redis session migration | medium | `ma-002` |
| Structured logging | low | `ma-003` |

## Run locally

```bash
loopbench run --task LB-MA-1 --spec ../05-loopgym/envs/loopbench/multi-agent-debate-v1/spec.yaml
```

## LES stress

Primary: **Effectiveness**, **Autonomy**, **Scalability**
