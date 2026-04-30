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
2) Always call the tool `parse_student_input` exactly once with the full original student input as `user_text`.
3) Extract only academic tasks and available daily study hours.
4) If a task difficulty is not specified, use "medium".
5) Keep extraction faithful and conservative.
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


def _extract_user_text_from_tool_calls(tool_calls: list[dict[str, Any]]) -> str | None:
    """Extract user_text argument from the first parse_student_input tool call."""
    for call in tool_calls:
        if call.get("name") != "parse_student_input":
            continue
        args = call.get("args", {})
        if isinstance(args, dict):
            candidate = args.get("user_text")
            if isinstance(candidate, str):
                return candidate
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

    raw_input = state.get("raw_input", "")
    if not isinstance(raw_input, str):
        raise ValueError("state['raw_input'] must be a string.")

    parsed_user_text: str | None = None
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
        parsed_user_text = _extract_user_text_from_tool_calls(tool_calls)
    except ModuleNotFoundError:
        parsed_user_text = None

    normalized_input = parsed_user_text if parsed_user_text is not None else raw_input

    parsed_output = parse_student_input(user_text=normalized_input)
    tasks = parsed_output.get("tasks", [])
    available_hours = parsed_output.get("available_hours_per_day", 0)

    updated_fields = {
        "tasks": tasks if isinstance(tasks, list) else [],
        "student_profile": {
            "available_hours_per_day": int(available_hours) if available_hours is not None else 0
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
        "details": {"tool_call_detected": bool(parsed_user_text), "task_count": len(updated_fields["tasks"])},
    }
    state.setdefault("logs", []).append(event)
    _file_logger.info(json.dumps(event, ensure_ascii=True))

    return updated_fields
