"""Schedule generation tool for the study planner system."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any


logger = logging.getLogger(__name__)

_DIFFICULTY_DEFAULT_HOURS = {"easy": 2.0, "medium": 3.0, "hard": 4.0}
_DIFFICULTY_BONUS = {"easy": 0.9, "medium": 1.0, "hard": 1.15}
_DIFFICULTY_RANK = {"easy": 1, "medium": 2, "hard": 3}


@dataclass(frozen=True)
class _Task:
    """Internal normalized task representation."""

    task_id: str
    label: str
    priority_score: float
    deadline_days: int
    difficulty: str
    estimated_hours: float
    source: dict[str, Any]


def _normalize_difficulty(value: Any) -> str:
    text = str(value or "medium").strip().lower()
    if text not in _DIFFICULTY_DEFAULT_HOURS:
        return "medium"
    return text


def _normalize_tasks(tasks: list[dict[str, Any]]) -> list[_Task]:
    normalized: list[_Task] = []
    for idx, task in enumerate(tasks, start=1):
        if not isinstance(task, dict):
            raise ValueError("Each task must be a dictionary.")

        subject = str(task.get("subject") or "General").strip() or "General"
        task_name = str(task.get("task_name") or f"Task {idx}").strip() or f"Task {idx}"
        difficulty = _normalize_difficulty(task.get("difficulty"))

        raw_deadline = task.get("deadline_days", 1)
        try:
            deadline_days = max(1, int(raw_deadline))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid deadline_days for task '{subject} {task_name}'.") from exc

        raw_estimated_hours = task.get("estimated_hours", _DIFFICULTY_DEFAULT_HOURS[difficulty])
        try:
            estimated_hours = float(raw_estimated_hours)
        except (TypeError, ValueError):
            estimated_hours = _DIFFICULTY_DEFAULT_HOURS[difficulty]
        if estimated_hours <= 0:
            estimated_hours = _DIFFICULTY_DEFAULT_HOURS[difficulty]

        raw_priority = task.get("priority_score", 0.0)
        try:
            priority_score = float(raw_priority)
        except (TypeError, ValueError):
            priority_score = 0.0

        normalized.append(
            _Task(
                task_id=f"task_{idx}",
                label=f"{subject} {task_name}",
                priority_score=priority_score,
                deadline_days=deadline_days,
                difficulty=difficulty,
                estimated_hours=estimated_hours,
                source=task,
            )
        )
    return normalized


def generate_study_schedule(tasks: list[dict], hours_per_day: float) -> dict[str, Any]:
    """
    Create a feasible study schedule using prioritized tasks and time constraints.

    The function enforces daily limits, prioritizes urgent/high-priority tasks early,
    supports missing fields with safe defaults, and reports overload scenarios.
    """
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("tasks must be a non-empty list.")

    try:
        daily_hours = float(hours_per_day)
    except (TypeError, ValueError) as exc:
        raise ValueError("hours_per_day must be a valid number.") from exc
    if daily_hours <= 0:
        raise ValueError("hours_per_day must be greater than zero.")

    difficulty_weight = {"easy": 0.8, "medium": 1.0, "hard": 1.3}
    normalized_tasks = _normalize_tasks(tasks)
    ordered_tasks = sorted(
        normalized_tasks,
        key=lambda t: (t.deadline_days, -t.priority_score, -_DIFFICULTY_RANK[t.difficulty], t.task_id),
    )

    logger.info("Schedule generation started for %s tasks.", len(ordered_tasks))
    logger.debug("Ordered tasks: %s", [t.label for t in ordered_tasks])

    max_days = max(task.deadline_days for task in ordered_tasks)
    total_required_hours = round(sum(task.estimated_hours for task in ordered_tasks), 2)
    total_available_hours = round(max_days * daily_hours, 2)
    overload_precheck = total_required_hours > total_available_hours

    day_capacity = {day: daily_hours for day in range(1, max_days + 1)}
    schedule: dict[str, list[dict[str, float | str]]] = {f"Day {day}": [] for day in range(1, max_days + 1)}
    remaining_by_task = {task.task_id: task.estimated_hours for task in ordered_tasks}
    unmet_by_task: dict[str, float] = {}

    for task in ordered_tasks:
        remaining = remaining_by_task[task.task_id]
        for day in range(1, task.deadline_days + 1):
            if remaining <= 0:
                break
            capacity = day_capacity[day]
            if capacity <= 0:
                continue

            days_left = task.deadline_days - day + 1
            required_today = remaining / days_left
            target_today = required_today * difficulty_weight[task.difficulty]
            allocate = max(required_today, target_today)
            allocate = min(allocate, capacity, remaining)
            if required_today <= 3.0:
                allocate = min(allocate, 3.0)
            allocate = round(allocate, 2)
            if allocate <= 0:
                continue

            schedule[f"Day {day}"].append({"task": task.label, "hours": allocate})
            day_capacity[day] = round(capacity - allocate, 2)
            remaining = round(remaining - allocate, 2)
            logger.debug(
                "Allocated %.2fh to '%s' on Day %s (remaining %.2f).",
                allocate,
                task.label,
                day,
                remaining,
            )

        if remaining > 0:
            unmet_by_task[task.label] = round(remaining, 2)

    # Remove empty days for cleaner output while preserving ordering.
    schedule = {day: entries for day, entries in schedule.items() if entries}

    overload = bool(overload_precheck or unmet_by_task)
    warnings: list[str] = []
    if overload_precheck:
        warnings.append("Pre-check: total required hours exceed available hours before deadlines.")
    if overload:
        warnings.append("Workload exceeds available capacity before one or more deadlines.")

    result: dict[str, Any] = {
        **schedule,
        "_meta": {
            "overload": overload,
            "total_required_hours": total_required_hours,
            "total_available_hours": total_available_hours,
            "unmet_hours_by_task": unmet_by_task,
            "warnings": warnings,
        },
    }

    logger.info("Schedule generation completed. Overload=%s", overload)
    logger.debug("Final schedule output: %s", result)
    return result
