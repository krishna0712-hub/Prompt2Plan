"""
cost_estimation.py — Cloud cost estimation & risk analysis for Prompt2Plan
"""
import math

COMPONENT_COST_FACTORS = {
    "database": {"starter": 15, "growth": 60, "scale": 250, "unit": "managed DB instance"},
    "storage": {"starter": 5, "growth": 25, "scale": 100, "unit": "object storage & CDN"},
    "cache": {"starter": 10, "growth": 45, "scale": 180, "unit": "managed Redis"},
    "backend": {"starter": 10, "growth": 40, "scale": 200, "unit": "compute nodes / serverless"},
    "frontend": {"starter": 0, "growth": 20, "scale": 100, "unit": "CDN hosting & edge bandwidth"},
    "integration": {"starter": 15, "growth": 50, "scale": 300, "unit": "API provider usage / webhooks"},
}


def estimate_cloud_costs(architecture: dict, scale: str = "medium") -> dict:
    """
    Calculate estimated monthly cloud infrastructure & service costs based on components.
    """
    components = architecture.get("components", [])
    
    starter_total = 10  # Base DNS, SSL, monitoring
    growth_total = 40
    scale_total = 150
    
    breakdown = []
    
    for comp in components:
        comp_type = comp.get("type", "backend")
        comp_name = comp.get("name", "Component")
        factors = COMPONENT_COST_FACTORS.get(comp_type, COMPONENT_COST_FACTORS["backend"])
        
        starter_val = factors["starter"]
        growth_val = factors["growth"]
        scale_val = factors["scale"]
        
        starter_total += starter_val
        growth_total += growth_val
        scale_total += scale_val
        
        breakdown.append({
            "component": comp_name,
            "type": comp_type,
            "starter_monthly_usd": starter_val,
            "growth_monthly_usd": growth_val,
            "scale_monthly_usd": scale_val,
            "notes": factors["unit"]
        })

    return {
        "currency": "USD",
        "starter_tier_monthly": starter_total,
        "growth_tier_monthly": growth_total,
        "scale_tier_monthly": scale_total,
        "breakdown": breakdown
    }


def analyze_project_risks(requirements: dict, architecture: dict, tasks: list[dict]) -> dict:
    """
    Generate automated technical risk evaluation and complexity rating.
    """
    features = requirements.get("features", [])
    components = architecture.get("components", [])
    total_hours = sum(t.get("estimated_hours", 4) for t in tasks)
    
    # Calculate complexity score out of 10
    comp_count = len(components)
    feat_count = len(features)
    
    complexity_score = min(10.0, round(2.0 + (comp_count * 0.5) + (total_hours / 30.0), 1))
    
    if complexity_score < 4.0:
        complexity_level = "Low"
    elif complexity_score < 7.0:
        complexity_level = "Moderate"
    elif complexity_score < 8.5:
        complexity_level = "High"
    else:
        complexity_level = "Very High"
        
    risks = []
    
    # Check specific component presence
    types_present = set(c.get("type") for c in components)
    names_lower = [c.get("name", "").lower() for c in components]
    
    if "integration" in types_present or any("payment" in n or "gateway" in n for n in names_lower):
        risks.append({
            "category": "Third-Party Integration",
            "risk": "Reliance on external API webhooks & payment gateways",
            "impact": "High",
            "mitigation": "Implement webhooks idempotent handling, dead-letter queues, and sandbox test harnesses."
        })
        
    if "websocket_server" in [c.get("id") for c in components] or any("real-time" in f.lower() or "chat" in f.lower() for f in features):
        risks.append({
            "category": "Scalability & Concurrency",
            "risk": "Real-time state synchronization under high concurrent load",
            "impact": "Medium",
            "mitigation": "Use Redis pub/sub for WebSocket connection scaling across worker instances."
        })
        
    if any("auth" in n or "user" in n for n in names_lower):
        risks.append({
            "category": "Security & Compliance",
            "risk": "User authentication, JWT token storage, and session security",
            "impact": "High",
            "mitigation": "Enforce HTTP-only secure cookies, short-lived JWTs with refresh token rotation."
        })
        
    if "database" in types_present:
        risks.append({
            "category": "Data Management",
            "risk": "Database schema migrations and relational query optimization",
            "impact": "Medium",
            "mitigation": "Use migration tools (e.g., Alembic/Prisma) with continuous backup automated scripts."
        })
        
    if not risks:
        risks.append({
            "category": "General Engineering",
            "risk": "Scope expansion during initial development phase",
            "impact": "Low",
            "mitigation": "Focus strictly on Phase 1 MVP features before adding auxiliary components."
        })

    return {
        "complexity_score": complexity_score,
        "complexity_level": complexity_level,
        "estimated_total_hours": total_hours,
        "risks": risks
    }
