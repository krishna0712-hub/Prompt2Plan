"""
main.py — FastAPI application for Prompt2Plan
Serves both the REST API and the built React frontend from one process on port 8000.
"""
import os
import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from backend.database import init_db, SessionLocal, Project, Architecture, Task, Milestone
from backend.nlp_extraction import extract_requirements
from backend.rag_retrieval import initialize_rag, retrieve_similar
from backend.knowledge_graph import initialize_kg, lookup_components
from backend.architecture_gen import generate_architecture
from backend.task_breakdown import break_into_tasks
from backend.ai_effort_estimator import estimate_effort, initialize_estimator, get_model_metrics
from backend.milestone_scheduler import schedule_milestones
from backend.cost_estimation import estimate_cloud_costs, analyze_project_risks
from backend.exporter import generate_jira_csv, generate_github_csv, generate_html_report


# ────────────────────────────────────────────────────────────────────────────
#  Logging setup
# ────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(name)-28s │ %(levelname)-5s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


import asyncio

def _async_init_bg():
    try:
        initialize_rag()
        logger.info("✓ RAG index built")
    except Exception as e:
        logger.error(f"✗ RAG initialization failed: {e}")

    try:
        initialize_kg()
        logger.info("✓ Knowledge graph loaded")
    except Exception as e:
        logger.error(f"✗ Knowledge graph loading failed: {e}")

    try:
        initialize_estimator()
        logger.info("✓ AI Effort Estimator trained & ready")
    except Exception as e:
        logger.error(f"✗ AI Effort Estimator initialization failed: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and trigger RAG/KG initialization in background."""
    logger.info("🚀 Initializing Prompt2Plan...")

    # 1. Create database tables
    init_db()
    logger.info("✓ Database initialized")

    # 2. Trigger RAG & Knowledge Graph load in background thread so server starts instantly
    asyncio.create_task(asyncio.to_thread(_async_init_bg))

    logger.info("🎯 Prompt2Plan server listening on http://localhost:8000")
    yield
    logger.info("👋 Shutting down Prompt2Plan...")

    logger.info("👋 Shutting down Prompt2Plan...")


# ────────────────────────────────────────────────────────────────────────────
#  FastAPI app
# ────────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Prompt2Plan",
    description="Prompt in, project plan out.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend dev server during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ────────────────────────────────────────────────────────────────────────────
#  Request / Response models
# ────────────────────────────────────────────────────────────────────────────
class GeneratePlanRequest(BaseModel):
    idea: str


class ProjectResponse(BaseModel):
    id: int
    idea_text: str
    created_at: str
    architecture: dict
    tasks: list[dict]
    milestones: list[dict]


class TaskCreateRequest(BaseModel):
    name: str
    component: str = "General"
    phase: str = "Core Development"
    estimated_hours: float = 4.0
    status: str = "todo"


class TaskUpdateRequest(BaseModel):
    name: str | None = None
    component: str | None = None
    phase: str | None = None
    estimated_hours: float | None = None
    status: str | None = None


class TaskActualHoursRequest(BaseModel):
    actual_hours: float


# ────────────────────────────────────────────────────────────────────────────
#  API Endpoints
# ────────────────────────────────────────────────────────────────────────────

@app.post("/api/generate-plan")
async def generate_plan(request: GeneratePlanRequest):
    """
    Main pipeline endpoint. Takes a project idea and returns a full plan.
    Pipeline: NLP → RAG ∥ KG → Architecture → Tasks → Effort → Milestones → DB
    """
    idea_text = request.idea.strip()

    if not idea_text:
        raise HTTPException(status_code=400, detail="Project idea cannot be empty.")

    if len(idea_text) < 10:
        raise HTTPException(status_code=400, detail="Please provide a more detailed project description (at least 10 characters).")

    try:
        # ── Step 1: NLP Extraction ─────────────────────────────────
        logger.info("Step 1/7: NLP extraction...")
        requirements = await extract_requirements(idea_text)
        logger.info(f"  → Extracted: {requirements['domain']} / {len(requirements['features'])} features")

        # ── Step 2 & 3: RAG + KG (run sequentially for simplicity in v1) ──
        logger.info("Step 2/7: RAG retrieval...")
        rag_results = retrieve_similar(requirements["features"], top_k=3)
        logger.info(f"  → Retrieved {len(rag_results)} similar architectures")

        logger.info("Step 3/7: Knowledge graph lookup...")
        kg_components = lookup_components(requirements["features"])
        logger.info(f"  → Found {len(kg_components['components'])} components, {len(kg_components['dependencies'])} dependencies")

        # ── Step 4: Architecture Generation ────────────────────────
        logger.info("Step 4/7: Generating architecture...")
        architecture = await generate_architecture(requirements, rag_results, kg_components)
        logger.info(f"  → Architecture: {len(architecture['components'])} components, {len(architecture['connections'])} connections")

        # ── Step 5: Task Breakdown ─────────────────────────────────
        logger.info("Step 5/7: Breaking down tasks...")
        tasks = await break_into_tasks(architecture)
        logger.info(f"  → Generated {len(tasks)} tasks")

        # ── Step 6: Effort Estimation ──────────────────────────────
        logger.info("Step 6/7: Estimating effort...")
        tasks = estimate_effort(tasks)

        # ── Step 7: Milestone Scheduling ───────────────────────────
        logger.info("Step 7/7: Scheduling milestones...")
        milestones_data = schedule_milestones(tasks)

        # ── Persist to SQLite ──────────────────────────────────────
        logger.info("Saving to database...")
        project_data = _save_to_db(idea_text, architecture, tasks, milestones_data)

        logger.info(f"✅ Plan generated successfully (Project #{project_data['id']})")

        return JSONResponse(content={
            "success": True,
            "data": project_data,
        })

    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate plan: {str(e)}. Please try again."
        )


