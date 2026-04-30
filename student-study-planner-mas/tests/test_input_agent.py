"""Tests for Input Understanding Agent behavior."""

from __future__ import annotations

from typing import Any

from agents.input_agent import run_input_agent


def test_run_input_agent_extracts_tasks_list(monkeypatch: Any) -> None:
    state = {"raw_input": "I have math and os tasks", "logs": []}

    def _mock_parser(user_text: str) -> dict[str, object]:
        assert isinstance(user_text, str)
        return {
            "available_hours_per_day": 5,
            "tasks": [
                {
                    "subject": "Math",
                    "task_name": "Assignment 1",
                    "deadline_days": 2,
                    "difficulty": "medium",
                }
            ],
        }

    monkeypatch.setattr("agents.input_agent.parse_student_input", _mock_parser)

    updated = run_input_agent(state)
    assert updated["tasks"] == state["tasks"]
    assert isinstance(updated["tasks"], list)
    assert len(updated["tasks"]) == 1
    assert updated["tasks"][0]["subject"] == "Math"


def test_run_input_agent_extracts_available_hours_per_day(monkeypatch: Any) -> None:
    state = {"raw_input": "I can study 4 hours daily", "logs": []}

    def _mock_parser(user_text: str) -> dict[str, object]:
        assert "4 hours" in user_text
        return {"available_hours_per_day": 4, "tasks": []}

    monkeypatch.setattr("agents.input_agent.parse_student_input", _mock_parser)

    updated = run_input_agent(state)
    assert updated["student_profile"]["available_hours_per_day"] == 4
    assert state["student_profile"]["available_hours_per_day"] == 4


def test_run_input_agent_handles_irrelevant_text_safely(monkeypatch: Any) -> None:
    state = {"raw_input": "blue sky random words 12345", "logs": []}

    def _mock_parser(user_text: str) -> dict[str, object]:
        assert isinstance(user_text, str)
        return {"available_hours_per_day": 0, "tasks": []}

    monkeypatch.setattr("agents.input_agent.parse_student_input", _mock_parser)

    updated = run_input_agent(state)
    assert isinstance(updated["tasks"], list)
    assert updated["tasks"] == []
    assert "student_profile" in updated
    assert updated["student_profile"]["available_hours_per_day"] == 0
