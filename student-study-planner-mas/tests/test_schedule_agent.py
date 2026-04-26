"""Tests for schedule generation tool and agent."""

from __future__ import annotations

from agents.schedule_agent import run_schedule_generation_agent
from tools.scheduler_tool import generate_study_schedule


def _total_daily_hours(entries: list[dict]) -> float:
    return round(sum(float(item["hours"]) for item in entries), 2)


def test_daily_limit_is_respected() -> None:
    tasks = [
        {
            "subject": "DBMS",
            "task_name": "Assignment",
            "priority_score": 9.5,
            "deadline_days": 3,
            "difficulty": "hard",
            "estimated_hours": 6.0,
        },
        {
            "subject": "OOP",
            "task_name": "Quiz",
            "priority_score": 6.0,
            "deadline_days": 5,
            "difficulty": "medium",
            "estimated_hours": 3.0,
        },
    ]
    output = generate_study_schedule(tasks, hours_per_day=4)
    schedule = {k: v for k, v in output.items() if k.startswith("Day ")}

    for day_entries in schedule.values():
        assert _total_daily_hours(day_entries) <= 4.0


def test_all_tasks_appear_in_schedule() -> None:
    tasks = [
        {"subject": "SE", "task_name": "Lab", "priority_score": 8, "deadline_days": 2, "difficulty": "hard"},
        {"subject": "ML", "task_name": "Revision", "priority_score": 5, "deadline_days": 4, "difficulty": "easy"},
    ]
    output = generate_study_schedule(tasks, hours_per_day=3)
    task_labels = {
        entry["task"]
        for day, entries in output.items()
        if day.startswith("Day ")
        for entry in entries
    }
    assert "SE Lab" in task_labels
    assert "ML Revision" in task_labels


def test_urgent_high_priority_tasks_scheduled_earlier() -> None:
    tasks = [
        {
            "subject": "Urgent",
            "task_name": "Project",
            "priority_score": 10,
            "deadline_days": 1,
            "difficulty": "hard",
            "estimated_hours": 2.5,
        },
        {
            "subject": "Later",
            "task_name": "Reading",
            "priority_score": 3,
            "deadline_days": 5,
            "difficulty": "easy",
            "estimated_hours": 2.5,
        },
    ]
    output = generate_study_schedule(tasks, hours_per_day=3)
    day_1_tasks = [entry["task"] for entry in output.get("Day 1", [])]
    assert "Urgent Project" in day_1_tasks


def test_overload_is_reported_with_unmet_hours() -> None:
    tasks = [
        {"subject": "A", "task_name": "Task", "priority_score": 9, "deadline_days": 1, "difficulty": "hard", "estimated_hours": 4},
        {"subject": "B", "task_name": "Task", "priority_score": 8, "deadline_days": 1, "difficulty": "hard", "estimated_hours": 4},
    ]
    output = generate_study_schedule(tasks, hours_per_day=3)
    assert output["_meta"]["overload"] is True
    assert output["_meta"]["unmet_hours_by_task"]


def test_schedule_agent_updates_state() -> None:
    state = {
        "prioritized_tasks": [
            {"subject": "DBMS", "task_name": "Assignment", "priority_score": 9, "deadline_days": 2, "difficulty": "hard"}
        ],
        "student_profile": {"available_hours_per_day": 2},
    }
    updated = run_schedule_generation_agent(state)
    assert "schedule" in updated
    assert "schedule_meta" in updated


def test_invalid_hours_raise_error() -> None:
    tasks = [{"subject": "DBMS", "task_name": "Assignment", "deadline_days": 2}]
    try:
        generate_study_schedule(tasks, hours_per_day=0)
    except ValueError as exc:
        assert "greater than zero" in str(exc)
    else:
        assert False, "Expected ValueError for invalid hours_per_day"