@app.get("/api/projects")
async def list_projects():
    """List all saved projects (basic history)."""
    db = SessionLocal()
    try:
        projects = db.query(Project).order_by(Project.created_at.desc()).limit(20).all()
        return JSONResponse(content={
            "success": True,
            "data": [
                {
                    "id": p.id,
                    "idea_text": p.idea_text[:100] + ("..." if len(p.idea_text) > 100 else ""),
                    "created_at": p.created_at.isoformat() if p.created_at else None,
                }
                for p in projects
            ],
        })
    finally:
        db.close()


@app.get("/api/projects/{project_id}")
async def get_project(project_id: int):
    """Retrieve a saved project plan by ID."""
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found.")

        # Load architecture
        arch = db.query(Architecture).filter(Architecture.project_id == project_id).first()
        architecture = json.loads(arch.json_data) if arch else {"components": [], "connections": []}

        # Load tasks
        tasks_db = db.query(Task).filter(Task.project_id == project_id).all()
        tasks = [
            {
                "id": t.id,
                "name": t.name,
                "component": t.component,
                "phase": t.phase,
                "estimated_hours": t.estimated_hours,
                "optimistic_hours": round(t.estimated_hours * 0.75, 1),
                "pessimistic_hours": round(t.estimated_hours * 1.35, 1),
                "actual_hours": t.actual_hours,
                "status": t.status,
            }
            for t in tasks_db
        ]

        # Load milestones
        milestones_db = db.query(Milestone).filter(Milestone.project_id == project_id).all()
        milestones = []
        for m in milestones_db:
            total_h = m.total_hours or 4.0
            opt_h = m.optimistic_hours or round(total_h * 0.75, 1)
            pess_h = m.pessimistic_hours or round(total_h * 1.35, 1)
            total_d = max(1, round(total_h / 6.0))
            opt_d = max(1, round(opt_h / 6.0))
            pess_d = max(1, round(pess_h / 6.0))

            milestones.append({
                "phase_name": m.phase_name,
                "start_day": m.start_day,
                "end_day": m.end_day,
                "total_hours": total_h,
                "optimistic_hours": opt_h,
                "pessimistic_hours": pess_h,
                "total_days": total_d,
                "optimistic_days": opt_d,
                "pessimistic_days": pess_d,
            })

        cost_estimate = estimate_cloud_costs(architecture)
        risk_analysis = analyze_project_risks({}, architecture, tasks)

        return JSONResponse(content={
            "success": True,
            "data": {
                "id": project.id,
                "idea_text": project.idea_text,
                "created_at": project.created_at.isoformat() if project.created_at else None,
                "architecture": architecture,
                "tasks": tasks,
                "milestones": milestones,
                "cost_estimate": cost_estimate,
                "risk_analysis": risk_analysis,
            },
        })
    finally:
        db.close()


