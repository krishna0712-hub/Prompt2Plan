"""
eval_benchmark.py — Evaluation dataset and quality benchmark for Prompt2Plan.
Contains:
- 10 semantic-search queries
- 5 architecture-generation test cases
- 5 timeline-estimation test cases
- 5 task-breakdown test cases
"""
import os
import sys
import json
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HOME"] = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".cache", "huggingface")

# 10 semantic search queries
SEARCH_QUERIES = [
    ["user_auth", "payments", "shopping_cart", "product_listing"],  # E-commerce
    ["chat", "real_time_tracking", "notifications", "user_profiles"],  # Social / Real-time
    ["appointments", "doctor", "health", "video_streaming"],  # Healthcare
    ["course", "student", "video_streaming", "user_auth"],  # EdTech
    ["analytics", "admin_dashboard", "metrics", "reports"],  # SaaS / Analytics
    ["order_tracking", "delivery", "gps", "notifications"],  # Logistics
    ["reviews", "recommendations", "social_features", "search"],  # Social Discovery
    ["file_upload", "collaboration", "real_time", "user_auth"],  # Collaborative Workspace
    ["iot", "sensor", "analytics", "real_time_tracking"],  # IoT
    ["finance", "payments", "billing", "analytics"],  # Fintech
]

# 5 architecture test cases
ARCH_TEST_CASES = [
    {
        "domain": "e-commerce",
        "scale": "medium",
        "project_type": "web_app",
        "features": ["user_auth", "payments", "shopping_cart", "product_listing", "search"]
    },
    {
        "domain": "healthcare",
        "scale": "medium",
        "project_type": "web_app",
        "features": ["user_auth", "appointments", "video_streaming", "notifications"]
    },
    {
        "domain": "fintech",
        "scale": "large",
        "project_type": "web_app",
        "features": ["user_auth", "payments", "analytics", "admin_dashboard", "notifications"]
    },
    {
        "domain": "social",
        "scale": "large",
        "project_type": "mobile_app",
        "features": ["user_auth", "chat", "user_profiles", "social_features", "notifications"]
    },
    {
        "domain": "logistics",
        "scale": "small",
        "project_type": "web_app",
        "features": ["user_auth", "real_time_tracking", "order_tracking", "notifications"]
    }
]

# 5 timeline / effort estimation test cases
TIMELINE_TEST_CASES = [
    [
        {"name": "Setup PostgreSQL database schema and migrations", "component": "Database", "type": "setup"},
        {"name": "Implement user authentication with JWT and refresh tokens", "component": "Auth Service", "type": "backend"},
        {"name": "Build responsive React checkout flow and cart UI", "component": "Web Frontend", "type": "ui"},
        {"name": "Integrate Stripe payment intent webhook processor", "component": "Payment Gateway", "type": "integration"},
        {"name": "Write automated end-to-end integration test suite", "component": "Testing", "type": "testing"},
    ],
    [
        {"name": "Configure Redis cluster and pub-sub channels", "component": "Cache", "type": "setup"},
        {"name": "Build WebSocket real-time messaging gateway", "component": "Chat Service", "type": "backend"},
        {"name": "Implement user direct message chat screen in React", "component": "Web Frontend", "type": "ui"},
        {"name": "Add push notification dispatch for offline users", "component": "Notification Service", "type": "integration"},
        {"name": "Perform load testing for 10k concurrent connections", "component": "Testing", "type": "testing"},
    ],
    [
        {"name": "Design HIPAA compliant encrypted patient record store", "component": "Database", "type": "setup"},
        {"name": "Develop appointment scheduling REST API endpoints", "component": "API Server", "type": "backend"},
        {"name": "Build doctor availability calendar booking component", "component": "Web Frontend", "type": "ui"},
        {"name": "Integrate Twilio video WebRTC consultation room", "component": "Video Gateway", "type": "integration"},
        {"name": "Security audit and vulnerability penetration test", "component": "Testing", "type": "testing"},
    ],
    [
        {"name": "Setup time-series database for IoT sensor ingestion", "component": "Database", "type": "setup"},
        {"name": "Build streaming telemetry data processor pipeline", "component": "Backend", "type": "backend"},
        {"name": "Create real-time device health telemetry dashboard", "component": "Frontend", "type": "ui"},
        {"name": "MQTT broker hardware device bridge integration", "component": "Integration", "type": "integration"},
        {"name": "Simulated hardware sensor failure testing", "component": "Testing", "type": "testing"},
    ],
    [
        {"name": "Initialize Docker containers and CI/CD pipeline", "component": "Infrastructure", "type": "setup"},
        {"name": "Implement multi-tenant ledger and transaction engine", "component": "Core API", "type": "backend"},
        {"name": "Build executive financial analytics charts and metrics", "component": "Frontend", "type": "ui"},
        {"name": "Connect Plaid banking verification API provider", "component": "Integration", "type": "integration"},
        {"name": "Execute financial reconciliation test validation", "component": "Testing", "type": "testing"},
    ]
]

# 5 task breakdown test cases (components)
BREAKDOWN_TEST_CASES = [
    {"id": "web_frontend", "name": "Web Frontend", "type": "frontend"},
    {"id": "auth_service", "name": "Auth Service", "type": "backend"},
    {"id": "payment_gateway", "name": "Payment Gateway", "type": "integration"},
    {"id": "search_service", "name": "Search Engine", "type": "backend"},
    {"id": "analytics_dashboard", "name": "Analytics Dashboard", "type": "dashboard_ui"},
]
