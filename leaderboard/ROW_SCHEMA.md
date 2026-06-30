# Leaderboard row schema (v0.2.0)

Extensions for **new** PRs to `leaderboard/entries.json`. Existing v0.1 rows remain valid.

---

## Required on entry object

| Field | Type | Description |
|-------|------|-------------|
| `submitter` | string | GitHub org or handle (non-maintainer for community credit) |
| `spec_path` | string | HTTPS URL to LSS YAML |
| `spec_hash` | string | `sha256:...` of spec bytes |
| `results` | array | LoopBench results with `task_id` + `aggregate` |
| `repro_command` | string | Single-line repro, e.g. `loopbench run --suite suite-repair --spec my.yaml --seeds 0,1,2,3,4 -o results.json` |

---

## Recommended (Wave 15 — suite rankings)

| Field | Type | Description |
|-------|------|-------------|
| `suite_scores` | object | Per-suite LES from `loopbench run --suite …` or full micro-task run |
| `grand_composite` | object | Mean of suite scores — **primary generalist rank** |
| `composite` | object | Same as `grand_composite` when suites present; else task mean |
| `primary_suite` | string | Optional tab hint: `suite-repair`, `suite-agent`, `suite-knowledge`, `suite-rigor` |
| `partial` | boolean | Set `true` when fewer than 4 suite scores; **excluded from generalist rank** |
| `harness` | string | `native`, `cursor`, `langgraph`, `crewai`, … |
| `trace_uri` | string | Loop Trace JSON URL |
| `verified_external` | boolean | Set `true` by maintainer after merge review |
| `notes` | string | One-line harness or tuning note |

**Ranking:** Generalist tab uses `grand_composite.rank_score` (fallback: `composite`). Suite tabs use `suite_scores.<suite-id>.rank_score`.

---

## PR checklist

1. `loopbench validate results.json` passes locally
2. Seeds documented (default `0,1,2,3,4`)
3. `repro_command` matches your actual run (`--suite` preferred over flat `--task` lists)
4. Include `suite_scores` + `grand_composite` when running multiple suite tasks
5. Reference [Loop Playground](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/LOOP_PLAYGROUND.md)

Template: [external-template-row.json](https://github.com/KanakMalpani/Loop-Engineering/blob/main/docs/submission-dry-run/external-template-row.json)

---

## Anti-gaming

- Maintainer / bot rows excluded from external adoption signals
- Human merge required
- Spec hash must match submitted YAML
Generate maintainer suite baselines (requires loopgym):

```bash
python scripts/run_suite_baselines.py
```

Entries with `partial: true` or fewer than 4 `suite_scores` are excluded from the **generalist** tab.
