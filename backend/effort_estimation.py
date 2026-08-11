"""
effort_estimation.py — Step 6: Heuristic-based effort estimation for tasks

Uses keyword matching to classify task type and assign base hours,
with a small random variance for realism.

NOTE: In a production version, this would be replaced by a regression model
trained on real historical task data (e.g., Jira exports with actual vs estimated hours).
The heuristic here provides reasonable ballpark estimates for planning purposes.
"""
import random
import logging

logger = logging.getLogger(__name__)

# ────────────────────────────────────────────────────────────────────────────
#  Base hours per task type
# ────────────────────────────────────────────────────────────────────────────
BASE_HOURS = {
    "ui": 8,           # UI/frontend tasks
    "integration": 12, # Third-party API integration tasks
    "backend": 6,      # Backend logic implementation
    "setup": 4,        # Setup, configuration, scaffolding
    "testing": 6,      # Testing and QA tasks
}

# ────────────────────────────────────────────────────────────────────────────
#  Complexity multipliers based on keywords in task name
# ────────────────────────────────────────────────────────────────────────────
COMPLEXITY_KEYWORDS = {
    # High complexity (+50%)
    "high": [
        "real-time", "realtime", "machine learning", "ai", "algorithm",
        "encryption", "security", "oauth", "websocket", "streaming",
        "distributed", "scalable", "optimize", "performance", "migration",
    ],
    # Medium complexity (+25%)
    "medium": [
        "integrate", "api", "database", "schema", "search", "filter",
        "payment", "transaction", "validation", "authentication",
        "notification", "caching", "queue",
    ],
    # Low complexity (-20%)
    "low": [
        "configure", "setup", "install", "scaffold", "template",
        "readme", "documentation", "seed", "mock", "placeholder",
    ],
}

COMPLEXITY_MULTIPLIERS = {
    "high": 1.5,
    "medium": 1.25,
    "low": 0.8,
}

# Random variance range: ±20%
VARIANCE_MIN = 0.8
VARIANCE_MAX = 1.2


def estimate_effort(tasks: list[dict]) -> list[dict]:
    """
    Add estimated_hours to each task using heuristic-based estimation.

    Args:
        tasks: List of task dicts with "name", "component", "type" fields.

    Returns:
        Same list with "estimated_hours" added to each task (rounded to 1 decimal).
    """
    total_hours = 0

    for task in tasks:
        task_type = task.get("type", "backend")
        task_name = task.get("name", "")

        # Get base hours for this task type
        base = BASE_HOURS.get(task_type, 6)

        # Apply complexity multiplier
        multiplier = _get_complexity_multiplier(task_name)

        # Apply random variance for realism
        variance = random.uniform(VARIANCE_MIN, VARIANCE_MAX)

        # Calculate final estimate
        estimated = base * multiplier * variance
        estimated = round(estimated, 1)

        # Clamp to reasonable range (2h minimum, 24h maximum for a single task)
        estimated = max(2.0, min(24.0, estimated))

        task["estimated_hours"] = estimated
        total_hours += estimated

    logger.info(
        f"Effort estimation: {len(tasks)} tasks, "
        f"total={round(total_hours, 1)}h, "
        f"avg={round(total_hours / len(tasks), 1) if tasks else 0}h/task"
    )

    return tasks


def _get_complexity_multiplier(task_name: str) -> float:
    """Determine complexity multiplier based on keywords in task name."""
    name_lower = task_name.lower()

    for level in ["high", "medium", "low"]:
        keywords = COMPLEXITY_KEYWORDS[level]
        if any(kw in name_lower for kw in keywords):
            return COMPLEXITY_MULTIPLIERS[level]

    return 1.0  # Default: no multiplier
