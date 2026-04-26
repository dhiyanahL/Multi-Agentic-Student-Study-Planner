"""Minimal LangGraph orchestration skeleton for the study planner MAS."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from pprint import pprint

from langgraph.graph import END, START, StateGraph

from agents.schedule_agent import run_schedule_generation_agent
from state.state_schema import PlannerState, create_initial_state


def _log_event(
    state: PlannerState,
    agent: str,
    action: str,
    *,
    input_data: dict | None = None,
    tool_called: str | None = None,
    output_data: dict | None = None,
    details: dict | None = None,
) -> None:
    """Append a structured observability event to shared state."""
    state.setdefault("logs", []).append(
        {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "agent": agent,
            "action": action,
            "input": input_data or {},
            "tool_called": tool_called or "",
            "output": output_data or {},
            "details": details or {},
        }
    )


def _persist_logs(state: PlannerState) -> None:
    """Persist execution logs as JSON lines for assignment observability."""
    logs_dir = Path(__file__).resolve().parent / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / "execution.log"
    with log_file.open("w", encoding="utf-8") as handle:
        for event in state.get("logs", []):
            handle.write(json.dumps(event, ensure_ascii=True) + "\n")


def input_understanding_node(state: PlannerState) -> PlannerState:
    """
    Placeholder for Agent 1.

    If tasks already exist in state (demo/testing), this node passes through.
    """
    _log_event(
        state,
        "InputUnderstandingAgent",
        "pass_through",
        input_data={"raw_input_present": bool(state.get("raw_input"))},
        tool_called="",
        output_data={"task_count": len(state.get("tasks", []))},
        details={"message": "Placeholder node. Integrate parser tool here."},
    )
    return state


def task_prioritization_node(state: PlannerState) -> PlannerState:
    """
    Placeholder for Agent 2.

    For now: if prioritized_tasks is empty but tasks exist, pass tasks through.
    """
    if not state.get("prioritized_tasks") and state.get("tasks"):
        state["prioritized_tasks"] = state["tasks"]

    _log_event(
        state,
        "TaskPrioritizationAgent",
        "pass_through",
        input_data={"task_count": len(state.get("tasks", []))},
        tool_called="",
        output_data={"prioritized_task_count": len(state.get("prioritized_tasks", []))},
        details={"message": "Placeholder node. Integrate priority tool here."},
    )
    return state


def schedule_generation_node(state: PlannerState) -> PlannerState:
    """Agent 3 node: uses the implemented schedule generation tool."""
    return run_schedule_generation_agent(state)


def review_feedback_node(state: PlannerState) -> PlannerState:
    """
    Placeholder for Agent 4.

    Adds basic feedback based on schedule meta as a minimal end-to-end flow.
    """
    overload = bool(state.get("schedule_meta", {}).get("overload"))
    if overload:
        state.setdefault("feedback", []).append(
            "Warning: workload exceeds available capacity before one or more deadlines."
        )
    else:
        state.setdefault("feedback", []).append("Schedule appears feasible with current constraints.")

    _log_event(
        state,
        "ReviewFeedbackAgent",
        "basic_review",
        input_data={"overload": overload},
        tool_called="",
        output_data={"feedback_count": len(state.get("feedback", []))},
        details={"overload": overload},
    )
    return state


def build_graph():
    """Construct minimal sequential 4-agent graph."""
    graph = StateGraph(PlannerState)
    graph.add_node("input_understanding", input_understanding_node)
    graph.add_node("task_prioritization", task_prioritization_node)
    graph.add_node("schedule_generation", schedule_generation_node)
    graph.add_node("review_feedback", review_feedback_node)

    graph.add_edge(START, "input_understanding")
    graph.add_edge("input_understanding", "task_prioritization")
    graph.add_edge("task_prioritization", "schedule_generation")
    graph.add_edge("schedule_generation", "review_feedback")
    graph.add_edge("review_feedback", END)
    return graph.compile()


def run_demo() -> PlannerState:
    """Run a sample end-to-end flow using one shared global state."""
    initial_state = create_initial_state()
    initial_state["student_profile"]["available_hours_per_day"] = 4
    initial_state["tasks"] = [
        {
            "subject": "DBMS",
            "task_name": "assignment",
            "priority_score": 9.5,
            "deadline_days": 2,
            "difficulty": "hard",
            "estimated_hours": 8.0,
        },
        {
            "subject": "OOP",
            "task_name": "quiz",
            "priority_score": 6.0,
            "deadline_days": 5,
            "difficulty": "medium",
            "estimated_hours": 3.0,
        },
    ]

    graph = build_graph()
    return graph.invoke(initial_state)


if __name__ == "__main__":
    final_state = run_demo()
    _persist_logs(final_state)
    pprint(final_state["schedule"])
    pprint(final_state["schedule_meta"])
    pprint(final_state["feedback"])

