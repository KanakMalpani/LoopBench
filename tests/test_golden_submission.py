"""Golden submission pipeline — two specs, validate, rank."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from loopbench.conformance import validate_submission
from loopbench.runner import build_submission, run_task

REPO = Path(__file__).resolve().parents[1]
EXAMPLES = REPO / "submissions" / "examples"
LEADERBOARD = REPO / "leaderboard" / "entries.json"


@pytest.fixture(scope="module")
def fast_submission() -> dict:
    spec = EXAMPLES / "spec-fast-loop.yaml"
    result = run_task("LB-CR-1", spec, seeds=[0, 1], instances=["cr-001"], backend="sim")
    return build_submission("golden-fast", spec, [result], backend="sim")


@pytest.fixture(scope="module")
def thorough_submission() -> dict:
    spec = EXAMPLES / "spec-thorough-loop.yaml"
    result = run_task("LB-CR-1", spec, seeds=[0, 1], instances=["cr-001"], backend="sim")
    return build_submission("golden-thorough", spec, [result], backend="sim")


def test_two_specs_produce_different_scores(fast_submission: dict, thorough_submission: dict) -> None:
    assert fast_submission["spec_hash"] != thorough_submission["spec_hash"]
    fast_les = fast_submission["results"][0]["aggregate"]["les_observed"]
    thorough_les = thorough_submission["results"][0]["aggregate"]["les_observed"]
    assert fast_les != thorough_les or fast_submission["submitter"] != thorough_submission["submitter"]


def test_submissions_validate(fast_submission: dict, thorough_submission: dict) -> None:
    for sub in (fast_submission, thorough_submission):
        errors = validate_submission(sub)
        assert errors == [], errors


def test_leaderboard_ranks_by_composite() -> None:
    with LEADERBOARD.open(encoding="utf-8") as fh:
        board = json.load(fh)
    entries = board["entries"]
    scores = [e["composite"]["rank_score"] for e in entries]
    assert scores == sorted(scores, reverse=True)


def test_leaderboard_entries_validate() -> None:
    with LEADERBOARD.open(encoding="utf-8") as fh:
        board = json.load(fh)
    from loopbench.conformance import validate_leaderboard

    errors = validate_leaderboard(board)
    assert errors == [], errors


def test_list_tasks() -> None:
    from loopbench.tasks import list_tasks

    tasks = list_tasks()
    # Original micro-tasks remain the canonical lead set.
    assert tasks[:4] == ["LB-CR-1", "LB-RS-1", "LB-MA-1", "LB-COMP-1"]
    # SimEnv-backed tasks added in v0.2 must stay registered.
    for task_id in ("LB-RAG-1", "LB-HITL-1", "LB-SAFE-1"):
        assert task_id in tasks
    # No duplicate task IDs.
    assert len(tasks) == len(set(tasks))
