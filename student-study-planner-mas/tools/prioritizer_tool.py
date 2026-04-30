"""Task prioritization tool for the study planner system."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


_DIFFICULTY_WEIGHT = {"easy": 1.0, "medium": 1.15, "hard": 1.3}


@dataclass(frozen=True)
class _Task:
    """Internal normalized task used for ranking."""

    source: dict[str, Any]
    deadline_days: int
    difficulty: str
    estimated_hours: float
    base_priority: float
    ranking_score: float


def _normalize_difficulty(value: Any) -> str:
    text = str(value or "medium").strip().lower()
    if text not in _DIFFICULTY_WEIGHT:
        return "medium"
    return text


def _to_positive_float(value: Any, default: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    if number <= 0:
        return default
    return number


def _to_positive_int(value: Any, default: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    if number <= 0:
        return default
    return number


def prioritize_tasks(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Rank tasks from highest to lowest urgency/importance.

    Score heuristic (higher is more urgent):
    - higher explicit `priority_score`
    - nearer deadline (`1 / deadline_days`)
    - harder difficulty
    - larger estimated workload
    """
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("tasks must be a non-empty list.")

    normalized: list[_Task] = []
    for task in tasks:
        if not isinstance(task, dict):
            raise ValueError("Each task must be a dictionary.")

        deadline_days = _to_positive_int(task.get("deadline_days"), 7)
        difficulty = _normalize_difficulty(task.get("difficulty"))
        estimated_hours = _to_positive_float(task.get("estimated_hours"), 2.0)
        base_priority = _to_positive_float(task.get("priority_score"), 0.0)

        urgency_component = 10.0 / deadline_days
        difficulty_component = 2.0 * _DIFFICULTY_WEIGHT[difficulty]
        workload_component = min(estimated_hours, 8.0) * 0.5
        ranking_score = round(
            base_priority + urgency_component + difficulty_component + workload_component,
            3,
        )

        normalized.append(
            _Task(
                source=task,
                deadline_days=deadline_days,
                difficulty=difficulty,
                estimated_hours=estimated_hours,
                base_priority=base_priority,
                ranking_score=ranking_score,
            )
        )

    ranked = sorted(
        normalized,
        key=lambda item: (
            -item.ranking_score,
            item.deadline_days,
            -item.base_priority,
        ),
    )

    prioritized_tasks: list[dict[str, Any]] = []
    for index, task in enumerate(ranked, start=1):
        task_copy = dict(task.source)
        task_copy["priority_score"] = task.ranking_score
        task_copy["reason"] = (
            f"Rank {index}: deadline={task.deadline_days}d, "
            f"difficulty={task.difficulty}, "
            f"estimated_hours={task.estimated_hours:g}"
        )
        prioritized_tasks.append(task_copy)

    return prioritized_tasks
