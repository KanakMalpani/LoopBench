# Leaderboard row schema (v0.1.1)

Extensions for **new** PRs to `leaderboard/entries.json`. Existing v0.1 rows remain valid.

---

## Required on entry object

| Field | Type | Description |
|-------|------|-------------|
| `submitter` | string | GitHub org or handle (non-maintainer for community credit) |
| `spec_path` | string | HTTPS URL to LSS YAML |
| `spec_hash` | string | `sha256:...` of spec bytes |
| `results` | array | LoopBench results with `task_id` + `aggregate` |
| `repro_command` | string | Single-line repro, e.g. `loopbench run --task LB-CR-1 --spec my.yaml --seeds 0,1,2,3,4 -o results.json` |

---

## Recommended

| Field | Type | Description |
|-------|------|-------------|
| `harness` | string | `native`, `cursor`, `langgraph`, `crewai`, … |
| `trace_uri` | string | Loop Trace JSON URL |
| `verified_external` | boolean | Set `true` by maintainer after merge review |
| `notes` | string | One-line harness or tuning note |

---

## PR checklist

1. `loopbench validate results.json` passes locally
2. Seeds documented (default `0,1,2,3,4`)
3. `repro_command` matches your actual run
4. Reference [Loop Playground](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/LOOP_PLAYGROUND.md)
5. Reference good-first issue ([#4](https://github.com/KanakMalpani/Loop-Engineering/issues/4) for LB-CR-1)

Template: [external-template-row.json](https://github.com/KanakMalpani/Loop-Engineering/blob/main/docs/submission-dry-run/external-template-row.json)

---

## Anti-gaming

- Maintainer / bot rows excluded from external adoption signals
- Human merge required
- Spec hash must match submitted YAML
