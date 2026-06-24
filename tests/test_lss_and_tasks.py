"""Validate submission LSS specs against Loop Core Engineering schema."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
EXAMPLES = REPO / "submissions" / "examples"


def _core_root() -> Path | None:
    for candidate in (
        REPO.parent / "01-loop-engineering-core",
        REPO.parent / "Loop-Core-Engineering",
        REPO / "deps" / "loop-core",
    ):
        validator = candidate / "tools" / "validate_lss.py"
        if validator.exists():
            return candidate
    return None


CORE = _core_root()
VALIDATOR = (CORE / "tools" / "validate_lss.py") if CORE else None


@pytest.mark.skipif(VALIDATOR is None, reason="Loop Core Engineering not found")
@pytest.mark.parametrize(
    "spec_file",
    [
        EXAMPLES / "spec-fast-loop.yaml",
        EXAMPLES / "spec-thorough-loop.yaml",
    ],
)
def test_submission_specs_validate_against_lss(spec_file: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), str(spec_file)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout


@pytest.mark.parametrize("task_id", ["LB-CR-1", "LB-RS-1", "LB-MA-1", "LB-COMP-1"])
def test_smoke_run_all_tasks(task_id: str) -> None:
    from loopbench.runner import run_task

    spec = EXAMPLES / "spec-fast-loop.yaml"
    result = run_task(task_id, spec, seeds=[0], instances=None, backend="sim")
    assert result["task_id"] == task_id
    assert result["aggregate"]["les_observed"] >= 0.0
    assert len(result["runs"]) >= 1