@app.get("/api/projects/{project_id}/export")
async def export_project(project_id: int, format: str = "markdown"):
    """Export project plan in Markdown, JSON, or text format."""
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found.")

        arch = db.query(Architecture).filter(Architecture.project_id == project_id).first()
        architecture = json.loads(arch.json_data) if arch else {"components": [], "connections": []}

        tasks_db = db.query(Task).filter(Task.project_id == project_id).all()
        tasks = [
            {
                "id": t.id,
                "name": t.name,
                "component": t.component,
                "phase": t.phase,
                "estimated_hours": t.estimated_hours,
                "status": t.status,
            }
            for t in tasks_db
        ]

        milestones_db = db.query(Milestone).filter(Milestone.project_id == project_id).all()
        milestones = [
            {
                "phase_name": m.phase_name,
                "start_day": m.start_day,
                "end_day": m.end_day,
                "total_hours": m.total_hours,
            }
            for m in milestones_db
        ]

        cost_estimate = estimate_cloud_costs(architecture)
        risk_analysis = analyze_project_risks({}, architecture, tasks)

        data = {
            "id": project.id,
            "idea_text": project.idea_text,
            "created_at": project.created_at.isoformat() if project.created_at else "",
            "architecture": architecture,
            "tasks": tasks,
            "milestones": milestones,
            "cost_estimate": cost_estimate,
            "risk_analysis": risk_analysis,
        }

        if format.lower() == "json":
            return JSONResponse(
                content=data,
                headers={"Content-Disposition": f"attachment; filename=plan-{project_id}.json"}
            )

        fmt = format.lower().strip()
        if fmt in ("jira_csv", "jira"):
            jira_csv = generate_jira_csv(data)
            return Response(
                content=jira_csv,
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=plan-{project_id}-jira.csv"}
            )
        elif fmt in ("github_csv", "github"):
            github_csv = generate_github_csv(data)
            return Response(
                content=github_csv,
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=plan-{project_id}-github.csv"}
            )
        elif fmt in ("html", "pdf"):
            html_report = generate_html_report(data)
            return Response(
                content=html_report,
                media_type="text/html",
                headers={"Content-Disposition": f"inline; filename=plan-{project_id}-report.html"}
            )

        # Default to Markdown export
        md_content = _generate_markdown_content(data)
        return Response(
            content=md_content,
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename=plan-{project_id}.md"}
        )
    finally:
        db.close()


# ────────────────────────────────────────────────────────────────────────────
#  Task CRUD & Dynamic Recalculation Endpoints (Phase 10)
# ────────────────────────────────────────────────────────────────────────────

def _recalculate_project_milestones(db, project_id: int):
    """Re-schedule milestones and update risk/cost models in DB based on current tasks."""
    tasks_db = db.query(Task).filter(Task.project_id == project_id).all()
    task_dicts = [
        {
            "id": t.id,
            "name": t.name,
            "component": t.component,
            "phase": t.phase,
            "estimated_hours": t.estimated_hours,
            "status": t.status,
        }
        for t in tasks_db
    ]
    
    # Recalculate scheduled milestones
    new_milestones = schedule_milestones(task_dicts)
    
    # Clear existing milestones and insert new
    db.query(Milestone).filter(Milestone.project_id == project_id).delete()
    saved_milestones = []
    for ms in new_milestones:
        db_ms = Milestone(
            project_id=project_id,
            phase_name=ms["phase_name"],
            start_day=ms["start_day"],
            end_day=ms["end_day"],
            total_hours=ms.get("total_hours", 0),
        )
        db.add(db_ms)
        saved_milestones.append({
            "phase_name": ms["phase_name"],
            "description": ms.get("description", ""),
            "start_day": ms["start_day"],
            "end_day": ms["end_day"],
            "total_hours": ms.get("total_hours", 0),
            "total_days": ms.get("total_days", 1),
            "tasks": ms.get("tasks", []),
        })
    db.commit()
    return task_dicts, saved_milestones


