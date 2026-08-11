"""
test_api.py — Unit and integration tests for Prompt2Plan FastAPI endpoints
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_list_projects_endpoint():
    """Test GET /api/projects endpoint."""
    response = client.get("/api/projects")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert isinstance(data["data"], list)


def test_generate_plan_validation():
    """Test POST /api/generate-plan validation errors for empty / short input."""
    # Test empty string
    res_empty = client.post("/api/generate-plan", json={"idea": ""})
    assert res_empty.status_code == 400
    assert "empty" in res_empty.json()["detail"].lower()

    # Test short string (< 10 chars)
    res_short = client.post("/api/generate-plan", json={"idea": "short"})
    assert res_short.status_code == 400
    assert "detailed" in res_short.json()["detail"].lower()


def test_full_generate_plan_and_export():
    """Test full pipeline plan generation, fetch by ID, and export in Markdown & JSON."""
    test_idea = "Build a subscription SaaS platform for AI automated code reviews with payment gateway and GitHub integration"
    
    # 1. Generate plan
    response = client.post("/api/generate-plan", json={"idea": test_idea})
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["success"] is True
    
    plan = res_data["data"]
    assert "id" in plan
    project_id = plan["id"]
    assert len(plan["architecture"]["components"]) > 0
    assert len(plan["tasks"]) > 0
    assert len(plan["milestones"]) > 0
    assert "cost_estimate" in plan
    assert "risk_analysis" in plan

    # 2. Fetch generated plan by ID
    get_res = client.get(f"/api/projects/{project_id}")
    assert get_res.status_code == 200
    fetched_plan = get_res.json()["data"]
    assert fetched_plan["id"] == project_id
    assert fetched_plan["idea_text"] == test_idea

    # 3. Export Markdown
    export_md = client.get(f"/api/projects/{project_id}/export?format=markdown")
    assert export_md.status_code == 200
    assert "text/markdown" in export_md.headers["content-type"]
    assert "Prompt2Plan" in export_md.text
    assert "System Architecture" in export_md.text

    # 4. Export JSON
    export_json = client.get(f"/api/projects/{project_id}/export?format=json")
    assert export_json.status_code == 200
    assert export_json.json()["id"] == project_id
