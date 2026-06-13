"""Load LoopBench task definitions."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
TASKS_ROOT = REPO_ROOT / "tasks"


def list_tasks() -> list[str]:
    index_path = TASKS_ROOT / "index.yaml"
    if not index_path.exists():
        return []
    with index_path.open(encoding="utf-8") as fh:
        index = yaml.safe_load(fh)
    return [t["id"] for t in index.get("tasks", [])]


def load_task(task_id: str) -> dict:
    task_path = TASKS_ROOT / task_id / "task.yaml"
    if not task_path.exists():
        available = ", ".join(list_tasks())
        raise FileNotFoundError(f"Unknown task '{task_id}'. Available: {available}")
    with task_path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"Invalid task spec: {task_path}")
    return data


def speed_baselines(task: dict) -> tuple[float, float]:
    sb = task.get("speed_baselines") or {}
    return (
        float(sb.get("b_floor_iter_per_s", 0.001)),
        float(sb.get("b_ceiling_iter_per_s", 0.05)),
    )


def cost_baselines(task: dict) -> tuple[float, float]:
    cb = task.get("cost_baselines") or {}
    return (
        float(cb.get("b_floor_efficiency", 0.05)),
        float(cb.get("b_ceiling_efficiency", 2.0)),
    )
