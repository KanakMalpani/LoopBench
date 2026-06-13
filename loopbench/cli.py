"""LoopBench CLI — local eval, validate, rank."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from loopbench import __version__
from loopbench.conformance import validate_file
from loopbench.runner import build_submission, run_task
from loopbench.tasks import list_tasks


def _parse_seeds(raw: str) -> list[int]:
    return [int(s.strip()) for s in raw.split(",") if s.strip()]


def cmd_list(_args: argparse.Namespace) -> int:
    print("LoopBench tasks:")
    for task_id in list_tasks():
        print(f"  {task_id}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    spec_path = Path(args.spec)
    if not spec_path.exists():
        print(f"Error: spec not found: {spec_path}", file=sys.stderr)
        return 2

    seeds = _parse_seeds(args.seeds) if args.seeds else None
    task_ids = args.task.split(",") if args.task else ["LB-CR-1"]
    task_results = []
    for task_id in task_ids:
        print(f"Running {task_id} via LoopGym (backend={args.backend})...", file=sys.stderr)
        task_results.append(
            run_task(
                task_id.strip(),
                spec_path,
                seeds=seeds,
                backend=args.backend,
            )
        )

    submission = build_submission(
        args.submitter,
        spec_path,
        task_results,
        backend=args.backend,
    )

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(submission, indent=2), encoding="utf-8")
        print(f"Wrote {out}", file=sys.stderr)
    else:
        print(json.dumps(submission, indent=2))

    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    path = Path(args.file)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 2
    valid, errors = validate_file(path)
    if args.json:
        print(json.dumps({"valid": valid, "errors": errors}, indent=2))
    elif valid:
        print(f"VALID: {path}")
    else:
        print(f"INVALID: {path}", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
    return 0 if valid else 1


def cmd_rank(args: argparse.Namespace) -> int:
    path = Path(args.file)
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)

    entries = data if isinstance(data, list) else data.get("entries", [])
    ranked = sorted(
        entries,
        key=lambda e: e.get("composite", {}).get("rank_score", 0.0),
        reverse=True,
    )
    print(f"{'Rank':<6}{'Submitter':<24}{'LES':>8}{'Display':>10}{'Backend':>10}")
    print("-" * 58)
    for i, entry in enumerate(ranked, 1):
        comp = entry.get("composite", {})
        print(
            f"{i:<6}{entry.get('submitter', '?')[:24]:<24}"
            f"{comp.get('les_observed', 0):>8.4f}"
            f"{comp.get('les_display', 0):>10.1f}"
            f"{entry.get('backend', '?'):>10}"
        )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=f"LoopBench CLI v{__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List benchmark tasks")
    p_list.set_defaults(func=cmd_list)

    p_run = sub.add_parser("run", help="Run local evaluation via LoopGym")
    p_run.add_argument("--task", default="LB-CR-1", help="Task ID or comma-separated list")
    p_run.add_argument("--spec", required=True, help="Path to LSS YAML spec")
    p_run.add_argument("--seeds", default="0,1,2,3,4", help="Comma-separated seeds")
    p_run.add_argument("--submitter", default="local-dev", help="Submitter name")
    p_run.add_argument("--backend", default="sim", choices=["sim", "live", "replay"])
    p_run.add_argument("--output", "-o", help="Write results JSON to path")
    p_run.set_defaults(func=cmd_run)

    p_val = sub.add_parser("validate", help="Validate submission JSON")
    p_val.add_argument("file", help="Results JSON path")
    p_val.add_argument("--json", action="store_true")
    p_val.set_defaults(func=cmd_validate)

    p_rank = sub.add_parser("rank", help="Rank leaderboard entries by composite LES")
    p_rank.add_argument("file", help="Leaderboard JSON path")
    p_rank.set_defaults(func=cmd_rank)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
