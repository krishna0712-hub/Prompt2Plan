"""
test_pipeline.py — Unit tests for NLP, RAG, Knowledge Graph, Effort, and Cost modules
"""
import pytest
import asyncio

from backend.nlp_extraction import _rule_based_extract
from backend.knowledge_graph import lookup_components
from backend.ai_effort_estimator import estimate_effort, get_model_metrics
from backend.cost_estimation import estimate_cloud_costs, analyze_project_risks


def test_rule_based_nlp_extraction():
    """Test NLP extraction fallback rule logic."""
    idea = "Build a real-time chat mobile application with vector DB search and user login"
    extracted = _rule_based_extract(idea)


    
    assert "features" in extracted
    assert len(extracted["features"]) > 0
    assert any("chat" in f.lower() or "search" in f.lower() for f in extracted["features"])


def test_knowledge_graph_lookup():
    """Test Knowledge Graph fuzzy component and dependency lookup."""
    features = ["user authentication", "payment checkout", "real-time chat", "vector database"]
    kg_data = lookup_components(features)
    
    assert "components" in kg_data
    assert "dependencies" in kg_data
    comp_names = [c["name"].lower() for c in kg_data["components"]]
    assert any("auth" in n or "user" in n for n in comp_names)


def test_ai_effort_estimation():
    """Test learned effort calculation with PERT range fields."""
    sample_tasks = [
        {"name": "Create database schema", "component": "User DB", "type": "database"},
        {"name": "Build login interface", "component": "Login UI", "type": "frontend"},
        {"name": "Implement payment webhook", "component": "Payment Gateway", "type": "integration"},
    ]
    estimated = estimate_effort(sample_tasks)
    
    assert len(estimated) == 3
    for task in estimated:
        assert "estimated_hours" in task
        assert "optimistic_hours" in task
        assert "pessimistic_hours" in task
        assert task["optimistic_hours"] <= task["estimated_hours"] <= task["pessimistic_hours"]
        assert task["estimated_hours"] > 0

    metrics = get_model_metrics()
    assert "mmre" in metrics
    assert "pred_25" in metrics


def test_cost_and_risk_estimation():
    """Test cloud infrastructure cost and risk analyzer."""
    architecture = {
        "components": [
            {"id": "auth_ui", "name": "Auth UI", "type": "frontend"},
            {"id": "auth_service", "name": "Auth Service", "type": "backend"},
            {"id": "user_db", "name": "User DB", "type": "database"},
            {"id": "payment_gateway", "name": "Payment Gateway", "type": "integration"},
        ],
        "connections": []
    }
    
    costs = estimate_cloud_costs(architecture)
    assert costs["starter_tier_monthly"] > 0
    assert costs["growth_tier_monthly"] >= costs["starter_tier_monthly"]
    assert len(costs["breakdown"]) == 4
    
    risks = analyze_project_risks({"features": ["payments", "auth"]}, architecture, [])
    assert "complexity_score" in risks
    assert "complexity_level" in risks
    assert len(risks["risks"]) > 0
