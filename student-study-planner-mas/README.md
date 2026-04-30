# Multi-Agent Student Study Planner (MAS)

Locally hosted multi-agent system that helps students convert raw study needs into a realistic schedule with feasibility feedback.

## Project Goal

This project demonstrates a full **Agentic AI pipeline** for academic planning using:

- 4 specialized agents
- Custom Python tools
- Shared global state between agents
- End-to-end observability logs
- Local execution (no paid API requirement)

## System Architecture

The application follows a sequential 4-agent workflow orchestrated in `app.py` with LangGraph.

1. **Input Understanding Agent**
   - Reads `state["raw_input"]`
   - Produces normalized `state["tasks"]` and `state["student_profile"]`

2. **Task Prioritization Agent**
   - Reads `state["tasks"]`
   - Produces ranked `state["prioritized_tasks"]`

3. **Schedule Generation Agent**
   - Reads `state["prioritized_tasks"]` and `state["student_profile"]`
   - Produces `state["schedule"]` and `state["schedule_meta"]`

4. **Review/Feedback Agent**
   - Reads schedule and context fields
   - Produces `state["feedback"]`

All agents append structured events to `state["logs"]`, and logs are persisted to `logs/execution.log`.

## Global State Management

Global state is defined in `state/state_schema.py` as `PlannerState`.  
This ensures every member uses the same handoff contract.

Core shared keys:

- `raw_input`
- `student_profile`
- `tasks`
- `prioritized_tasks`
- `schedule`
- `schedule_meta`
- `feedback`
- `logs`

## File and Folder Roles

- `app.py`  
  LangGraph orchestrator (agent routing, execution order, flow run, log persistence).

- `agents/`  
  Agent wrappers that read from state, call tools, and write back to state.

- `tools/`  
  Core business logic functions used by agents.

- `state/state_schema.py`  
  Shared type-safe state schema and initial state builder.

- `logs/execution.log`  
  Persistent JSONL observability trace of agent execution.

- `tests/`  
  Agent/tool validation and unified test harness.


## How to Run Tests

Component test:

```bash
python -m pytest tests/test_schedule_agent.py
```

Unified harness:

```bash
python tests/run_all_tests.py
```

## Observability Format

Each log event is structured with fields like:

- `timestamp`
- `agent`
- `action`
- `input`
- `tool_called`
- `output`
- `details`

Logs are available both in-memory (`state["logs"]`) and on disk (`logs/execution.log`).

## Team Integration Checklist

Each teammate should:

1. Implement one agent in `agents/`
2. Implement one tool in `tools/`
3. Update the relevant node logic in `app.py`
4. Read/write only agreed `PlannerState` keys
5. Add structured logs on every run
6. Add tests for their own component in `tests/`

## Demo Strategy (No Frontend Required)

A terminal demo is sufficient:

1. Run `python app.py`
2. Show state handoff through the 4-agent flow
3. Show final schedule + feedback
4. Open `logs/execution.log` to prove observability
5. Run tests to prove reliability

Optional: Streamlit UI can be added later as a presentation layer, while keeping `app.py` as the backend orchestration flow.