@app.post("/api/projects/{project_id}/tasks")
async def add_task(project_id: int, request: TaskCreateRequest):
    """Add a custom task to an existing project and recalculate timeline."""
    db = SessionLocal()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found.")
            
        new_task = Task(
            project_id=project_id,
            name=request.name,
            component=request.component,
            phase=request.phase,
            estimated_hours=request.estimated_hours,
            status=request.status,
        )
        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        task_dicts, updated_milestones = _recalculate_project_milestones(db, project_id)

        arch = db.query(Architecture).filter(Architecture.project_id == project_id).first()
        architecture = json.loads(arch.json_data) if arch else {"components": [], "connections": []}

        return JSONResponse(content={
            "success": True,
            "message": "Task created successfully",
            "data": {
                "tasks": task_dicts,
                "milestones": updated_milestones,
                "cost_estimate": estimate_cloud_costs(architecture),
                "risk_analysis": analyze_project_risks({}, architecture, task_dicts),
            }
        })
    finally:
        db.close()


@app.put("/api/projects/{project_id}/tasks/{task_id}")
async def update_task(project_id: int, task_id: int, request: TaskUpdateRequest):
    """Update properties of an existing task (status, hours, phase, component, name)."""
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id, Task.project_id == project_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found.")

        if request.name is not None:
            task.name = request.name
        if request.component is not None:
            task.component = request.component
        if request.phase is not None:
            task.phase = request.phase
        if request.estimated_hours is not None:
            task.estimated_hours = request.estimated_hours
        if request.status is not None:
            task.status = request.status

        db.commit()

        task_dicts, updated_milestones = _recalculate_project_milestones(db, project_id)

        arch = db.query(Architecture).filter(Architecture.project_id == project_id).first()
        architecture = json.loads(arch.json_data) if arch else {"components": [], "connections": []}

        return JSONResponse(content={
            "success": True,
            "message": "Task updated successfully",
            "data": {
                "tasks": task_dicts,
                "milestones": updated_milestones,
                "cost_estimate": estimate_cloud_costs(architecture),
                "risk_analysis": analyze_project_risks({}, architecture, task_dicts),
            }
        })
    finally:
        db.close()


@app.delete("/api/projects/{project_id}/tasks/{task_id}")
async def delete_task(project_id: int, task_id: int):
    """Delete a task from a project and recalculate timeline."""
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id, Task.project_id == project_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found.")

        db.delete(task)
        db.commit()

        task_dicts, updated_milestones = _recalculate_project_milestones(db, project_id)

        arch = db.query(Architecture).filter(Architecture.project_id == project_id).first()
        architecture = json.loads(arch.json_data) if arch else {"components": [], "connections": []}

        return JSONResponse(content={
            "success": True,
            "message": "Task deleted successfully",
            "data": {
                "tasks": task_dicts,
                "milestones": updated_milestones,
                "cost_estimate": estimate_cloud_costs(architecture),
                "risk_analysis": analyze_project_risks({}, architecture, task_dicts),
            }
        })
    finally:
        db.close()

@app.patch("/api/tasks/{task_id}/actual-hours")
async def log_actual_hours(task_id: int, request: TaskActualHoursRequest):
    """Log actual hours spent on a completed task for feedback training."""
    db = SessionLocal()
    try:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise HTTPException(status_code=404, detail="Task not found.")

        task.actual_hours = request.actual_hours
        task.status = "done"
        db.commit()

        return JSONResponse(content={
            "success": True,
            "message": f"Logged {request.actual_hours} actual hours for task {task_id}",
            "data": {
                "id": task.id,
                "name": task.name,
                "estimated_hours": task.estimated_hours,
                "actual_hours": task.actual_hours,
                "status": task.status,
            }
        })
    finally:
        db.close()


