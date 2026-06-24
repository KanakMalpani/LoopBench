"""Validate LoopBench submission JSON against schema and conformance rules."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

REPO_ROOT = Path(__file__).resolve().parents[1]
_SCHEMA_PACKAGED = Path(__file__).resolve().parent / "submit_schema.json"
SCHEMA_PATH = _SCHEMA_PACKAGED if _SCHEMA_PACKAGED.is_file() else REPO_ROOT / "submit" / "schema.json"


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
        entry_errors = validate_submission(entry)
        for err in entry_errors:
            messages.append(f"entries[{i}].{err}")
    return messages


def validate_file(path: Path) -> tuple[bool, list[str]]:
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if isinstance(data, dict) and "entries" in data:
        errors = validate_leaderboard(data)
    else:
        errors = validate_submission(data)
    return len(errors) == 0, errors
