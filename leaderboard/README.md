# LoopBench Leaderboard (static JSON v0.1)

Public rankings for LoopBench submissions. v0.2 adds web UI and signed attestations.

## Ranking rule

Sort by `composite.rank_score` (= mean task `les_observed`) descending. Ties broken by higher `success_at_k` mean, then lower `cost_usd_mean`.

## Submit

1. Run `loopbench run --task LB-CR-1,LB-RS-1,LB-MA-1 --spec your-loop.yaml -o results.json`
2. Validate: `loopbench validate results.json`
3. Open PR adding your entry to `entries.json`

## Example entries

See [`entries.json`](./entries.json) — golden submissions from CI and local dev fixtures.

## Fields

| Field | Description |
|-------|-------------|
| `submitter` | Team or individual name |
| `composite.les_observed` | Suite mean LES `[0,1]` |
| `composite.les_display` | Human-readable `0–100` |
| `spec_hash` | SHA-256 of submitted LSS file |
| `backend` | `sim` (default CI) or `live` |

## Pins

- `lss@1.0.0`, `les@1.0.0`, `loopbench@0.1.0`
