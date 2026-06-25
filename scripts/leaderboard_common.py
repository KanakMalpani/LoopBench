#!/usr/bin/env python3
"""Shared leaderboard parsing and markdown rendering for LoopBench entries.json."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

LEADERBOARD_URL = (
    "https://raw.githubusercontent.com/KanakMalpani/LoopBench/main/leaderboard/entries.json"
)
LIVE_MD_URL = (
    "https://raw.githubusercontent.com/KanakMalpani/LoopBench/main/leaderboard/LIVE.md"
)

INTERNAL_SUBMITTER_MARKERS = (
    "loop engineering maintainer",
    "team thorough",
    "team fast",
    "golden",
    "local-dev",
)

KNOWN_TASKS = ("LB-CR-1", "LB-RS-1", "LB-MA-1", "LB-COMP-1")

TASK_META: dict[str, dict[str, str | int]] = {
    "LB-CR-1": {
        "name": "Code repair",
        "tagline": "Fix broken code under test-suite verify pressure.",
        "language": "SimEnv",
        "seeds": 5,
    },
    "LB-RS-1": {
        "name": "Research synthesis",
        "tagline": "Structured briefs — quality vs cost under evaluator scrutiny.",
        "language": "SimEnv",
        "seeds": 5,
    },
    "LB-MA-1": {
        "name": "Multi-agent debate",
        "tagline": "Autonomy and coordination under multi-evaluator pressure.",
        "language": "SimEnv",
        "seeds": 5,
    },
    "LB-COMP-1": {
        "name": "Composed swarm",
        "tagline": "Parallel branches + merge — MiroFish-style LSS composition.",
        "language": "SimEnv",
        "seeds": 5,
    },
}


@dataclass
class TaskRow:
    submitter: str
    task_id: str
    les_observed: float
    les_display: float
    success_at_k: float
    spec_path: str
    repro_command: str
    harness: str
    submission_id: str
    is_external: bool


def fetch_json(url: str) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": "loop-engineering-leaderboard"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def load_entries_from_url(url: str = LEADERBOARD_URL) -> dict[str, Any]:
    return fetch_json(url)


def load_entries_from_file(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def is_internal_submitter(name: str) -> bool:
    lower = (name or "").lower()
    return any(marker in lower for marker in INTERNAL_SUBMITTER_MARKERS)


def _loop_name_from_spec(spec_path: str) -> str:
    if not spec_path:
        return "unknown"
    base = spec_path.rstrip("/").split("/")[-1]
    return re.sub(r"\.ya?ml$", "", base, flags=re.I)


def _repro_command(entry: dict[str, Any], task_id: str, spec_path: str) -> str:
    if entry.get("repro_command"):
        return str(entry["repro_command"])
    spec = spec_path or entry.get("spec_path", "your-loop.yaml")
    if spec.startswith("http"):
        spec = _loop_name_from_spec(spec) + ".yaml"
    return f"loopbench run --task {task_id} --spec {spec} --seeds 0,1,2,3,4 -o results.json"


def flatten_entries(board: dict[str, Any]) -> list[TaskRow]:
    rows: list[TaskRow] = []
    for entry in board.get("entries") or []:
        submitter = str(entry.get("submitter", "?"))
        spec_path = str(entry.get("spec_path") or entry.get("spec_uri") or "")
        harness = str(entry.get("harness") or "native")
        submission_id = str(entry.get("submission_id") or "")
        external = not is_internal_submitter(submitter)

        for result in entry.get("results") or []:
            task_id = str(result.get("task_id", ""))
            if not task_id:
                continue
            agg = result.get("aggregate") or {}
            les_obs = float(agg.get("les_observed") or 0.0)
            les_display = float(agg.get("les_display") or les_obs * 100)
            success = float(agg.get("success_at_k") or 0.0)
            rows.append(
                TaskRow(
                    submitter=submitter,
                    task_id=task_id,
                    les_observed=les_obs,
                    les_display=les_display,
                    success_at_k=success,
                    spec_path=spec_path,
                    repro_command=_repro_command(entry, task_id, spec_path),
                    harness=harness,
                    submission_id=submission_id,
                    is_external=external,
                )
            )
    return rows


def rank_by_task(rows: list[TaskRow], top_n: int = 10, external_only: bool = False) -> dict[str, list[TaskRow]]:
    by_task: dict[str, list[TaskRow]] = {t: [] for t in KNOWN_TASKS}
    for row in rows:
        if external_only and not row.is_external:
            continue
        if row.task_id in by_task:
            by_task[row.task_id].append(row)

    ranked: dict[str, list[TaskRow]] = {}
    for task_id, task_rows in by_task.items():
        task_rows.sort(key=lambda r: (r.les_observed, r.success_at_k), reverse=True)
        ranked[task_id] = task_rows[:top_n]
    return ranked


def render_task_table(task_id: str, rows: list[TaskRow], *, show_internal: bool = True) -> list[str]:
    lines = [f"### {task_id}", ""]
    if not rows:
        lines.append("_No entries yet._")
        lines.append("")
        return lines

    lines.extend(
        [
            "| Rank | Submitter | LES | Success@k | Spec |",
            "|------|-----------|-----|-----------|------|",
        ]
    )
    for i, row in enumerate(rows, 1):
        spec_link = row.spec_path if row.spec_path.startswith("http") else f"`{row.spec_path}`"
        tag = "" if row.is_external or show_internal else ""
        submitter = row.submitter + (" *" if row.is_external else "")
        lines.append(
            f"| {i} | {submitter} | {row.les_display:.1f} | {row.success_at_k:.2f} | {spec_link} |"
        )
    lines.append("")
    if any(r.is_external for r in rows):
        lines.append("_\\* external submitter_")
        lines.append("")
    return lines


def render_live_markdown(
    board: dict[str, Any],
    *,
    top_n: int = 10,
    external_only: bool = False,
    generated_note: str = "Auto-generated from `leaderboard/entries.json`. Do not edit manually.",
) -> str:
    rows = flatten_entries(board)
    ranked = rank_by_task(rows, top_n=top_n, external_only=external_only)
    updated = board.get("updated", "unknown")

    lines = [
        "# LoopBench — live leaderboard",
        "",
        f"_Updated: {updated}_",
        "",
        generated_note,
        "",
        "Rankings use **LES_obs** (aggregate) per task. Top 10 per task.",
        "",
    ]
    for task_id in KNOWN_TASKS:
        lines.extend(render_task_table(task_id, ranked.get(task_id, [])))
    return "\n".join(lines) + "\n"


def render_readme_block(board: dict[str, Any], *, top_n: int = 5) -> str:
    """Compact block for README between LEADERBOARD markers."""
    rows = flatten_entries(board)
    ranked = rank_by_task(rows, top_n=top_n, external_only=False)
    updated = board.get("updated", "unknown")

    lines = [
        f"**Live board** (updated {updated}) — [full rankings](leaderboard/LIVE.md)",
        "",
    ]
    for task_id in KNOWN_TASKS:
        top = ranked.get(task_id, [])
        if not top:
            lines.append(f"- **{task_id}:** _no entries_")
            continue
        leader = top[0]
        ext = " (external)" if leader.is_external else ""
        lines.append(
            f"- **{task_id}:** {leader.submitter}{ext} — LES **{leader.les_display:.1f}**"
        )
    lines.append("")
    lines.append("[Submit your loop →](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/LOOP_PLAYGROUND.md)")
    return "\n".join(lines)


def _loop_name_from_entry(row: TaskRow) -> str:
    return _loop_name_from_spec(row.spec_path)


def export_site_json(board: dict[str, Any], *, top_n: int = 20) -> dict[str, Any]:
    rows = flatten_entries(board)
    ranked = rank_by_task(rows, top_n=top_n, external_only=False)
    tasks_out: dict[str, Any] = {}
    for task_id in KNOWN_TASKS:
        meta = TASK_META.get(task_id, {})
        entries = []
        for rank, row in enumerate(ranked.get(task_id, []), 1):
            cost = 0.0
            for entry in board.get("entries") or []:
                if str(entry.get("submitter")) != row.submitter:
                    continue
                for result in entry.get("results") or []:
                    if result.get("task_id") == task_id:
                        cost = float((result.get("aggregate") or {}).get("cost_usd_mean") or 0)
                        break
            entries.append(
                {
                    "rank": rank,
                    "submitter": row.submitter,
                    "loop_name": _loop_name_from_entry(row),
                    "les_observed": round(row.les_observed, 4),
                    "les_display": round(row.les_display, 1),
                    "success_at_k": round(row.success_at_k, 3),
                    "cost_usd_mean": round(cost, 4),
                    "spec_path": row.spec_path,
                    "repro_command": row.repro_command,
                    "harness": row.harness,
                    "is_external": row.is_external,
                    "submission_id": row.submission_id,
                }
            )
        tasks_out[task_id] = {
            "id": task_id,
            "name": meta.get("name", task_id),
            "tagline": meta.get("tagline", ""),
            "seeds": meta.get("seeds", 5),
            "entries": entries,
        }
    return {
        "version": board.get("version", "0.1.0"),
        "updated": board.get("updated", "unknown"),
        "entry_count": len(board.get("entries") or []),
        "tasks": tasks_out,
    }


def inject_readme_markers(readme_text: str, block: str) -> str:
    start = "<!-- LEADERBOARD:START -->"
    end = "<!-- LEADERBOARD:END -->"
    inner = f"{start}\n<!-- auto-generated; do not edit -->\n{block}\n{end}"
    pattern = re.compile(
        re.escape(start) + r"[\s\S]*?" + re.escape(end),
        re.MULTILINE,
    )
    if pattern.search(readme_text):
        return pattern.sub(inner, readme_text, count=1)
    return readme_text.rstrip() + "\n\n" + inner + "\n"
