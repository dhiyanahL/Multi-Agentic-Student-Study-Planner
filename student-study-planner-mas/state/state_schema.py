"""Shared global state schema for the multi-agent study planner."""

from __future__ import annotations

from typing import Any, TypedDict


class StudentProfile(TypedDict, total=False):
    """Student-level constraints used by all agents."""

    available_hours_per_day: float


class TaskItem(TypedDict, total=False):
    """Normalized academic task structure."""

    subject: str
    task_name: str
    deadline_days: int
    difficulty: str
    estimated_hours: float
    priority_score: float
    reason: str


class LogEvent(TypedDict, total=False):
    """Structured execution trace event for observability."""

    timestamp: str
    agent: str
    action: str
    input: dict[str, Any]
    tool_called: str
    output: dict[str, Any]
    details: dict[str, Any]


class PlannerState(TypedDict, total=False):
    """
    Global state passed between all 4 agents.

    This aligns with the assignment requirement for shared state handoff.
    """

    raw_input: str
    student_profile: StudentProfile
    tasks: list[TaskItem]
    prioritized_tasks: list[TaskItem]
    schedule: dict[str, Any]
    schedule_meta: dict[str, Any]
    feedback: list[str]
    logs: list[LogEvent]


def create_initial_state(raw_input: str = "") -> PlannerState:
    """Create a safe initial global state object for graph execution."""
    return {
        "raw_input": raw_input,
        "student_profile": {"available_hours_per_day": 0},
        "tasks": [],
        "prioritized_tasks": [],
        "schedule": {},
        "schedule_meta": {},
        "feedback": [],
        "logs": [],
    }
