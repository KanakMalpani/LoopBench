#!/usr/bin/env python3
"""Shared leaderboard parsing — generalist + per-suite tabs (Wave 15)."""

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

KNOWN_TASKS = (
    "LB-CR-1",
    "LB-RS-1",
    "LB-MA-1",
    "LB-COMP-1",
    "LB-REACT-1",
    "LB-GRAPH-1",
    "LB-CREW-1",
    "LB-REFLEX-1",
    "LB-AUTO-1",
    "LB-RAG-1",
    "LB-OPT-1",
    "LB-TOT-1",
    "LB-VOTE-1",
    "LB-HITL-1",
    "LB-SAFE-1",
    "LB-MEM-1",
    "LB-BOOT-1",
    "LB-SIM-1",
    "LB-NEST-1",
)

SUITE_IDS = ("suite-repair", "suite-agent", "suite-knowledge", "suite-rigor")

SUITE_META: dict[str, dict[str, str]] = {
    "suite-repair": {"label": "Repair & Verify", "tagline": "Code, tool, reflexion, DSPy repair"},
    "suite-agent": {"label": "Multi-Agent", "tagline": "Crews, graphs, debate, ToT, voting"},
    "suite-knowledge": {"label": "Research & RAG", "tagline": "Synthesis, retrieval, bootstrap, autonomy"},
    "suite-rigor": {"label": "Composition & Safety", "tagline": "Compose, nest, sim, HITL, memory"},
}

