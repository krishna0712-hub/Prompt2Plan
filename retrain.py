"""
retrain.py — Retrain AI Effort Estimator with logged usage feedback

Appends logged real task completion hours (actual_hours from SQLite database)
to the historical dataset and retrains the GradientBoostingRegressor model.
"""

import sys
import os
import csv
import logging

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.database import SessionLocal, Task, init_db
from backend.ai_effort_estimator import initialize_estimator, get_model_metrics, DATASET_PATH

logging.basicConfig(level=logging.INFO, format="%(asctime)s │ %(levelname)-5s │ %(message)s")
logger = logging.getLogger("retrain")


def retrain_model():
    """Query logged task actual hours, append to dataset CSV, and retrain model."""
    logger.info("Checking SQLite database for user-logged actual task hours...")
    init_db()
    db = SessionLocal()

    logged_tasks = []
    try:
        tasks_with_actuals = db.query(Task).filter(Task.actual_hours.isnot(None)).all()
        logger.info(f"Found {len(tasks_with_actuals)} tasks with logged actual_hours.")

        for t in tasks_with_actuals:
            logged_tasks.append({
                "project_name": f"Project_{t.project_id}",
                "task_description": f"{t.name} in component {t.component or 'General'} ({t.phase})",
                "task_type": t.phase.lower() if t.phase else "backend",
                "component_category": t.component or "General",
                "loc_ksloc": round(t.actual_hours * 1.5, 1),
                "complexity": 1.1,
                "actual_hours": float(t.actual_hours),
            })
    finally:
        db.close()

    if logged_tasks:
        logger.info(f"Appending {len(logged_tasks)} user feedback records to {DATASET_PATH}...")
        
        # Read existing dataset to find max ID
        existing_ids = []
        if os.path.exists(DATASET_PATH):
            with open(DATASET_PATH, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                existing_ids = [int(row["id"]) for row in reader if row.get("id")]
        
        next_id = max(existing_ids) + 1 if existing_ids else 1

        with open(DATASET_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for item in logged_tasks:
                writer.writerow([
                    next_id,
                    item["project_name"],
                    item["task_description"],
                    item["task_type"],
                    item["component_category"],
                    item["loc_ksloc"],
                    item["complexity"],
                    item["actual_hours"],
                ])
                next_id += 1

    logger.info("Retraining AI effort estimation model on updated dataset...")
    initialize_estimator()

    metrics = get_model_metrics()
    logger.info(f"✅ Retraining complete! Updated Metrics -> MMRE: {metrics.get('mmre')}, PRED(25): {metrics.get('pred_25')}%")
    print(f"\n[OK] Model successfully retrained on {metrics.get('total_training_records')} total historical records.")
    print(f"     MMRE: {metrics.get('mmre')}")
    print(f"     PRED(25): {metrics.get('pred_25')}%\n")


if __name__ == "__main__":
    retrain_model()
