# Contributing to LoopBench

## What belongs here

- Benchmark task definitions (ALS v2 YAML)
- Comparison suite registry (`tasks/suites/`)
- Observed LES computation and submission schema
- CLI, conformance validation, leaderboard entries
- Golden submission tests

## What does not belong here

- LSS schema — [Loop Core Engineering](https://github.com/KanakMalpani/Loop-Core-Engineering)
- Environment runtime — [LoopGym](https://github.com/KanakMalpani/LoopGym)
- Dataset records — [LoopNet](https://github.com/KanakMalpani/loopnet)

## Before opening a PR

```bash
pip install -e ../LoopGym   # or deps/LoopGym in CI layout
pip install -e ".[dev]"
pytest tests/ -q
loopbench validate leaderboard/entries.json
```

## Submitting benchmark results

Run a full suite (recommended for generalist rank):

```bash
loopbench run --suite suite-repair --spec your-loop.yaml --seeds 0,1,2,3,4 -o results.json
loopbench validate results.json
```

Other suites: `suite-agent`, `suite-knowledge`, `suite-rigor`. For a single micro-task:

```bash
loopbench run --task LB-CR-1 --spec your-loop.yaml --seeds 0,1,2,3,4 -o results.json
```

Include a `repro_command` in your leaderboard entry when possible:

```json
"repro_command": "loopbench run --suite suite-repair --spec your-loop.yaml --seeds 0,1,2,3,4 -o results.json"
```

Open a PR adding your entry to `leaderboard/entries.json`. Entries with all four `suite_scores` qualify for **generalist** rank.

## License

MIT — see [LICENSE](LICENSE).
