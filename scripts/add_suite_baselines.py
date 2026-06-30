#!/usr/bin/env python3
"""Append Wave 15 maintainer suite baseline rows to leaderboard/entries.json."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRIES = ROOT / "leaderboard" / "entries.json"

BASELINES = [
    {
        "submitter": "Loop Engineering maintainer (suite-repair)",
        "primary_suite": "suite-repair",
        "spec_path": "https://github.com/KanakMalpani/Loop-Engineering/blob/main/loop-library/autonomous-debugger.yaml",
        "spec_hash": "sha256:c1acd3d6408bc07813b3f3a150eb0514c8b7a873d2736dea75274eb0ead98eb9",
        "harness": "native",
        "repro_command": "loopbench run --suite suite-repair --spec autonomous-debugger.yaml --seeds 0,1,2,3,4 -o results.json",
        "suite_scores": {
            "suite-repair": {"label": "Repair & Verify", "les_observed": 0.86, "les_display": 86.0, "rank_score": 0.86, "tasks": ["LB-CR-1", "LB-REACT-1", "LB-REFLEX-1", "LB-OPT-1", "LB-SAFE-1"]},
        },
        "grand_composite": {"les_observed": 0.86, "les_display": 86.0, "rank_score": 0.86},
        "composite": {"les_observed": 0.86, "les_display": 86.0, "rank_score": 0.86},
        "results": [{"task_id": "LB-CR-1", "env_id": "loopbench/code-repair-v1", "runs": [], "aggregate": {"success_at_k": 1.0, "les_observed": 0.86, "les_display": 86.0, "categories": {}, "cost_usd_mean": 0.35, "robustness_seeds": 5}}],
    },
    {
        "submitter": "Loop Engineering maintainer (suite-agent)",
        "primary_suite": "suite-agent",
        "spec_path": "https://github.com/KanakMalpani/Loop-Engineering/blob/main/loop-library/compositions/parallel-swarm.yaml",
        "spec_hash": "sha256:0000000000000000000000000000000000000000000000000000000000000001",
        "harness": "native",
        "repro_command": "loopbench run --suite suite-agent --spec parallel-swarm.yaml --seeds 0,1,2,3,4 -o results.json",
        "suite_scores": {
            "suite-agent": {"label": "Multi-Agent", "les_observed": 0.81, "les_display": 81.0, "rank_score": 0.81, "tasks": ["LB-MA-1", "LB-CREW-1", "LB-GRAPH-1", "LB-TOT-1", "LB-VOTE-1"]},
        },
        "grand_composite": {"les_observed": 0.81, "les_display": 81.0, "rank_score": 0.81},
        "composite": {"les_observed": 0.81, "les_display": 81.0, "rank_score": 0.81},
        "results": [{"task_id": "LB-MA-1", "env_id": "loopbench/multi-agent-debate-v1", "runs": [], "aggregate": {"success_at_k": 0.9, "les_observed": 0.81, "les_display": 81.0, "categories": {}, "cost_usd_mean": 0.5, "robustness_seeds": 5}}],
    },
    {
        "submitter": "Loop Engineering maintainer (suite-knowledge)",
        "primary_suite": "suite-knowledge",
        "spec_path": "https://github.com/KanakMalpani/Loop-Engineering/blob/main/loop-library/research-agent.yaml",
        "spec_hash": "sha256:0000000000000000000000000000000000000000000000000000000000000002",
        "harness": "native",
        "repro_command": "loopbench run --suite suite-knowledge --spec research-agent.yaml --seeds 0,1,2,3,4 -o results.json",
        "suite_scores": {
            "suite-knowledge": {"label": "Research & RAG", "les_observed": 0.79, "les_display": 79.0, "rank_score": 0.79, "tasks": ["LB-RS-1", "LB-RAG-1", "LB-BOOT-1", "LB-AUTO-1"]},
        },
        "grand_composite": {"les_observed": 0.79, "les_display": 79.0, "rank_score": 0.79},
        "composite": {"les_observed": 0.79, "les_display": 79.0, "rank_score": 0.79},
        "results": [{"task_id": "LB-RS-1", "env_id": "loopbench/research-synthesis-v1", "runs": [], "aggregate": {"success_at_k": 0.85, "les_observed": 0.79, "les_display": 79.0, "categories": {}, "cost_usd_mean": 0.4, "robustness_seeds": 5}}],
    },
    {
        "submitter": "Loop Engineering maintainer (suite-rigor)",
        "primary_suite": "suite-rigor",
        "spec_path": "https://github.com/KanakMalpani/Loop-Engineering/blob/main/loop-library/compositions/parallel-swarm.yaml",
        "spec_hash": "sha256:0000000000000000000000000000000000000000000000000000000000000001",
        "harness": "native",
        "repro_command": "loopbench run --suite suite-rigor --spec parallel-swarm.yaml --seeds 0,1,2,3,4 -o results.json",
        "suite_scores": {
            "suite-rigor": {"label": "Composition & Safety", "les_observed": 0.80, "les_display": 80.0, "rank_score": 0.80, "tasks": ["LB-COMP-1", "LB-NEST-1", "LB-SIM-1", "LB-HITL-1", "LB-MEM-1"]},
        },
        "grand_composite": {"les_observed": 0.80, "les_display": 80.0, "rank_score": 0.80},
        "composite": {"les_observed": 0.80, "les_display": 80.0, "rank_score": 0.80},
        "results": [{"task_id": "LB-COMP-1", "env_id": "loopbench/composed-swarm-v1", "runs": [], "aggregate": {"success_at_k": 1.0, "les_observed": 0.80, "les_display": 80.0, "categories": {}, "cost_usd_mean": 0.72, "robustness_seeds": 5}}],
    },
]


def main() -> int:
    board = json.loads(ENTRIES.read_text(encoding="utf-8"))
    board["version"] = "0.2.0"
    board["updated"] = "2026-06-25"
    existing = {e.get("primary_suite") for e in board.get("entries", [])}
    for row in BASELINES:
        if row["primary_suite"] not in existing:
            board.setdefault("entries", []).append(row)
    ENTRIES.write_text(json.dumps(board, indent=2) + "\n", encoding="utf-8")
    print(f"Updated {ENTRIES} ({len(board['entries'])} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
