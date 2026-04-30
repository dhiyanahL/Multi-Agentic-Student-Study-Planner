"""Parser tool for the Input Understanding Agent."""

from __future__ import annotations


def parse_student_input(available_hours_per_day: int, tasks: list[dict]) -> dict[str, object]:
    """
    Extracts available study hours and a list of academic tasks from student input.
    The tasks list must contain dictionaries with the keys: subject, task_name, deadline_days, and difficulty.

    Args:
        available_hours_per_day: The number of hours the student can study per day.
        tasks: A list of task dictionaries extracted from the user input.
    """
    return {
        "available_hours_per_day": available_hours_per_day,
        "tasks": tasks
    }
