Project Title
Multi-Agent Student Assignment and Study Planner
1. Problem Domain

University students often struggle to manage:

multiple assignments
different deadlines
overlapping study tasks
limited daily study time
uneven subject difficulty

Many students know what they need to do, but they do not know:

what to start first
how to divide time properly
how to balance urgent work and important work
how to adjust plans when something changes

So this system will act as a local multi-agent academic planning assistant that takes assignment and study inputs from a student and produces a personalized study plan.

2. Core Idea of the System

The user enters information such as:

subject names
assignment titles
deadlines
estimated difficulty
estimated workload
available study hours per day

The system then uses multiple agents to:

understand and structure the input
prioritize tasks
generate a realistic study schedule
review the plan and suggest adjustments

The final output can be:

a prioritized task list
a daily study timetable
warnings for overload
recommended adjustments
3. Why This Topic Is Good for the Assignment

This topic is good because it directly supports the required MAS components:

Multi-agent orchestration

The work can be clearly divided among 4 agents.

Tool usage

Each agent can use a Python tool such as parsing, scoring, scheduling, or saving data.

State management

All extracted student information, task priorities, and schedules can be stored in a shared state dictionary and passed between agents.

Observability

You can log:

user input
each agent’s output
tool calls
final schedule generation steps
Easy local execution

You can run everything locally with:

Ollama
CrewAI or LangGraph
Python
local JSON/CSV/text files
4. Proposed 4-Agent Architecture
Agent 1: Input Understanding Agent
Main responsibility

Read the student’s raw request and convert it into structured data.

Example input

“I have a DBMS assignment due in 3 days, an OOP quiz in 5 days, and I can study 4 hours daily. DBMS is hard, OOP is medium.”

Example output
{
  "tasks": [
    {
      "subject": "DBMS",
      "task_name": "assignment",
      "deadline_days": 3,
      "difficulty": "hard"
    },
    {
      "subject": "OOP",
      "task_name": "quiz",
      "deadline_days": 5,
      "difficulty": "medium"
    }
  ],
  "available_hours_per_day": 4
}
Tool for Member 1

parse_student_input()

Main challenge

Natural language can be messy. The tool and prompt must extract data consistently.

Testing focus
Can it detect deadlines correctly?
Can it detect subjects and task names?
Can it detect available study hours?
Does it reject incomplete or invalid input safely?
Agent 2: Task Prioritization Agent
Main responsibility

Take the structured tasks and calculate which tasks are most urgent and important.

Inputs received from state
tasks
deadlines
difficulty levels
workload estimates if available
Outputs
ranked task list
priority score for each task
explanation for priority
Example output
[
  {
    "subject": "DBMS",
    "task_name": "assignment",
    "priority_score": 9.5,
    "reason": "Short deadline and high difficulty"
  },
  {
    "subject": "OOP",
    "task_name": "quiz",
    "priority_score": 6.0,
    "reason": "Moderate deadline and medium difficulty"
  }
]
Tool for Member 2

calculate_priority_score()

Suggested priority logic

You can use a simple weighted formula like:

deadline urgency = high if close
difficulty weight = high for hard tasks
workload weight = high for long tasks

Example:

priority_score =
(urgency_weight × deadline_factor) +
(difficulty_weight × difficulty_factor) +
(workload_weight × workload_factor)
Testing focus
Shorter deadlines should rank higher
Harder tasks should rank higher
Equal tasks should be handled consistently
No negative or invalid scores
Agent 3: Schedule Generation Agent
Main responsibility

Generate a realistic daily or weekly study timetable from the prioritized tasks.

Inputs received from state
prioritized tasks
available hours per day
number of days remaining
Outputs
a daily study plan
time allocation per task
warning if workload exceeds available time
Example output
{
  "Day 1": [
    {"task": "DBMS assignment", "hours": 2.5},
    {"task": "OOP quiz revision", "hours": 1.5}
  ],
  "Day 2": [
    {"task": "DBMS assignment", "hours": 3},
    {"task": "OOP quiz revision", "hours": 1}
  ]
}
Tool for Member 3

generate_study_schedule()

Scheduling rules
urgent tasks get more time early
daily hours must not exceed available hours
hard tasks should get more study time
the plan should avoid unrealistic overload
Testing focus
Total allocated hours per day should not exceed the limit
All tasks should appear in the schedule
Urgent tasks should be scheduled earlier
The plan should handle overloaded situations properly
Agent 4: Review and Feedback Agent
Main responsibility