@app.get("/api/model-metrics")
async def get_metrics():
    """Retrieve held-out test evaluation metrics (MMRE and PRED(25))."""
    metrics = get_model_metrics()
    return JSONResponse(content={
        "success": True,
        "metrics": metrics,
    })


# ────────────────────────────────────────────────────────────────────────────
#  Database helpers
# ────────────────────────────────────────────────────────────────────────────

def _save_to_db(idea_text: str, architecture: dict, tasks: list[dict], milestones: list[dict]) -> dict:
    """Persist the full plan to SQLite and return the structured response."""
    init_db()
    db = SessionLocal()
    try:
        # Create project
        project = Project(idea_text=idea_text)
        db.add(project)
        db.flush()  # Get the project ID

        # Save architecture
        arch = Architecture(
            project_id=project.id,
            json_data=json.dumps(architecture),
        )
        db.add(arch)

        # Save tasks
        saved_tasks = []
        for task in tasks:
            est_h = task.get("estimated_hours", 4.0)
            opt_h = task.get("optimistic_hours", round(est_h * 0.75, 1))
            pess_h = task.get("pessimistic_hours", round(est_h * 1.35, 1))

            db_task = Task(
                project_id=project.id,
                name=task["name"],
                component=task.get("component", ""),
                phase=task.get("phase", _get_task_phase(task, milestones)),
                estimated_hours=est_h,
                status="todo",
            )
            db.add(db_task)
            saved_tasks.append({
                "name": task["name"],
                "component": task.get("component", ""),
                "phase": db_task.phase,
                "estimated_hours": est_h,
                "optimistic_hours": opt_h,
                "pessimistic_hours": pess_h,
                "status": "todo",
                "type": task.get("type", "backend"),
            })

        # Save milestones
        saved_milestones = []
        for ms in milestones:
            tot_h = ms.get("total_hours", 0)
            opt_h = ms.get("optimistic_hours", round(tot_h * 0.75, 1))
            pess_h = ms.get("pessimistic_hours", round(tot_h * 1.35, 1))

            db_milestone = Milestone(
                project_id=project.id,
                phase_name=ms["phase_name"],
                start_day=ms["start_day"],
                end_day=ms["end_day"],
                total_hours=tot_h,
                optimistic_hours=opt_h,
                pessimistic_hours=pess_h,
            )
            db.add(db_milestone)
            saved_milestones.append({
                "phase_name": ms["phase_name"],
                "description": ms.get("description", ""),
                "start_day": ms["start_day"],
                "end_day": ms["end_day"],
                "total_hours": tot_h,
                "optimistic_hours": opt_h,
                "pessimistic_hours": pess_h,
                "total_days": ms.get("total_days", 1),
                "optimistic_days": ms.get("optimistic_days", max(1, round(opt_h / 6.0))),
                "pessimistic_days": ms.get("pessimistic_days", max(1, round(pess_h / 6.0))),
                "tasks": ms.get("tasks", []),
            })

        db.commit()

        cost_estimate = estimate_cloud_costs(architecture)
        risk_analysis = analyze_project_risks({}, architecture, saved_tasks)

        return {
            "id": project.id,
            "idea_text": idea_text,
            "created_at": project.created_at.isoformat() if project.created_at else None,
            "architecture": architecture,
            "tasks": saved_tasks,
            "milestones": saved_milestones,
            "cost_estimate": cost_estimate,
            "risk_analysis": risk_analysis,
        }
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def _generate_markdown_content(project_data: dict) -> str:
    """Generate clean GitHub-flavored markdown document for exporting plans."""
    lines = []
    lines.append(f"# ⚡ Prompt2Plan Project Document: Plan #{project_data['id']}\n")
    lines.append(f"> **Project Idea:** {project_data.get('idea_text')}\n")
    lines.append(f"**Generated Date:** {project_data.get('created_at', 'N/A')}\n")
    lines.append("---\n")

    # Overview Metrics
    risk = project_data.get("risk_analysis", {})
    cost = project_data.get("cost_estimate", {})
    lines.append("## 📊 Overview Metrics")
    lines.append(f"- **Complexity Rating:** {risk.get('complexity_score', 5.0)} / 10 ({risk.get('complexity_level', 'Moderate')})")
    lines.append(f"- **Total Estimated Effort:** {risk.get('estimated_total_hours', 0)} Developer Hours")
    lines.append(f"- **Monthly Infrastructure Estimate:** ${cost.get('starter_tier_monthly', 0)} (Starter) — ${cost.get('growth_tier_monthly', 0)} (Growth)")
    lines.append("")

    # Architecture
    arch = project_data.get("architecture", {})
    lines.append("## 🏗️ System Architecture")
    lines.append("```mermaid")
    lines.append("graph TD")
    for comp in arch.get("components", []):
        c_id = comp["id"].replace("-", "_")
        lines.append(f"  {c_id}[\"{comp['name']} ({comp['type']})\"]")
    for conn in arch.get("connections", []):
        f_id = conn["from"].replace("-", "_")
        t_id = conn["to"].replace("-", "_")
        lbl = conn.get("label", "")
        if lbl:
            lines.append(f"  {f_id} -->|\"{lbl}\"| {t_id}")
        else:
            lines.append(f"  {f_id} --> {t_id}")
    lines.append("```")
    lines.append("")

    # Task Breakdown
    lines.append("## 📋 Task Breakdown")
    lines.append("| Task Name | Component | Phase | Est. Hours |")
    lines.append("|---|---|---|---|")
    for t in project_data.get("tasks", []):
        lines.append(f"| {t.get('name')} | {t.get('component')} | {t.get('phase')} | {t.get('estimated_hours')}h |")
    lines.append("")

    # Milestone Timeline
    lines.append("## 📅 Milestone Timeline")
    lines.append("| Phase Name | Start Day | End Day | Total Hours |")
    lines.append("|---|---|---|---|")
    for ms in project_data.get("milestones", []):
        lines.append(f"| {ms.get('phase_name')} | Day {ms.get('start_day')} | Day {ms.get('end_day')} | {ms.get('total_hours')}h |")
    lines.append("")

    # Risk Assessment
    if risk.get("risks"):
        lines.append("## ⚠️ Technical Risk Assessment")
        lines.append("| Category | Identified Risk | Impact | Recommended Mitigation |")
        lines.append("|---|---|---|---|")
        for r in risk["risks"]:
            lines.append(f"| {r.get('category')} | {r.get('risk')} | {r.get('impact')} | {r.get('mitigation')} |")
        lines.append("")

    return "\n".join(lines)



