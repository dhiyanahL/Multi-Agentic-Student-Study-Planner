"""Member 4 — Review & Feedback Agent (tool-backed feasibility checks)."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys
from typing import Any

try:
    from tools.review_tool import review_schedule_feasibility
except ModuleNotFoundError:
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from tools.review_tool import review_schedule_feasibility

REVIEW_AGENT_SYSTEM_PROMPT = """
You are the Review & Feedback Agent for the study planner.
Use the review_schedule_feasibility tool outputs only — do not invent tasks, deadlines, or hours.
Summarize overload, missing coverage, and deadline-capacity issues in short actionable bullets for a student.
""".strip()


def run_review_feedback_agent(state: dict[str, Any]) -> dict[str, Any]:
    """Run deterministic review on schedule + tasks; write feedback, review_report, and one log event."""
    if not isinstance(state, dict):
        raise ValueError("state must be a dictionary.")

    student_profile = state.get("student_profile", {})
    if not isinstance(student_profile, dict):
        student_profile = {}
    hours_raw = student_profile.get("available_hours_per_day", 0)
    try:
        hours_per_day = float(hours_raw)
    except (TypeError, ValueError):
        hours_per_day = 0.0
    if hours_per_day <= 0:
        hours_per_day = 4.0

    tasks = state.get("prioritized_tasks") or state.get("tasks") or []
    if not isinstance(tasks, list):
        tasks = []
    schedule = state.get("schedule", {})
    if not isinstance(schedule, dict):
        schedule = {}

    report = review_schedule_feasibility(
        schedule=schedule,
        tasks=tasks,
        hours_per_day=hours_per_day,
    )

    feedback = list(report.get("feedback", []))
    meta = state.get("schedule_meta", {})
    if isinstance(meta, dict) and meta.get("overload"):
        note = (
            "Scheduler reported workload overload before one or more deadlines "
            "(see schedule_meta)."
        )
        if note not in feedback:
            feedback.insert(0, note)

    state["feedback"] = feedback
    state["review_report"] = report

    state.setdefault("logs", []).append(
        {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "agent": "ReviewFeedbackAgent",
            "action": "review_schedule_feasibility",
            "input": {
                "task_count": len(tasks),
                "schedule_days": len(schedule),
                "hours_per_day": hours_per_day,
                "schedule_meta_overload": bool(isinstance(meta, dict) and meta.get("overload")),
            },
            "tool_called": "review_schedule_feasibility",
            "output": {
                "status": report.get("status"),
                "feedback_count": len(feedback),
            },
            "details": {"metrics_keys": list((report.get("metrics") or {}).keys())},
        }
    )
    return state
