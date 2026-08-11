"""
milestone_scheduler.py — Step 7: Group tasks into phased milestones
4 fixed phases: Setup → Core Development → Testing → Deployment
Assigns tasks to phases based on type/keywords, sums hours, converts to calendar days.
"""
import logging

logger = logging.getLogger(__name__)

# Working hours per day
HOURS_PER_DAY = 6

# Phase definitions with their task assignment rules
PHASES = [
    {
        "name": "Setup",
        "description": "Project scaffolding, environment setup, and infrastructure",
        "task_types": ["setup"],
        "keywords": ["set up", "setup", "configure", "install", "scaffold", "init", "schema", "migration", "design", "project structure"],
    },
    {
        "name": "Core Development",
        "description": "Main feature implementation and service development",
        "task_types": ["backend", "ui", "integration"],
        "keywords": ["implement", "build", "create", "develop", "integrate", "add", "design"],
    },
    {
        "name": "Testing",
        "description": "Testing, QA, optimization, and bug fixes",
        "task_types": ["testing"],
        "keywords": ["test", "qa", "quality", "verify", "optimize", "performance", "debug", "fix", "monitor"],
    },
    {
        "name": "Deployment",
        "description": "Deployment, documentation, and launch preparation",
        "task_types": [],
        "keywords": ["deploy", "release", "launch", "document", "readme", "ci/cd", "docker", "production", "backup"],
    },
]


def schedule_milestones(tasks: list[dict]) -> list[dict]:
    """
    Group tasks into phased milestones with start/end day calculations.

    Args:
        tasks: List of task dicts with "name", "component", "type", "estimated_hours".

    Returns:
        List of milestone dicts:
        [
            {
                "phase_name": str,
                "description": str,
                "tasks": [task_dict, ...],
                "start_day": int,
                "end_day": int,
                "total_hours": float,
                "total_days": int
            }
        ]
    """
    # Assign each task to a phase
    phase_tasks = {phase["name"]: [] for phase in PHASES}

    for task in tasks:
        phase_name = _assign_to_phase(task)
        phase_tasks[phase_name].append(task)

    # If Core Development is empty but other phases have tasks,
    # move unassigned tasks there (shouldn't happen, but safety check)
    if not phase_tasks["Core Development"]:
        for phase_name in ["Setup", "Testing", "Deployment"]:
            if len(phase_tasks[phase_name]) > len(tasks) // 2:
                # Move excess tasks to Core Development
                excess = phase_tasks[phase_name][3:]
                phase_tasks[phase_name] = phase_tasks[phase_name][:3]
                phase_tasks["Core Development"].extend(excess)

    # Build milestones with cumulative day tracking
    milestones = []
    current_day = 1

    for phase in PHASES:
        phase_name = phase["name"]
        tasks_in_phase = phase_tasks[phase_name]

        if not tasks_in_phase:
            # Add deployment phase with minimum tasks even if empty
            if phase_name == "Deployment":
                tasks_in_phase = [
                    {"name": "Prepare deployment configuration", "component": "Infrastructure", "type": "setup", "estimated_hours": 4.0},
                    {"name": "Write documentation and README", "component": "Documentation", "type": "setup", "estimated_hours": 3.0},
                    {"name": "Final deployment and smoke testing", "component": "Infrastructure", "type": "testing", "estimated_hours": 4.0},
                ]
            elif phase_name == "Testing":
                tasks_in_phase = [
                    {"name": "Integration testing", "component": "Testing", "type": "testing", "estimated_hours": 6.0},
                    {"name": "User acceptance testing", "component": "Testing", "type": "testing", "estimated_hours": 4.0},
                    {"name": "Performance optimization", "component": "Testing", "type": "testing", "estimated_hours": 5.0},
                ]

        total_hours = sum(t.get("estimated_hours", 4.0) for t in tasks_in_phase)
        total_days = max(1, round(total_hours / HOURS_PER_DAY))

        start_day = current_day
        end_day = current_day + total_days - 1

        milestones.append({
            "phase_name": phase_name,
            "description": phase["description"],
            "tasks": tasks_in_phase,
            "start_day": start_day,
            "end_day": end_day,
            "total_hours": round(total_hours, 1),
            "total_days": total_days,
        })

        current_day = end_day + 1

    logger.info(
        f"Milestone scheduling: {len(tasks)} tasks across {len(milestones)} phases, "
        f"total timeline: {milestones[-1]['end_day']} days"
    )

    return milestones


def _assign_to_phase(task: dict) -> str:
    """Assign a task to one of the 4 phases based on type and keywords."""
    task_type = task.get("type", "backend")
    task_name = task.get("name", "").lower()

    # --- Phase 1: Setup ---
    if task_type == "setup":
        return "Setup"
    if any(kw in task_name for kw in PHASES[0]["keywords"]):
        return "Setup"

    # --- Phase 3: Testing ---
    if task_type == "testing":
        return "Testing"
    if any(kw in task_name for kw in PHASES[2]["keywords"]):
        return "Testing"

    # --- Phase 4: Deployment ---
    if any(kw in task_name for kw in PHASES[3]["keywords"]):
        return "Deployment"

    # --- Phase 2: Core Development (default) ---
    return "Core Development"