def _get_task_phase(task: dict, milestones: list[dict]) -> str:
    """Find which phase a task belongs to based on milestone data."""
    task_name = task.get("name", "")
    for ms in milestones:
        for ms_task in ms.get("tasks", []):
            if ms_task.get("name") == task_name:
                return ms["phase_name"]
    return "Core Development"


# ────────────────────────────────────────────────────────────────────────────
#  Static file serving (MUST come AFTER all /api/* routes)
# ────────────────────────────────────────────────────────────────────────────
FRONTEND_DIST = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")

# Mount static assets if the frontend is built
if os.path.isdir(os.path.join(FRONTEND_DIST, "assets")):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")


@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """Catch-all route: serve static asset files or fallback to index.html with no-cache headers."""
    no_cache_headers = {"Cache-Control": "no-cache, no-store, must-revalidate", "Pragma": "no-cache"}
    
    if full_path:
        clean_path = full_path.lstrip("/").replace("\\", "/")
        target_file = os.path.join(FRONTEND_DIST, clean_path)
        if os.path.isfile(target_file):
            return FileResponse(target_file, headers=no_cache_headers)

    index_path = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path, headers=no_cache_headers)

    # If frontend isn't built yet, return a helpful message
    return JSONResponse(
        status_code=503,
        content={
            "message": "Frontend not built yet. Run 'py run.py' to build and start Prompt2Plan.",
        },
    )


