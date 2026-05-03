"""Parser tool for the Input Understanding Agent."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator

# Keep in sync with scheduler difficulty defaults when hours are not stated
_DIFFICULTY_DEFAULT_HOURS: dict[str, float] = {"easy": 2.0, "medium": 3.0, "hard": 4.0}


class StudentTaskInput(BaseModel):
    """One academic task extracted from the student's message."""

    subject: str = Field(description="Course or subject name, e.g. DBMS, OOP")
    task_name: str = Field(description="Task type, e.g. assignment, quiz, exam, lab")
    deadline_days: int = Field(ge=1, description="Whole days until the task is due")
    difficulty: str = Field(description='One of: "easy", "medium", "hard"')
    estimated_hours: float | None = Field(
        default=None,
        description=(
            "Estimated hours of work if the student stated a number "
            '(e.g. "6 hours", "about 5 hrs"). Use null if not mentioned.'
        ),
    )

    @field_validator("difficulty")
    @classmethod
    def difficulty_lower(cls, value: str) -> str:
        text = str(value or "medium").strip().lower()
        if text not in _DIFFICULTY_DEFAULT_HOURS:
            return "medium"
        return text


def _normalize_difficulty(value: Any) -> str:
    text = str(value or "medium").strip().lower()
    if text not in _DIFFICULTY_DEFAULT_HOURS:
        return "medium"
    return text


def _coerce_estimated_hours(raw: Any, difficulty: str) -> float:
    if raw is None or raw == "":
        return float(_DIFFICULTY_DEFAULT_HOURS[difficulty])
    try:
        hours = float(raw)
    except (TypeError, ValueError):
        return float(_DIFFICULTY_DEFAULT_HOURS[difficulty])
    if hours <= 0:
        return float(_DIFFICULTY_DEFAULT_HOURS[difficulty])
    return round(hours, 2)


def _task_dict_from_raw(item: Any) -> dict[str, Any] | None:
    """Build a normalized task dict from a StudentTaskInput, dict, or None."""
    if item is None:
        return None
    if isinstance(item, StudentTaskInput):
        diff = item.difficulty
        return {
            "subject": item.subject.strip() or "General",
            "task_name": item.task_name.strip() or "task",
            "deadline_days": max(1, int(item.deadline_days)),
            "difficulty": diff,
            "estimated_hours": _coerce_estimated_hours(item.estimated_hours, diff),
        }
    if isinstance(item, dict):
        try:
            model = StudentTaskInput.model_validate(item)
        except Exception:
            diff = _normalize_difficulty(item.get("difficulty"))
            try:
                dl = int(item.get("deadline_days") or 7)
            except (TypeError, ValueError):
                dl = 7
            return {
                "subject": str(item.get("subject") or "General").strip() or "General",
                "task_name": str(item.get("task_name") or "task").strip() or "task",
                "deadline_days": max(1, dl),
                "difficulty": diff,
                "estimated_hours": _coerce_estimated_hours(item.get("estimated_hours"), diff),
            }
        diff = model.difficulty
        return {
            "subject": model.subject.strip() or "General",
            "task_name": model.task_name.strip() or "task",
            "deadline_days": max(1, int(model.deadline_days)),
            "difficulty": diff,
            "estimated_hours": _coerce_estimated_hours(model.estimated_hours, diff),
        }
    return None


def parse_student_input(
    available_hours_per_day: int,
    tasks: list[StudentTaskInput],
) -> dict[str, object]:
    """
    Validates and returns available daily study hours plus normalized tasks.

    Each output task always includes ``estimated_hours`` (float): extracted from the user
    when stated, otherwise a difficulty-based default aligned with the scheduler.
    """
    hours_day = int(available_hours_per_day) if available_hours_per_day > 0 else 3

    normalized_tasks: list[dict[str, Any]] = []
    for item in tasks:
        # Runtime: LangChain may pass dicts from tool-call JSON; normalize either way
        row = _task_dict_from_raw(item)
        if row:
            normalized_tasks.append(row)

    return {
        "available_hours_per_day": hours_day,
        "tasks": normalized_tasks,
    }
