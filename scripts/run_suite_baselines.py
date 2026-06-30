#!/usr/bin/env python3
"""Run maintainer suite baselines and merge into leaderboard/entries.json."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LE = Path(__file__).resolve().parents[2] / "01-loop-engineering"
ENTRIES = ROOT / "leaderboard" / "entries.json"

SUITES = [
    {
        "primary_suite": "suite-repair",
        "submitter": "Loop Engineering maintainer (suite-repair)",
        "spec": LE / "loop-library" / "autonomous-debugger.yaml",
        "harness": "native",
    },
    {
        "primary_suite": "suite-agent",
        "submitter": "Loop Engineering maintainer (suite-agent)",
        "spec": LE / "loop-library" / "compositions" / "scenario-swarm-rehearsal.yaml",
        "harness": "native",
    },
    {
        "primary_suite": "suite-knowledge",
        "submitter": "Loop Engineering maintainer (suite-knowledge)",
        "spec": LE / "loop-library" / "research-agent.yaml",
        "harness": "native",
    },
    {
        "primary_suite": "suite-rigor",
        "submitter": "Loop Engineering maintainer (suite-rigor)",
        "spec": LE / "loop-library" / "compositions" / "code-debug-repair.yaml",
        "harness": "native",
    },
]


def run_suite(cfg: dict) -> dict:
    spec = cfg["spec"]
    if not spec.is_file():
        raise FileNotFoundError(spec)
    out = Path(tempfile.gettempdir()) / f"baseline-{cfg['primary_suite']}.json"
    cmd = [
        sys.executable,
        "-m",
        "loopbench",
        "run",
        "--suite",
        cfg["primary_suite"],
        "--spec",
        str(spec),
        "--seeds",
        "0,1,2,3,4",
        "--submitter",
        cfg["submitter"],
        "-o",
        str(out),
    ]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"{cfg['primary_suite']}: {proc.stderr or proc.stdout}")
    data = json.loads(out.read_text(encoding="utf-8"))
    data["harness"] = cfg["harness"]
    data["repro_command"] = (
        f"loopbench run --suite {cfg['primary_suite']} --spec {spec.name} "
        f"--seeds 0,1,2,3,4 -o results.json"
    )
    data["primary_suite"] = cfg["primary_suite"]
    data["partial"] = len(data.get("suite_scores") or {}) < 4
    return data


def main() -> int:
    board = json.loads(ENTRIES.read_text(encoding="utf-8"))
    board["version"] = "0.2.0"
    board["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    entries = [
        e
        for e in board.get("entries", [])
        if "(suite-repair)" not in str(e.get("submitter", ""))
        and "(suite-agent)" not in str(e.get("submitter", ""))
        and "(suite-knowledge)" not in str(e.get("submitter", ""))
        and "(suite-rigor)" not in str(e.get("submitter", ""))
    ]

    for cfg in SUITES:
        print(f"Running {cfg['primary_suite']}...", file=sys.stderr)
        entries.append(run_suite(cfg))

    board["entries"] = entries
    ENTRIES.write_text(json.dumps(board, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {ENTRIES} ({len(entries)} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
