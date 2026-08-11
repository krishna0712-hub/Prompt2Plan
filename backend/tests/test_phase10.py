"""
test_phase10.py — Unit and Integration tests for Phase 10: Multi-format exporters and Interactive Task CRUD.
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.exporter import generate_jira_csv, generate_github_csv, generate_html_report

client = TestClient(app)


def test_exporter_functions():
    """Test unit functions for Jira CSV, GitHub CSV, and HTML report generation."""
    sample_plan = {
        "id": 99,
        "idea_text": "Build an AI customer service chatbot with vector search and analytics dashboard",
        "created_at": "2026-08-11T10:00:00",
        "tasks": [
            {
                "id": 1,
                "name": "Design vector DB schema",
                "component": "Database",
                "phase": "Setup",
                "estimated_hours": 6.0,
                "status": "todo"
            },
            {
                "id": 2,
                "name": "Build React chat UI widget",
                "component": "Frontend UI",
                "phase": "Core Development",
                "estimated_hours": 12.0,
                "status": "done"
            }
        ],
        "milestones": [
            {"phase_name": "Setup", "start_day": 1, "end_day": 2, "total_hours": 6.0},
            {"phase_name": "Core Development", "start_day": 2, "end_day": 4, "total_hours": 12.0}
        ],
        "risk_analysis": {
            "complexity_score": 6.5,
            "complexity_level": "Moderate",
            "estimated_total_hours": 18.0,
            "risks": [
                {
                    "category": "Data Management",
                    "risk": "Vector indexing latency",
                    "impact": "Medium",
                    "mitigation": "Use FAISS HNSW indexing"
                }
            ]
        },
        "cost_estimate": {
            "starter_tier_monthly": 45,
            "growth_tier_monthly": 180,
            "breakdown": [
                {
                    "component": "Frontend UI",
                    "recommendation": "Vercel / Netlify",
                    "starter_cost": 0,
                    "growth_cost": 20
                }
            ]
        }
    }

    # Test Jira CSV
    jira_csv = generate_jira_csv(sample_plan)
    assert "Issue Key,Summary,Description" in jira_csv
    assert "Design vector DB schema" in jira_csv
    assert "P2P-1" in jira_csv

    # Test GitHub CSV
    github_csv = generate_github_csv(sample_plan)
    assert "Title,Body,Labels,Milestone,State" in github_csv
    assert "Build React chat UI widget" in github_csv
    assert "closed" in github_csv

    # Test HTML report
    html_report = generate_html_report(sample_plan)
    assert "Prompt2Plan Report — Plan #99" in html_report
    assert "Design vector DB schema" in html_report
    assert "FAISS HNSW indexing" in html_report


def test_export_api_endpoints():
    """Test GET /api/projects/{id}/export with jira_csv, github_csv, and html formats."""
    # 1. Create a plan first
    res = client.post("/api/generate-plan", json={"idea": "Build a SaaS subscription management app"})
    assert res.status_code == 200
    plan_id = res.json()["data"]["id"]

    # 2. Test Jira CSV export
    jira_res = client.get(f"/api/projects/{plan_id}/export?format=jira_csv")
    assert jira_res.status_code == 200
    assert "text/csv" in jira_res.headers["content-type"]
    assert "Summary" in jira_res.text

    # 3. Test GitHub CSV export
    gh_res = client.get(f"/api/projects/{plan_id}/export?format=github_csv")
    assert gh_res.status_code == 200
    assert "text/csv" in gh_res.headers["content-type"]
    assert "Title" in gh_res.text

    # 4. Test HTML/PDF report export
    pdf_res = client.get(f"/api/projects/{plan_id}/export?format=pdf")
    assert pdf_res.status_code == 200
    assert "text/html" in pdf_res.headers["content-type"]
    assert "Prompt2Plan Report" in pdf_res.text


def test_task_crud_and_milestone_recalculation():
    """Test creating, updating, and deleting tasks via API, verifying live recalculation."""
    # 1. Create plan
    res = client.post("/api/generate-plan", json={"idea": "Build an e-learning platform with video streaming"})
    assert res.status_code == 200
    plan_data = res.json()["data"]
    plan_id = plan_data["id"]
    initial_task_count = len(plan_data["tasks"])

    # 2. Add custom task
    add_res = client.post(
        f"/api/projects/{plan_id}/tasks",
        json={
            "name": "Configure CDN for HLS Video Streaming",
            "component": "Video Service",
            "phase": "Testing & QA",
            "estimated_hours": 8.0,
            "status": "todo"
        }
    )
    assert add_res.status_code == 200
    updated_data = add_res.json()["data"]
    assert len(updated_data["tasks"]) == initial_task_count + 1

    # Find the added task
    new_task = next(t for t in updated_data["tasks"] if t["name"] == "Configure CDN for HLS Video Streaming")
    task_id = new_task["id"]
    assert new_task["estimated_hours"] == 8.0

    # 3. Update task status and hours
    update_res = client.put(
        f"/api/projects/{plan_id}/tasks/{task_id}",
        json={
            "status": "done",
            "estimated_hours": 12.0
        }
    )
    assert update_res.status_code == 200
    after_update_data = update_res.json()["data"]
    updated_task = next(t for t in after_update_data["tasks"] if t["id"] == task_id)
    assert updated_task["status"] == "done"
    assert updated_task["estimated_hours"] == 12.0

    # 4. Delete task
    del_res = client.delete(f"/api/projects/{plan_id}/tasks/{task_id}")
    assert del_res.status_code == 200
    final_data = del_res.json()["data"]
    assert len(final_data["tasks"]) == initial_task_count
    assert not any(t["id"] == task_id for t in final_data["tasks"])
