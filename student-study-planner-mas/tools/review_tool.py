"""Member 4 review tool — structural feasibility checks on generated schedules."""

from __future__ import annotations

import math
import re
from typing import Any, Literal

StatusLevel = Literal["ok", "warning", "critical"]


def _normalize_label(subject: str, task_name: str) -> str:
    return f"{subject.strip()} {task_name.strip()}".lower()


def _schedule_task_labels(schedule: dict[str, Any]) -> set[str]:
    labels: set[str] = set()
    for blocks in schedule.values():
        if not isinstance(blocks, list):
            continue
        for block in blocks:
            if not isinstance(block, dict):
                continue
            t = block.get("task")
            if isinstance(t, str) and t.strip():
                labels.add(t.strip().lower())
    return labels


def _task_matches_schedule(subject: str, task_name: str, schedule_labels: set[str]) -> bool:
    needle = _normalize_label(subject, task_name)
    if needle in schedule_labels:
        return True
    sub_l = subject.strip().lower()
    name_l = task_name.strip().lower()
    for lab in schedule_labels:
        if sub_l in lab and name_l in lab:
            return True
        if needle.replace(" ", "") in lab.replace(" ", ""):
            return True
    return False


def _parse_day_index(day_key: str) -> int | None:
    m = re.search(r"(\d+)", str(day_key))
    return int(m.group(1)) if m else None


def _daily_hours_sum(day_blocks: Any) -> float:
    if not isinstance(day_blocks, list):
        return 0.0
    total = 0.0
    for block in day_blocks:
        if not isinstance(block, dict):
            continue
        h = block.get("hours")
        if h is None:
            continue
        try:
            total += float(h)
        except (TypeError, ValueError):
            continue
    return total


def review_schedule_feasibility(
    schedule: dict[str, Any],
    tasks: list[dict[str, Any]],
    hours_per_day: float,
) -> dict[str, Any]:
    """Analyze schedule vs constraints: daily caps, coverage, crude deadline capacity."""
    if not isinstance(schedule, dict):
        raise TypeError("schedule must be a dict mapping day keys to block lists")
    if not isinstance(tasks, list):
        raise TypeError("tasks must be a list of task dicts")
    if not isinstance(hours_per_day, (int, float)) or not math.isfinite(float(hours_per_day)):
        raise ValueError("hours_per_day must be a finite number")
    if float(hours_per_day) <= 0:
        raise ValueError("hours_per_day must be positive")

    limit = float(hours_per_day)
    eps = 1e-6
    feedback: list[str] = []
    violations: list[str] = []
    daily_totals: dict[str, float] = {}

    ordered_days = sorted(schedule.keys(), key=lambda k: (_parse_day_index(str(k)) or 999, str(k)))
    for day_key in ordered_days:
        s = _daily_hours_sum(schedule[day_key])
        daily_totals[str(day_key)] = s
        if s > limit + eps:
            violations.append(f"{day_key}: scheduled {s:.2f}h exceeds limit {limit:.2f}h")
            feedback.append(
                f"Daily overload on {day_key}: {s:.2f}h scheduled vs "
                f"{limit:.2f}h available — redistribute across days."
            )

    schedule_labels = _schedule_task_labels(schedule)
    missing: list[str] = []
    for task in tasks:
        if not isinstance(task, dict):
            continue
        sub = str(task.get("subject", "")).strip()
        name = str(task.get("task_name", "")).strip()
        if not sub and not name:
            continue
        if not _task_matches_schedule(sub or "task", name or "", schedule_labels):
            label = f"{sub} {name}".strip()
            missing.append(label)
            feedback.append(
                f"Schedule may not cover '{label}'. Confirm it appears in allocated blocks."
            )

    capacity_issues: list[str] = []
    for task in tasks:
        if not isinstance(task, dict):
            continue
        try:
            dl = float(task.get("deadline_days"))
        except (TypeError, ValueError):
            continue
        if dl <= 0 or not math.isfinite(dl):
            continue
        eh_raw = task.get("estimated_hours")
        if eh_raw is None:
            continue
        try:
            eh = float(eh_raw)
        except (TypeError, ValueError):
            continue
        if eh <= 0 or not math.isfinite(eh):
            continue
        cap = dl * limit
        sub = str(task.get("subject", "")).strip()
        name = str(task.get("task_name", "")).strip()
        tag = f"{sub} {name}".strip() or "task"
        if eh > cap + eps:
            capacity_issues.append(tag)
            feedback.append(
                f"'{tag}' needs ~{eh:.1f}h before deadline vs ~{cap:.1f}h available at "
                f"{limit:.1f}h/day — increase hours/day, extend deadline, or reduce scope."
            )

    if not schedule:
        feedback.append("Schedule is empty — no blocks generated.")
    if not tasks:
        feedback.append("No structured tasks to cross-check.")

    if not feedback and not violations and not missing and not capacity_issues:
        feedback.append("Schedule respects daily limits and coverage looks consistent.")

    status: StatusLevel = "ok"
    if violations or capacity_issues:
        status = "critical"
    elif missing or not schedule or not tasks:
        status = "warning"

    return {
        "status": status,
        "feedback": feedback,
        "metrics": {
            "hours_per_day_limit": limit,
            "daily_totals": daily_totals,
            "daily_over_limit": violations,
            "missing_task_hints": missing,
            "deadline_capacity_issues": capacity_issues,
        },
    }
