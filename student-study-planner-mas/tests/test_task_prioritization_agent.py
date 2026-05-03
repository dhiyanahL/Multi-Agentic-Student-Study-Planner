"""Tests for task prioritization tool and agent."""

from __future__ import annotations

from agents.task_prioritization_agent import run_task_prioritization_agent
from tools.prioritizer_tool import prioritize_tasks


def test_prioritize_tasks_sorts_by_urgency_and_weight() -> None:
    tasks = [
        {
            "subject": "Maths",
            "task_name": "Revision",
            "priority_score": 6,
            "deadline_days": 5,
            "difficulty": "easy",
            "estimated_hours": 2,
        },
        {
            "subject": "DBMS",
            "task_name": "Assignment",
            "priority_score": 8,
            "deadline_days": 2,
            "difficulty": "hard",
            "estimated_hours": 6,
        },
        {
            "subject": "SE",
            "task_name": "Lab",
            "priority_score": 9,
            "deadline_days": 4,
            "difficulty": "medium",
            "estimated_hours": 3,
        },
    ]

    ranked = prioritize_tasks(tasks)

    assert len(ranked) == 3
    assert ranked[0]["subject"] == "DBMS"
    assert ranked[0]["task_name"] == "Assignment"
    assert "reason" in ranked[0]
    assert "Rank 1" in ranked[0]["reason"]


def test_prioritize_tasks_applies_safe_defaults() -> None:
    tasks = [{"subject": "AI", "task_name": "Reading", "deadline_days": "bad"}]
    ranked = prioritize_tasks(tasks)

    assert len(ranked) == 1
    assert ranked[0]["subject"] == "AI"
    assert isinstance(ranked[0]["priority_score"], float)
    assert ranked[0]["reason"]


def test_task_prioritization_agent_updates_state_and_logs() -> None:
    state = {
        "tasks": [
            {
                "subject": "CN",
                "task_name": "Tutorial",
                "priority_score": 7,
                "deadline_days": 2,
                "difficulty": "medium",
                "estimated_hours": 3,
            }
        ]
    }

    updated = run_task_prioritization_agent(state)

    assert "prioritized_tasks" in updated
    assert len(updated["prioritized_tasks"]) == 1
    assert "logs" in updated
    assert updated["logs"][-1]["agent"] == "TaskPrioritizationAgent"
    assert updated["logs"][-1]["tool_called"] == "prioritize_tasks"


def test_prioritize_tasks_raises_for_invalid_input() -> None:
    try:
        prioritize_tasks([])
    except ValueError as exc:
        assert "non-empty list" in str(exc)
    else:
        assert False, "Expected ValueError for empty tasks list"