TASK_META: dict[str, dict[str, str | int]] = {
    "LB-CR-1": {"name": "Code repair", "tagline": "Fix broken code under test-suite verify pressure.", "language": "SimEnv", "seeds": 5},
    "LB-RS-1": {"name": "Research synthesis", "tagline": "Structured briefs — quality vs cost.", "language": "SimEnv", "seeds": 5},
    "LB-MA-1": {"name": "Multi-agent debate", "tagline": "Autonomy and coordination under pressure.", "language": "SimEnv", "seeds": 5},
    "LB-COMP-1": {"name": "Composed swarm", "tagline": "Parallel branches + merge.", "language": "SimEnv", "seeds": 5},
    "LB-REACT-1": {"name": "ReAct tool loop", "tagline": "Reason-act-observe under repair SimEnv.", "language": "SimEnv", "seeds": 5},
    "LB-GRAPH-1": {"name": "State graph routing", "tagline": "LangGraph-style parallel routing.", "language": "SimEnv", "seeds": 5},
    "LB-CREW-1": {"name": "Sequential crew", "tagline": "CrewAI-style role pipeline.", "language": "SimEnv", "seeds": 5},
    "LB-REFLEX-1": {"name": "Reflexion memory", "tagline": "Verbal RL with episodic memory.", "language": "SimEnv", "seeds": 5},
    "LB-AUTO-1": {"name": "Long-horizon autonomy", "tagline": "Plan-execute under synthesis env.", "language": "SimEnv", "seeds": 5},
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


@dataclass
class GeneralistRow:
    submitter: str
    les_observed: float
    les_display: float
    spec_path: str
    repro_command: str
    harness: str
    submission_id: str
    is_external: bool
    primary_suite: str | None
    suite_scores: dict[str, dict[str, Any]]


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
    suite = entry.get("primary_suite")
    if suite:
        return f"loopbench run --suite {suite} --spec {spec} --seeds 0,1,2,3,4 -o results.json"
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


def flatten_generalist(board: dict[str, Any]) -> list[GeneralistRow]:
    rows: list[GeneralistRow] = []
    for entry in board.get("entries") or []:
        submitter = str(entry.get("submitter", "?"))
        spec_path = str(entry.get("spec_path") or entry.get("spec_uri") or "")
        harness = str(entry.get("harness") or "native")
        submission_id = str(entry.get("submission_id") or "")
        external = not is_internal_submitter(submitter)
        suite_scores = dict(entry.get("suite_scores") or {})

        gc = entry.get("grand_composite") or entry.get("composite") or {}
        les_obs = float(gc.get("les_observed") or gc.get("rank_score") or 0.0)
        les_display = float(gc.get("les_display") or les_obs * 100)

        if not les_obs and suite_scores:
            vals = [float(s.get("les_observed", 0)) for s in suite_scores.values()]
            les_obs = sum(vals) / len(vals) if vals else 0.0
            les_display = les_obs * 100

        if les_obs <= 0 and not suite_scores:
            continue
        if entry.get("partial"):
            continue
        if suite_scores and len(suite_scores) < 4:
            continue

        rows.append(
            GeneralistRow(
                submitter=submitter,
                les_observed=les_obs,
                les_display=les_display,
                spec_path=spec_path,
                repro_command=str(
                    entry.get("repro_command")
                    or _repro_command(entry, "", spec_path)
                ),
                harness=harness,
                submission_id=submission_id,
                is_external=external,
                primary_suite=entry.get("primary_suite"),
                suite_scores=suite_scores,
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


def rank_generalist(rows: list[GeneralistRow], top_n: int = 10, external_only: bool = False) -> list[GeneralistRow]:
    filtered = [r for r in rows if not external_only or r.is_external]
    filtered.sort(key=lambda r: r.les_observed, reverse=True)
    return filtered[:top_n]


def rank_by_suite(rows: list[GeneralistRow], top_n: int = 10, external_only: bool = False) -> dict[str, list[tuple[GeneralistRow, float, float]]]:
    ranked: dict[str, list[tuple[GeneralistRow, float, float]]] = {s: [] for s in SUITE_IDS}
    for row in rows:
        if external_only and not row.is_external:
            continue
        for suite_id in SUITE_IDS:
            score = row.suite_scores.get(suite_id) or {}
            les = float(score.get("les_observed") or score.get("rank_score") or 0.0)
            if les <= 0:
                continue
            disp = float(score.get("les_display") or les * 100)
            ranked[suite_id].append((row, les, disp))
    for suite_id in SUITE_IDS:
        ranked[suite_id].sort(key=lambda t: t[1], reverse=True)
        ranked[suite_id] = ranked[suite_id][:top_n]
    return ranked


def render_generalist_table(rows: list[GeneralistRow]) -> list[str]:
    lines = ["## Generalist (grand composite)", ""]
    if not rows:
        lines.append("_No suite-scored entries yet._")
        lines.append("")
        return lines
    lines.extend(["| Rank | Submitter | LES | Primary suite | Spec |", "|------|-----------|-----|---------------|------|"])
    for i, row in enumerate(rows, 1):
        spec_link = row.spec_path if row.spec_path.startswith("http") else f"`{row.spec_path}`"
        ps = row.primary_suite or "—"
        tag = " *" if row.is_external else ""
        lines.append(f"| {i} | {row.submitter}{tag} | {row.les_display:.1f} | {ps} | {spec_link} |")
    lines.append("")
    return lines


def render_suite_table(suite_id: str, rows: list[tuple[GeneralistRow, float, float]]) -> list[str]:
    meta = SUITE_META.get(suite_id, {})
    lines = [f"## {meta.get('label', suite_id)} (`{suite_id}`)", ""]
    if not rows:
        lines.append("_No entries yet._")
        lines.append("")
        return lines
    lines.extend(["| Rank | Submitter | LES | Spec |", "|------|-----------|-----|------|"])
    for i, (row, _, disp) in enumerate(rows, 1):
        spec_link = row.spec_path if row.spec_path.startswith("http") else f"`{row.spec_path}`"
        tag = " *" if row.is_external else ""
        lines.append(f"| {i} | {row.submitter}{tag} | {disp:.1f} | {spec_link} |")
    lines.append("")
    return lines


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
    task_rows = flatten_entries(board)
    generalist_rows = flatten_generalist(board)
    ranked_tasks = rank_by_task(task_rows, top_n=top_n, external_only=external_only)
    ranked_gen = rank_generalist(generalist_rows, top_n=top_n, external_only=external_only)
    ranked_suites = rank_by_suite(generalist_rows, top_n=top_n, external_only=external_only)
    updated = board.get("updated", "unknown")

    lines = [
        "# LoopBench — live leaderboard",
        "",
        f"_Updated: {updated}_",
        "",
        generated_note,
        "",
        "Primary rank: **generalist** (mean of suite scores). Filter by suite tab below.",
        "",
    ]
    lines.extend(render_generalist_table(ranked_gen))
    for suite_id in SUITE_IDS:
        lines.extend(render_suite_table(suite_id, ranked_suites.get(suite_id, [])))

    lines.append("---")
    lines.append("")
    lines.append("## Micro-task detail (legacy columns)")
    lines.append("")
    for task_id in ("LB-CR-1", "LB-RS-1", "LB-MA-1", "LB-COMP-1"):
        lines.extend(render_task_table(task_id, ranked_tasks.get(task_id, [])))
    return "\n".join(lines) + "\n"


def render_readme_block(board: dict[str, Any], *, top_n: int = 5) -> str:
    generalist_rows = flatten_generalist(board)
    ranked_gen = rank_generalist(generalist_rows, top_n=top_n, external_only=False)
    updated = board.get("updated", "unknown")

    lines = [
        f"**Live board** (updated {updated}) — [full rankings](leaderboard/LIVE.md)",
        "",
        "**Generalist:**",
    ]
    if not ranked_gen:
        lines.append("- _no suite-scored entries_")
    else:
        for row in ranked_gen[:3]:
            ext = " (external)" if row.is_external else ""
            lines.append(f"- {row.submitter}{ext} — LES **{row.les_display:.1f}**")
    lines.append("")
    lines.append("[Submit your loop →](https://github.com/KanakMalpani/Loop-Engineering/blob/main/contributions/LOOP_PLAYGROUND.md)")
    return "\n".join(lines) + "\n"


def _loop_name_from_entry(row: TaskRow) -> str:
    return _loop_name_from_spec(row.spec_path)


def export_site_json(board: dict[str, Any], *, top_n: int = 20) -> dict[str, Any]:
    task_rows = flatten_entries(board)
    generalist_rows = flatten_generalist(board)
    ranked_tasks = rank_by_task(task_rows, top_n=top_n, external_only=False)
    ranked_gen = rank_generalist(generalist_rows, top_n=top_n, external_only=False)
    ranked_suites = rank_by_suite(generalist_rows, top_n=top_n, external_only=False)

    tasks_out: dict[str, Any] = {}
    for task_id in KNOWN_TASKS[:9]:
        meta = TASK_META.get(task_id, {})
        entries = []
        for rank, row in enumerate(ranked_tasks.get(task_id, []), 1):
            entries.append(
                {
                    "rank": rank,
                    "submitter": row.submitter,
                    "loop_name": _loop_name_from_entry(row),
                    "les_observed": round(row.les_observed, 4),
                    "les_display": round(row.les_display, 1),
                    "success_at_k": round(row.success_at_k, 3),
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

    suites_out: dict[str, Any] = {}
    for suite_id in SUITE_IDS:
        meta = SUITE_META.get(suite_id, {})
        entries = []
        for rank, (row, les, disp) in enumerate(ranked_suites.get(suite_id, []), 1):
            entries.append(
                {
                    "rank": rank,
                    "submitter": row.submitter,
                    "les_observed": round(les, 4),
                    "les_display": round(disp, 1),
                    "spec_path": row.spec_path,
                    "harness": row.harness,
                    "is_external": row.is_external,
                }
            )
        suites_out[suite_id] = {"id": suite_id, "label": meta.get("label", suite_id), "entries": entries}

    generalist_out = []
    for rank, row in enumerate(ranked_gen, 1):
        generalist_out.append(
            {
                "rank": rank,
                "submitter": row.submitter,
                "les_observed": round(row.les_observed, 4),
                "les_display": round(row.les_display, 1),
                "primary_suite": row.primary_suite,
                "spec_path": row.spec_path,
                "is_external": row.is_external,
            }
        )

    return {
        "version": board.get("version", "0.2.0"),
        "updated": board.get("updated", "unknown"),
        "entry_count": len(board.get("entries") or []),
        "generalist": generalist_out,
        "suites": suites_out,
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
