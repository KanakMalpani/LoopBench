"""Validate LoopBench submission JSON against schema and conformance rules."""

from __future__ import annotations

import json
import re
from pathlib import Path

import jsonschema

REPO_ROOT = Path(__file__).resolve().parents[1]
_SCHEMA_PACKAGED = Path(__file__).resolve().parent / "submit_schema.json"
SCHEMA_PATH = _SCHEMA_PACKAGED if _SCHEMA_PACKAGED.is_file() else REPO_ROOT / "submit" / "schema.json"

_PLACEHOLDER_HASH = re.compile(r"^sha256:0+$")


def load_schema() -> dict:
    with SCHEMA_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


def validate_submission(data: dict, schema: dict | None = None) -> list[str]:
    schema = schema or load_schema()
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))
    messages = [f"{'.'.join(str(p) for p in e.absolute_path) or '(root)'}: {e.message}" for e in errors]

    spec_path = data.get("spec_path")
    spec_hash = data.get("spec_hash")
    if spec_path and spec_hash:
        if _PLACEHOLDER_HASH.match(str(spec_hash)):
            messages.append("spec_hash: placeholder hash not allowed")
        path = Path(spec_path)
        if not path.is_absolute():
            path = REPO_ROOT / path
        if path.exists():
            import hashlib

            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            expected = f"sha256:{digest}"
            if spec_hash != expected:
                messages.append(f"spec_hash: mismatch (expected {expected})")

    for task_result in data.get("results", []):
        agg = task_result.get("aggregate", {})
        les_obs = agg.get("les_observed")
        les_disp = agg.get("les_display")
        if les_obs is not None and les_disp is not None:
            expected_disp = round(float(les_obs) * 100, 1)
            if abs(float(les_disp) - expected_disp) > 0.05:
                messages.append(
                    f"results.{task_result.get('task_id')}.aggregate: "
                    f"les_display {les_disp} != round(les_observed*100,1)={expected_disp}"
                )
        runs = task_result.get("runs") or []
        if not runs:
            messages.append(f"results.{task_result.get('task_id')}.runs: empty runs not allowed")

    return messages


def validate_leaderboard_entry(entry: dict, index: int = 0) -> list[str]:
    """Lightweight checks for leaderboard/entries.json rows."""
    prefix = f"entries[{index}]"
    messages: list[str] = []
    for key in ("submitter", "spec_path", "spec_hash"):
        if not entry.get(key):
            messages.append(f"{prefix}: missing {key}")
    spec_hash = str(entry.get("spec_hash") or "")
    if _PLACEHOLDER_HASH.match(spec_hash):
        messages.append(f"{prefix}.spec_hash: placeholder hash not allowed")
    results = entry.get("results") or []
    suite_scores = entry.get("suite_scores") or {}
    if not results and not suite_scores:
        messages.append(f"{prefix}: need results or suite_scores")
    for tr in results:
        tid = tr.get("task_id")
        runs = tr.get("runs") or []
        if not runs:
            messages.append(f"{prefix}.results.{tid}.runs: empty runs not allowed")
        agg = tr.get("aggregate") or {}
        cats = agg.get("categories") or {}
        if runs and not cats:
            messages.append(f"{prefix}.results.{tid}.aggregate.categories: required when runs present")
    gc = entry.get("grand_composite")
    if gc and suite_scores and len(suite_scores) < 4 and not entry.get("partial"):
        messages.append(f"{prefix}: grand_composite requires all 4 suite_scores or partial=true")
    return messages


def validate_leaderboard(data: dict) -> list[str]:
    messages: list[str] = []
    if not isinstance(data, dict):
        return ["(root): expected object"]
    for key in ("version", "updated", "entries"):
        if key not in data:
            messages.append(f"(root): missing required property '{key}'")
    entries = data.get("entries")
    if not isinstance(entries, list):
        messages.append("entries: expected array")
        return messages
    for i, entry in enumerate(entries):
        messages.extend(validate_leaderboard_entry(entry, i))
    return messages


def validate_file(path: Path) -> tuple[bool, list[str]]:
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if isinstance(data, dict) and "entries" in data:
        errors = validate_leaderboard(data)
    else:
        errors = validate_submission(data)
    return len(errors) == 0, errors
