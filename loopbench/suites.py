"""Load LoopBench comparison suites."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
_PACKAGED = Path(__file__).resolve().parent / "tasks" / "suites"
_SUITES_ROOT = _PACKAGED if (_PACKAGED / "index.yaml").is_file() else REPO_ROOT / "tasks" / "suites"


def _suites_index_path() -> Path:
    return _SUITES_ROOT / "index.yaml"


def list_suites() -> list[str]:
    path = _suites_index_path()
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return [s["id"] for s in data.get("suites", [])]


def load_suite(suite_id: str) -> dict:
    path = _suites_index_path()
    if not path.exists():
        raise FileNotFoundError("Suite registry not found")
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    for suite in data.get("suites", []):
        if suite.get("id") == suite_id:
            return suite
    available = ", ".join(list_suites())
    raise KeyError(f"Unknown suite {suite_id!r}. Available: {available}")


def suite_task_ids(suite_id: str) -> list[str]:
    suite = load_suite(suite_id)
    return list(suite.get("task_ids") or [])


def all_suite_task_ids() -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for sid in list_suites():
        for tid in suite_task_ids(sid):
            if tid not in seen:
                seen.add(tid)
                out.append(tid)
    return out
