"""Tests for Member 4 review_schedule_feasibility tool."""

from __future__ import annotations

import pytest

from tools.review_tool import review_schedule_feasibility


def test_daily_over_limit_is_critical() -> None:
    schedule = {
        "Day 1": [
            {"task": "DBMS assignment", "hours": 3.0},
            {"task": "OOP quiz", "hours": 2.0},
        ]
    }
    tasks = [{"subject": "DBMS", "task_name": "assignment", "deadline_days": 2, "estimated_hours": 6.0}]
    out = review_schedule_feasibility(schedule, tasks, 4.0)
    assert out["status"] == "critical"
    assert out["metrics"]["daily_over_limit"]


def test_missing_task_coverage_warns() -> None:
    schedule = {"Day 1": [{"task": "DBMS assignment", "hours": 2.0}]}
    tasks = [
        {"subject": "DBMS", "task_name": "assignment", "deadline_days": 3},
        {"subject": "OOP", "task_name": "quiz", "deadline_days": 5},
    ]
    out = review_schedule_feasibility(schedule, tasks, 4.0)
    assert out["status"] == "warning"
    assert out["metrics"]["missing_task_hints"]


def test_hours_per_day_invalid_raises() -> None:
    with pytest.raises(ValueError):
        review_schedule_feasibility({}, [], 0)


def test_happy_path_with_scheduler_style_labels_ok() -> None:
    schedule = {
        "Day 1": [
            {"task": "SE Lab", "hours": 2.0},
            {"task": "ML Revision", "hours": 2.0},
        ]
    }
    tasks = [
        {"subject": "SE", "task_name": "Lab", "deadline_days": 4, "estimated_hours": 5.0},
        {"subject": "ML", "task_name": "Revision", "deadline_days": 5, "estimated_hours": 4.0},
    ]
    out = review_schedule_feasibility(schedule, tasks, 4.0)
    assert out["status"] == "ok"
