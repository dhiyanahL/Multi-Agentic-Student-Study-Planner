"""Input Understanding Agent implementation."""

from __future__ import annotations

from datetime import datetime
import json
import logging
from pathlib import Path
import sys
from typing import Any

try:
    from tools.parser_tool import parse_student_input
except ModuleNotFoundError:
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from tools.parser_tool import parse_student_input


_SYSTEM_PROMPT = """
You are the Input Understanding Agent for a university study planning system.
Your only job is to extract explicit academic tasks and study-hour constraints from the student's raw text.

Rules:
1) Do not hallucinate or invent any information that is not stated by the student.
2) Always call the tool `parse_student_input` exactly once.
3) Pass arguments in this exact shape:
   - available_hours_per_day: int
   - tasks: list of dicts, each with subject, task_name, deadline_days, difficulty
4) Extract only academic tasks and available daily study hours.
4) If a task difficulty is not specified, use "medium".
5) Keep extraction faithful and conservative.
6) If the user mentions a task but does not provide a deadline, default deadline_days to 7. If the user does not provide available study hours, default available_hours_per_day to 3.
""".strip()

_llm_with_tools: Any | None = None

_file_logger = logging.getLogger("input_agent_execution")
if not _file_logger.handlers:
    logs_path = Path(__file__).resolve().parents[1] / "logs" / "execution.log"
    logs_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(logs_path, mode="a", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(message)s"))
    _file_logger.addHandler(file_handler)
    _file_logger.setLevel(logging.INFO)
    _file_logger.propagate = False


def _extract_tool_args(tool_calls: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Extract tool-call args from the first parse_student_input tool call."""
    for call in tool_calls:
        if call.get("name") != "parse_student_input":
            continue
        args = call.get("args", {})
        if isinstance(args, dict):
            return args
    return None


def _get_llm_with_tools() -> Any:
    """Initialize and cache the tool-enabled llama3 model."""
    global _llm_with_tools
    if _llm_with_tools is None:
        from langchain_ollama import ChatOllama

        llm = ChatOllama(model="llama3.1", temperature=0)
        _llm_with_tools = llm.bind_tools([parse_student_input])
    return _llm_with_tools

def run_input_agent(state: dict[str, Any]) -> dict[str, Any]:
    """Run Agent 1 to parse raw input into tasks and student profile."""
    if not isinstance(state, dict):
        raise ValueError("state must be a dictionary.")
    if not state.get("raw_input", "").strip():
        return {}  # If input is empty, don't overwrite the teammate's mock data

    raw_input = state.get("raw_input", "")
    if not isinstance(raw_input, str):
        raise ValueError("state['raw_input'] must be a string.")

    # START THE LOOP
    while True:
        tool_args: dict[str, Any] | None = None
        try:
            from langchain_core.messages import HumanMessage, SystemMessage

            llm_with_tools = _get_llm_with_tools()
            response = llm_with_tools.invoke(
                [
                    SystemMessage(content=_SYSTEM_PROMPT),
                    HumanMessage(content=raw_input),
                ]
            )
            tool_calls = getattr(response, "tool_calls", []) or []
            tool_args = _extract_tool_args(tool_calls)
        except ModuleNotFoundError:
            tool_args = None

        safe_tool_args = tool_args if isinstance(tool_args, dict) else {}
        
        # --- 🛡️ PYTHON-SIDE SAFETY ENFORCEMENT 🛡️ ---
        # 1. Enforce default hours if missing, 0, or None
        safe_hours = safe_tool_args.get("available_hours_per_day")
        if safe_hours in (None, 0, ""):
            safe_hours = 3
            
        # 2. Enforce default task values if missing or None
        safe_tasks = safe_tool_args.get("tasks", [])
        if not isinstance(safe_tasks, list):
            safe_tasks = []
            
        for task in safe_tasks:
            if task.get("deadline_days") in (None, "", 0):
                task["deadline_days"] = 7
            if task.get("difficulty") in (None, ""):
                task["difficulty"] = "medium"
        # ---------------------------------------------

        parsed_output = parse_student_input(
            **{
                "available_hours_per_day": int(safe_hours),
                "tasks": safe_tasks,
            }
        )

        tasks = parsed_output.get("tasks", [])

        # Check if the AI successfully extracted tasks
        if tasks:
            break  # We found tasks! Break the loop and continue.

        # If we get here, no tasks were found. Prompt the user again!
        print("\n🤖 [Input Agent]: I couldn't find any academic tasks in your message.")
        print("Please explicitly mention a subject and an assignment or exam.")
        print("(Note: If you don't provide a deadline or study hours, I will default to 7 days and 3 hours/day).")
        raw_input = input("\nTry again (or press Enter to use mock data): ")

        if not raw_input.strip():
            # If the user gives up and just presses Enter, escape the loop and do nothing
            return {}

    # END THE LOOP 

    available_hours = parsed_output.get("available_hours_per_day", 3)

    updated_fields = {
        "tasks": tasks if isinstance(tasks, list) else [],
        "student_profile": {
            "available_hours_per_day": int(available_hours)
        },
    }

    state.update(updated_fields)

    event = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "agent": "InputAgent",
        "action": "parse_student_input",
        "input": {"raw_input": raw_input},
        "tool_called": "parse_student_input",
        "output": updated_fields,
        "details": {"tool_call_detected": bool(tool_args), "task_count": len(updated_fields["tasks"])},
    }
    state.setdefault("logs", []).append(event)
    _file_logger.info(json.dumps(event, ensure_ascii=True))

    return updated_fields
