"""Parser tool for the Input Understanding Agent."""

from __future__ import annotations


def parse_student_input(user_text: str) -> dict[str, object]:
    """Parse free-form student text into a normalized mock planning payload.

    Args:
        user_text: Raw natural-language input provided by the student.

    Returns:
        A mock dictionary containing:
        - available_hours_per_day: Estimated integer study hours per day.
        - tasks: A list of task dictionaries with `subject`, `task_name`,
          `deadline_days`, and `difficulty`.
    """
    _ = user_text  # Placeholder until real parsing logic is implemented.

    return {
        "available_hours_per_day": 3,
        "tasks": [
            {
                "subject": "Mathematics",
                "task_name": "Complete calculus assignment",
                "deadline_days": 2,
                "difficulty": "high",
            },
            {
                "subject": "Computer Science",
                "task_name": "Revise graph algorithms",
                "deadline_days": 4,
                "difficulty": "medium",
            },
        ],
    }
