"""Tests for Member 4 review agent wiring."""

from __future__ import annotations

from agents.review_agent import REVIEW_AGENT_SYSTEM_PROMPT, run_review_feedback_agent
from state.state_schema import create_initial_state


def test_system_prompt_exists() -> None:
    assert "Review" in REVIEW_AGENT_SYSTEM_PROMPT
    assert "review_schedule_feasibility" in REVIEW_AGENT_SYSTEM_PROMPT.lower()


def test_review_agent_writes_report_and_logs() -> None:
    state = create_initial_state()
    state["student_profile"]["available_hours_per_day"] = 4
    state["prioritized_tasks"] = [
        {"subject": "DBMS", "task_name": "assignment", "deadline_days": 3, "estimated_hours": 6.0}
    ]
    state["schedule"] = {"Day 1": [{"task": "DBMS assignment", "hours": 2.0}]}

    out = run_review_feedback_agent(state)
    assert out["feedback"]
    assert "review_report" in out
    assert isinstance(out["review_report"].get("status"), str)
    assert out["logs"][-1]["tool_called"] == "review_schedule_feasibility"


def test_schedule_meta_overload_note_prepended_when_flagged() -> None:
    state = create_initial_state()
    state["student_profile"]["available_hours_per_day"] = 4
    state["prioritized_tasks"] = [
        {"subject": "DBMS", "task_name": "assignment", "deadline_days": 3, "estimated_hours": 6.0}
    ]
    state["schedule"] = {"Day 1": [{"task": "DBMS assignment", "hours": 2.0}]}
    state["schedule_meta"] = {"overload": True}

    out = run_review_feedback_agent(state)
    assert "Scheduler reported workload overload" in out["feedback"][0]