Review the generated schedule, identify risks, and give practical advice.

Inputs received from state
structured tasks
priority results
schedule
Outputs
final refined plan
warnings
study advice
overload suggestions
Example output
{
  "status": "warning",
  "feedback": [
    "DBMS assignment requires more time than available before the deadline.",
    "Consider increasing study time by 1 hour for the next 2 days.",
    "Start OOP revision after completing 70% of DBMS work."
  ]
}
Tool for Member 4

review_schedule_feasibility() or generate_feedback_report()

Testing focus
Can it detect overload?
Can it detect unrealistic plans?
Does it produce meaningful recommendations?
Does it stay within its role instead of changing raw data incorrectly?
5. Team Member Allocation
Member 1
Agent: Input Understanding Agent
Tool: parse_student_input()
Evaluation: input parsing accuracy and validation cases
Member 2
Agent: Task Prioritization Agent
Tool: calculate_priority_score()
Evaluation: ranking correctness and scoring consistency
Member 3
Agent: Schedule Generation Agent
Tool: generate_study_schedule()
Evaluation: schedule correctness, time-limit checks, task coverage
Member 4
Agent: Review and Feedback Agent
Tool: review_schedule_feasibility()
Evaluation: overload detection, feedback quality, risk identification

This division fits the requirement that each student contributes one agent, one tool, and testing for their own component.

6. Suggested Workflow
End-to-end flow
User enters raw study request
Agent 1 extracts and structures the information
Agent 2 calculates priorities
Agent 3 creates the study schedule
Agent 4 reviews the plan and produces final advice
Final output is shown and optionally saved to a local file
7. Global State Design

The assignment specifically asks for state management between agents, so define one global shared state like this:

state = {
    "raw_input": "",
    "student_profile": {
        "available_hours_per_day": 0
    },
    "tasks": [],
    "prioritized_tasks": [],
    "schedule": {},
    "feedback": [],
    "logs": []
}
State fields
raw_input

Stores the original user request

student_profile

Stores overall study constraints like available hours

tasks

Structured task list from Agent 1

prioritized_tasks

Scored and ranked tasks from Agent 2

schedule

Daily or weekly schedule from Agent 3

feedback

Review comments and warnings from Agent 4

logs

Agent traces and tool call outputs

8. Tools You Can Build

These should be proper Python functions with:

type hints
docstrings
error handling

because the rubric values tool quality highly.

Tool 1
def parse_student_input(user_text: str) -> dict:
    """Extract tasks, deadlines, difficulty levels, and available study hours from raw student input."""
Tool 2
def calculate_priority_score(task: dict) -> float:
    """Calculate a priority score based on deadline urgency, task difficulty, and workload."""
Tool 3
def generate_study_schedule(tasks: list[dict], hours_per_day: float) -> dict:
    """Create a feasible study schedule using prioritized tasks and time constraints."""
Tool 4
def review_schedule_feasibility(schedule: dict, tasks: list[dict], hours_per_day: float) -> dict:
    """Analyze the generated schedule and return warnings, risks, and improvement suggestions."""
9. Suggested Technology Stack
LLM
Ollama
model: llama3:8b or phi3
Agent framework
CrewAI if you want easier role-based setup
LangGraph if you want better state-based flow

For your assignment, LangGraph may look stronger because the rubric emphasizes orchestration and state passing. But CrewAI is easier for fast development.

Other tools
Python
JSON or CSV for saving schedules
logging module for traces
pytest for evaluation
10. Suggested Local Folder Structure
student-study-planner-mas/
│
├── app.py
├── requirements.txt
├── README.md
│
├── agents/
│   ├── input_agent.py
│   ├── priority_agent.py
│   ├── schedule_agent.py
│   └── review_agent.py
│
├── tools/
│   ├── parser_tool.py
│   ├── priority_tool.py
│   ├── scheduler_tool.py
│   └── review_tool.py
│
├── tests/
│   ├── test_input_agent.py
│   ├── test_priority_agent.py
│   ├── test_schedule_agent.py
│   └── test_review_agent.py
│
├── state/
│   └── state_schema.py
│
├── logs/
│   └── execution.log
│
└── data/
    └── sample_inputs.json
11. Observability / Logging Plan

The brief explicitly requires logging or tracing.

You should log:

timestamp
agent name
input received
tool called
tool output
next state update
Example log entry
{
  "timestamp": "2026-04-18 10:00:00",
  "agent": "PriorityAgent",
  "input": {
    "subject": "DBMS",
    "deadline_days": 3,
    "difficulty": "hard"
  },
  "tool_called": "calculate_priority_score",
  "output": {
    "priority_score": 9.5
  }
}

