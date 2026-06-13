# Contributing to LoopBench

## What belongs here

- Benchmark task definitions (ALS v2 YAML)
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

1. Run all tasks: `loopbench run --task LB-CR-1,LB-RS-1,LB-MA-1 --spec your-loop.yaml -o results.json`
2. Validate: `loopbench validate results.json`
3. Open a PR adding your entry to `leaderboard/entries.json`

## License

MIT — see [LICENSE](LICENSE).
