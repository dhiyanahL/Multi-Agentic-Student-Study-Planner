# 📘 Work Breakdown Structure (WBS)

## Schedule Generation Agent (Member 3)

---

## 🧩 1. Component Overview

The **Schedule Generation Agent** is responsible for creating a **feasible and structured study timetable** based on:

* prioritized academic tasks
* available study hours per day
* task deadlines
* task difficulty and workload

This agent transforms abstract task priorities into a **concrete day-by-day execution plan**.

---

## ⚙️ 2. Inputs and Outputs

### Inputs (from shared state)

```python
prioritized_tasks: list[dict]
available_hours_per_day: float
```

Each task contains:

```python
{
  "subject": str,
  "task_name": str,
  "priority_score": float,
  "deadline_days": int,
  "difficulty": str,
  "estimated_hours": float
}
```

---

### Output

```python
schedule: dict
```

Example:

```python
{
  "Day 1": [
    {"task": "DBMS assignment", "hours": 2.5},
    {"task": "OOP quiz", "hours": 1.5}
  ],
  "Day 2": [
    {"task": "DBMS assignment", "hours": 3}
  ]
}
```

---

## 🛠️ 3. Tool Specification

### Function

```python
def generate_study_schedule(
    tasks: list[dict],
    hours_per_day: float
) -> dict:
```

---

### Responsibilities of the Tool

* Sort tasks based on priority and urgency
* Allocate study hours across multiple days
* Ensure daily time constraints are respected
* Distribute workload according to deadlines
* Handle incomplete or invalid task data
* Return a structured schedule dictionary

---

## 🔧 4. Detailed Work Breakdown

---

### 🔹 4.1 Input Handling

* Validate `hours_per_day > 0`
* Validate task list is not empty
* Handle missing fields (e.g., default estimated hours)
* Normalize difficulty values (`easy`, `medium`, `hard`)

---

### 🔹 4.2 Task Ordering

* Sort tasks using:

  * priority score (descending)
  * deadline urgency (ascending)

Goal:

* urgent and high-priority tasks are scheduled first

---

### 🔹 4.3 Time Allocation Logic

* Initialize `remaining_hours` for each task
* Iterate day-by-day
* Allocate hours per task until:

  * daily limit is reached
  * or task is completed

---

### 🔹 4.4 Constraint Handling

#### Daily Constraint

* Total allocated hours per day must not exceed `hours_per_day`

#### Deadline Constraint

* Tasks should be completed within `deadline_days`

#### Workload Distribution

* Larger tasks should be spread across multiple days
* Hard tasks may receive slightly higher time allocation

---

### 🔹 4.5 Overload Detection

* Calculate:

  * total required hours
  * total available hours

* If required > available:

  * flag overload condition
  * allow schedule generation but mark as constrained

---

### 🔹 4.6 Output Formatting

* Group allocations by day

* Maintain consistent structure:

  * `"Day N"` keys
  * list of `{task, hours}` objects

* Round hours to 1–2 decimal places

---

### 🔹 4.7 Edge Case Handling

* Zero or negative study hours
* Tasks with identical priorities
* Missing estimated hours
* Very tight deadlines
* Excessive workload scenarios

---

### 🔹 4.8 Logging (Observability)

Log the following:

* input tasks
* sorted task list
* per-day allocation decisions
* final schedule output

Example:

```json
{
  "agent": "ScheduleAgent",
  "input_tasks": [...],
  "hours_per_day": 4,
  "output_schedule": {...}
}
```

---

## 🤖 5. Agent Responsibilities

The agent acts as a wrapper around the tool.

### Tasks

* Retrieve:

  * `prioritized_tasks`
  * `available_hours_per_day`

* Call:

  * `generate_study_schedule()`

* Update state:

```python
state["schedule"] = schedule
```

* Log execution details

---

## 🧪 6. Testing & Evaluation

The Schedule Generation Agent must be validated using automated tests.

---

### ✔ Test Cases

#### 1. Daily Limit Validation

* Ensure total hours per day ≤ available hours

#### 2. Task Coverage

* Ensure all tasks appear in the schedule

#### 3. Priority Ordering

* High-priority / urgent tasks appear earlier

#### 4. Overload Scenario

* Detect when workload exceeds available capacity

#### 5. Edge Cases

* Invalid inputs
* Missing data
* Zero available hours

---

## 🎯 7. Design Goals

* Generate realistic and balanced schedules
* Avoid overloading daily plans
* Respect task urgency and difficulty
* Ensure all tasks are accounted for
* Maintain clear and structured outputs

---

## 📌 8. Implementation Notes (for Code Generation)

* Core logic must be inside the tool, not the agent
* Use clean Python with type hints and docstrings
* Avoid hardcoded values
* Ensure deterministic output for testing
* Keep scheduling logic modular and readable

---

