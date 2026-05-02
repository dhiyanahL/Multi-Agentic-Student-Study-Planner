"""Minimal LangGraph orchestration skeleton for the study planner MAS."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from pprint import pprint

from langgraph.graph import END, START, StateGraph

from agents.input_agent import run_input_agent
from agents.review_agent import run_review_feedback_agent
from agents.schedule_agent import run_schedule_generation_agent
from agents.task_prioritization_agent import run_task_prioritization_agent
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
    event = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "agent": agent,
        "action": action,
        "input": input_data or {},
        "tool_called": tool_called or "",
        "output": output_data or {},
        "details": details or {},
    }

    # ✅ store in state
    state.setdefault("logs", []).append(event)

    # ✅ print to terminal
    #print(json.dumps(event, indent=2))


def _persist_logs(state: PlannerState) -> None:
    """Persist execution logs as JSON lines for assignment observability."""
    logs_dir = Path(__file__).resolve().parent / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / "execution.log"
    with log_file.open("w", encoding="utf-8") as handle:
        for event in state.get("logs", []):
            handle.write(json.dumps(event, ensure_ascii=True) + "\n")


def input_understanding_node(state: PlannerState) -> PlannerState:
    """Agent 1 node: parse raw student input into tasks and profile."""
    updates = run_input_agent(state)
    state.update(updates)
    return state


def task_prioritization_node(state: PlannerState) -> PlannerState:
    """Agent 2 node: ranks tasks using the prioritization agent toolchain."""
    return run_task_prioritization_agent(state)


def schedule_generation_node(state: PlannerState) -> PlannerState:
    """Agent 3 node: uses the implemented schedule generation tool."""
    return run_schedule_generation_agent(state)


def review_feedback_node(state: PlannerState) -> PlannerState:
    """Agent 4 node: Member 4 review agent (tool-backed)."""
    return run_review_feedback_agent(state)


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


def run_demo(raw_input: str = "") -> PlannerState:
    """Run a sample end-to-end flow using one shared global state."""
    initial_state = create_initial_state(raw_input=raw_input)
    if not raw_input:
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
    print("\n🎓 Welcome to the AI Study Planner!")
    print("\nPlease include your subjects, deadlines, and how many hours you can study daily.")
    print("\n(Defaults: 7 days for missing deadlines, 3 hours/day for missing study time)")
    user_input = input("\nEnter your request (or press Enter for mock data): ")
    final_state = run_demo(raw_input=user_input)
    # keep file logging
    _persist_logs(final_state)
    pprint(final_state["tasks"])

    # 🔥 PRINT ALL AGENT LOGS (this is what you need)
    print("\n========== AGENT EXECUTION LOGS ==========")
    for event in final_state.get("logs", []):
        print(json.dumps(event, indent=2))

    print("\n========== FINAL SCHEDULE ==========")
    pprint(final_state["schedule"])

    print("\n========== SCHEDULE META ==========")
    pprint(final_state["schedule_meta"])

    print("\n========== FEEDBACK ==========")
    pprint(final_state["feedback"])