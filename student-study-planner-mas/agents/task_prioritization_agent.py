"""Task Prioritization Agent wrapper."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any
import sys

try:
    from tools.prioritizer_tool import prioritize_tasks
except ModuleNotFoundError:
    # Allow direct script execution from the agents/ directory.
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from tools.prioritizer_tool import prioritize_tasks


def run_task_prioritization_agent(state: dict[str, Any]) -> dict[str, Any]:
    """Read raw tasks from state, rank them, and write to prioritized_tasks."""
    if not isinstance(state, dict):
        raise ValueError("state must be a dictionary.")

    tasks = state.get("tasks", [])
    prioritized = prioritize_tasks(tasks)
    state["prioritized_tasks"] = prioritized

    top_task = prioritized[0] if prioritized else {}
    top_label = " ".join(
        str(part).strip()
        for part in [top_task.get("subject", ""), top_task.get("task_name", "")]
        if str(part).strip()
    ).strip()

    state.setdefault("logs", []).append(
        {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "agent": "TaskPrioritizationAgent",
            "action": "prioritize_tasks",
            "input": {"task_count": len(tasks)},
            "tool_called": "prioritize_tasks",
            "output": {
                "prioritized_task_count": len(prioritized),
                "top_task": top_label,
            },
            "details": {
                "message": "Ranked tasks with urgency and difficulty-aware scoring."
            },
        }
    )
    return state
