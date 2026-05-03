from schedule_agent import run_schedule_generation_agent

state = {
    "student_profile": {
        "available_hours_per_day": 4
    },
    "prioritized_tasks": [
        {
            "subject": "DBMS",
            "task_name": "assignment",
            "priority_score": 9.5,
            "deadline_days": 2,
            "difficulty": "hard",
            "estimated_hours": 8
        },
        {
            "subject": "OOP",
            "task_name": "quiz",
            "priority_score": 6.0,
            "deadline_days": 5,
            "difficulty": "medium",
            "estimated_hours": 3
        }
    ]
}

new_state = run_schedule_generation_agent(state)

print(new_state["schedule"])