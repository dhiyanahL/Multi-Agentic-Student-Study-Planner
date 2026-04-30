"""Schedule Generation Agent wrapper."""

from __future__ import annotations

from typing import Any
from pathlib import Path
from datetime import datetime
import sys

try:
    from tools.scheduler_tool import generate_study_schedule
except ModuleNotFoundError:
    # Allow direct script execution from the agents/ directory.
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from tools.scheduler_tool import generate_study_schedule


def run_schedule_generation_agent(state: dict[str, Any]) -> dict[str, Any]:
    """
    Build a study schedule from state and write results back into state.

    Expected state inputs:
    - state["prioritized_tasks"]: list[dict]
    - state["student_profile"]["available_hours_per_day"] or state["available_hours_per_day"]
    """
    if not isinstance(state, dict):
        raise ValueError("state must be a dictionary.")

    tasks = state.get("prioritized_tasks", [])
    student_profile = state.get("student_profile", {}) if isinstance(state.get("student_profile"), dict) else {}
    hours_per_day = student_profile.get("available_hours_per_day", state.get("available_hours_per_day"))

    schedule_output = generate_study_schedule(tasks=tasks, hours_per_day=hours_per_day)
    state["schedule"] = {k: v for k, v in schedule_output.items() if k != "_meta"}
    state["schedule_meta"] = schedule_output.get("_meta", {})
    state.setdefault("logs", []).append(
        {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "agent": "ScheduleGenerationAgent",
            "action": "generate_study_schedule",
            "input": {"task_count": len(tasks), "hours_per_day": hours_per_day},
            "tool_called": "generate_study_schedule",
            "output": {
                "scheduled_days": len(state["schedule"]),
                "unmet_task_count": len(state["schedule_meta"].get("unmet_hours_by_task", {})),
                "overload": state["schedule_meta"].get("overload", False),
            },
            "details": {
                "task_count": len(tasks),
                "hours_per_day": hours_per_day,
                "overload": state["schedule_meta"].get("overload", False),
            },
        }
    )
    return state
