# LoopBench Live tier policy (v0.2 draft)

SimEnv (`--backend sim`) remains the **default** for leaderboard eligibility in v0.2.

## Backends

| Backend | API keys | Leaderboard |
|---------|----------|-------------|
| `sim` | No | Eligible (primary) |
| `live` | Yes (provider env vars) | Separate column (v0.3+) |
| `replay` | No | Analysis only — not ranked |

## Live run requirements (when enabled)

```bash
export OPENAI_API_KEY=...
loopbench run --suite suite-repair --spec my.yaml --backend live --seeds 0,1,2,3,4 -o results.json
```

Submissions must include:

- `backend: "live"`
- Model IDs used (in spec or submission notes)
- Total `cost_usd` from provider billing or Loop Trace
- Same `spec_hash` and seeds as SimEnv tier

## Cost caps

- Respect LSS `cost_limits` in the spec
- Maintainer review rejects runs with `cost_usd_mean` > 10× SimEnv baseline without justification

## Leaderboard display

Live rows appear in a **Live** filter on GitHub Pages (planned v0.3). Generalist rank remains SimEnv-only until dual-tier policy is finalized.
