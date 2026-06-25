# LoopBench leaderboard

Public rankings from [`entries.json`](./entries.json).

| File | Purpose |
|------|---------|
| [`entries.json`](./entries.json) | Canonical submission data (PR to add rows) |
| [`LIVE.md`](./LIVE.md) | Auto-generated top 20 per task (do not edit) |
| [`ROW_SCHEMA.md`](./ROW_SCHEMA.md) | Required fields for new submissions |

---

## Ranking rules

| Task | Primary metric | Tie-break |
|------|----------------|-----------|
| LB-CR-1 | `aggregate.les_observed` | `success_at_k` |
| LB-RS-1 | same | same |
| LB-MA-1 | same | same |
| LB-COMP-1 | same | same |

- Top **10** per task in `LIVE.md`
- **Internal** maintainer baselines appear but are marked; external submitters show `*`
- Merge requires human review — no auto-merge

---

## Regenerate locally

```bash
python scripts/render_leaderboard.py --entries leaderboard/entries.json --readme README.md
```

CI runs [leaderboard-render.yml](../.github/workflows/leaderboard-render.yml) on `entries.json` changes and weekly.

---

## Submit

Start at [Loop Playground](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/LOOP_PLAYGROUND.md) on Loop-Engineering.