This will help a lot in the demo and report.

12. Evaluation Strategy

The brief says each student must implement automated testing or evaluation for their own agent.

Member 1 evaluation

Test whether the parser extracts:

correct number of tasks
correct subject names
correct hours per day
proper handling of invalid text
Member 2 evaluation

Test whether:

closer deadlines increase priority
harder tasks increase priority
ranking is stable and logical
Member 3 evaluation

Test whether:

daily hours limit is respected
tasks are allocated across available days
urgent tasks are scheduled earlier
Member 4 evaluation

Test whether:

overload situations are flagged
missing schedule items are detected
advice is generated clearly
Group testing harness

Create one main script:

run_all_tests.py

This runs all member-specific test files together.

That fits the assignment note that there should be a unified testing harness, while each student contributes their own agent validations.

13. Example User Scenarios
Scenario 1

“I have an SE assignment due in 2 days, an ML lab due in 5 days, and an OOP presentation due in 4 days. I can study 5 hours per day.”

Expected:

tasks extracted
SE assignment ranked highest
balanced 5-hour schedule created
warnings if workload is too high
Scenario 2

“I have 4 subjects to revise for exams, but only 2 hours a day this week.”

Expected:

prioritization by urgency/difficulty
shorter but structured schedule
overload warning
Scenario 3

“I forgot to mention one deadline.”

Expected:

parser or review agent flags incomplete information
14. Suggested Input Format for MVP

For the first version, do not start with free-flow complex natural language only. Support both:

Option A: Natural language

Good for demo

Option B: Structured JSON/text form

Good for testing and reliable system behavior

Example JSON:

{
  "available_hours_per_day": 4,
  "tasks": [
    {"subject": "DBMS", "task_name": "Assignment", "deadline_days": 3, "difficulty": "hard", "estimated_hours": 6},
    {"subject": "OOP", "task_name": "Quiz", "deadline_days": 5, "difficulty": "medium", "estimated_hours": 3}
  ]
}

This will make your development much easier.

15. MVP Scope

To avoid making it too big, your first working version should do only this:

Phase 1
read input
extract tasks
prioritize tasks
generate schedule
review schedule
log outputs
Phase 2
save plan to file
allow editing a task
regenerate schedule
nicer terminal interface
Phase 3
optional GUI with Streamlit or simple frontend

For the assignment, even a terminal-based system is fine as long as the architecture is strong.

16. Report Writing Angles

Your report should explain:

why students need study planning support
why a multi-agent approach is better than one single agent
agent roles and responsibilities
tools built by each student
state design
logging design
testing methodology
contribution proof per student

These are directly aligned with the required report contents in the brief.

17. Why Multi-Agent Instead of Single Agent

This is important for your report and viva.

A single agent could try to do everything, but that would make:

task handling less modular
testing harder
reasoning less transparent
debugging more difficult

A multi-agent design is better because:

each agent has one focused role
each student can own one component clearly
tool responsibility is separated
outputs are easier to validate
orchestration and state passing are visible

This directly supports the architecture-focused grading criteria.

18. Best Framework Choice for You
Use LangGraph if:
you want strong state-flow diagrams
you want to show exact handoff logic
you want better rubric alignment for orchestration/state
Use CrewAI if:
you want to build quickly
you prefer clearer agent role definitions
your team is new to graph-based workflows
My recommendation

Use LangGraph for the backend flow, because this project is naturally a pipeline with shared state.

19. Immediate Team Starting Plan
Day 1

Finalize:

project name
agent responsibilities
state schema
tool signatures
Day 2

Each member builds:

their agent prompt
their tool
sample inputs and outputs
Day 3

Integrate agent flow

connect state passing
test orchestration
Day 4

Add:

logging
evaluation scripts
final polishing
20. Final Recommended Project Statement


Project Summary

The Multi-Agent Student Assignment and Study Planner is a locally hosted intelligent academic planning system that helps students organize study activities, prioritize tasks, and generate feasible schedules based on deadlines, difficulty, and available study time. The system uses four specialized agents working collaboratively to process student input, rank academic tasks, construct a realistic study plan, and review its feasibility. By combining local SLM reasoning, Python-based tools, shared state management, and agent-wise evaluation, the system demonstrates a practical implementation of agentic AI aligned with the assignment requirements.


