"""Tests for LoopBench suite scoring."""

from __future__ import annotations

from loopbench.runner import _suite_scores_from_results, build_submission
from loopbench.suites import list_suites, load_suite, suite_task_ids


def _task_result(task_id: str, les: float) -> dict:
    return {
        "task_id": task_id,
        "env_id": "loopbench/code-repair-v1",
        "runs": [{"task_instance_id": "x", "seed": 0, "success": True, "g_final": 0.9, "g_target": 0.8, "iterations": 1, "cost_usd": 0.1, "elapsed_s": 0.01, "termination_reason": "goal_met"}],
        "aggregate": {
            "success_at_k": 1.0,
            "les_observed": les,
            "les_display": les * 100,
            "categories": {
                "effectiveness": les,
                "speed": les,
                "cost": les,
                "robustness": les,
                "scalability": les,
                "safety": les,
                "adaptability": les,
                "autonomy": les,
            },
            "cost_usd_mean": 0.1,
            "robustness_seeds": 1,
        },
    }


def test_list_suites_has_four():
    suites = list_suites()
    assert len(suites) == 4
    assert "suite-repair" in suites


def test_suite_task_ids_repair():
    ids = suite_task_ids("suite-repair")
    assert "LB-CR-1" in ids
    assert len(ids) == 5


def test_suite_scores_from_results():
    repair_tasks = suite_task_ids("suite-repair")
    results = [_task_result(tid, 0.8 + i * 0.01) for i, tid in enumerate(repair_tasks)]
    scores = _suite_scores_from_results(results)
    assert "suite-repair" in scores
    assert scores["suite-repair"]["les_observed"] > 0


def test_build_submission_grand_composite(tmp_path):
    spec = tmp_path / "spec.yaml"
    spec.write_text("loop_name: test\nversion: 1.0.0\nobjective: test\n", encoding="utf-8")
    all_tasks = []
    for sid in list_suites():
        for tid in suite_task_ids(sid):
            all_tasks.append(_task_result(tid, 0.75))
    sub = build_submission("tester", spec, all_tasks, primary_suite="suite-repair")
    assert "suite_scores" in sub
    assert "grand_composite" in sub
    assert sub["composite"]["rank_score"] == sub["grand_composite"]["rank_score"]
