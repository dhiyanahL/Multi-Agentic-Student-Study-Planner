"""Tests for parse_student_input estimated_hours handling."""

from __future__ import annotations

from tools.parser_tool import parse_student_input


def test_parse_preserves_stated_estimated_hours() -> None:
    out = parse_student_input(
        5,
        [
            {
                "subject": "DBMS",
                "task_name": "assignment",
                "deadline_days": 2,
                "difficulty": "hard",
                "estimated_hours": 6.0,
            },
            {
                "subject": "OOP",
                "task_name": "quiz",
                "deadline_days": 5,
                "difficulty": "medium",
                "estimated_hours": 3.0,
            },
        ],
    )
    tasks = out["tasks"]
    assert tasks[0]["estimated_hours"] == 6.0
    assert tasks[1]["estimated_hours"] == 3.0


def test_parse_fills_default_hours_when_missing() -> None:
    out = parse_student_input(
        4,
        [
            {
                "subject": "SE",
                "task_name": "lab",
                "deadline_days": 3,
                "difficulty": "easy",
            },
        ],
    )
    assert out["tasks"][0]["estimated_hours"] == 2.0  # easy default


def test_total_required_matches_stated_hours_sum() -> None:
    """Regression: workload totals should follow parsed estimated_hours."""
    out = parse_student_input(
        5,
        [
            {"subject": "A", "task_name": "t", "deadline_days": 2, "difficulty": "hard", "estimated_hours": 6},
            {"subject": "B", "task_name": "t", "deadline_days": 5, "difficulty": "medium", "estimated_hours": 3},
            {"subject": "C", "task_name": "t", "deadline_days": 3, "difficulty": "hard", "estimated_hours": 5},
            {"subject": "D", "task_name": "t", "deadline_days": 7, "difficulty": "easy", "estimated_hours": 2},
            {"subject": "E", "task_name": "t", "deadline_days": 4, "difficulty": "medium", "estimated_hours": 4},
        ],
    )
    total = sum(t["estimated_hours"] for t in out["tasks"])
    assert total == 6 + 3 + 5 + 2 + 4
