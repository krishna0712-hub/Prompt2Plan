"""
task_breakdown.py — Step 5: Expand each component into concrete dev tasks
Uses a local template dictionary first, then LLM for unrecognized components.
"""
import logging
from backend.llm_client import call_llm, parse_json_response

logger = logging.getLogger(__name__)

# ────────────────────────────────────────────────────────────────────────────
#  Task templates: component type/name → common development tasks
# ────────────────────────────────────────────────────────────────────────────
TASK_TEMPLATES = {
    # --- Frontend components ---
    "frontend": [
        "Design and implement UI layouts",
        "Build reusable component library",
        "Implement responsive design",
        "Add form validation and error handling",
    ],
    "web_frontend": [
        "Set up React/Next.js project structure",
        "Design and implement responsive layouts",
        "Build navigation and routing",
        "Implement state management",
    ],
    "mobile_app": [
        "Set up React Native / Flutter project",
        "Design mobile-first UI components",
        "Implement native navigation",
        "Add offline support and data sync",
    ],
    "admin_ui": [
        "Build admin dashboard layout",
        "Implement data tables with sorting and filtering",
        "Create admin CRUD interfaces",
        "Add role-based view restrictions",
    ],
    "dashboard_ui": [
        "Design dashboard layout with widgets",
        "Implement chart and graph components",
        "Add real-time data refresh",
        "Build customizable dashboard views",
    ],

    # --- Backend services ---
    "auth_service": [
        "Implement user registration and login",
        "Set up JWT token generation and validation",
        "Add password hashing and reset flow",
        "Implement role-based access control",
    ],
    "api_gateway": [
        "Set up API gateway with route definitions",
        "Implement request validation middleware",
        "Add rate limiting and throttling",
        "Configure CORS and security headers",
    ],
    "api_server": [
        "Design RESTful API endpoints",
        "Implement request/response serialization",
        "Add error handling middleware",
        "Set up API versioning",
    ],
    "notification_service": [
        "Set up notification event system",
        "Implement email notification templates",
        "Add push notification support",
        "Build notification preferences management",
    ],
    "search_service": [
        "Set up full-text search index",
        "Implement search query parser",
        "Add filters and faceted search",
        "Optimize search performance and relevance",
    ],
    "analytics_service": [
        "Design analytics data collection pipeline",
        "Implement metric aggregation logic",
        "Build reporting query engine",
        "Create data export functionality",
    ],

    # --- Integration components ---
    "payment_gateway": [
        "Integrate payment provider API (Stripe/PayPal)",
        "Build checkout flow UI",
        "Handle failed transactions and retries",
        "Implement refund and dispute logic",
    ],
    "video_service": [
        "Set up WebRTC signaling server",
        "Implement video stream handling",
        "Add screen sharing capability",
        "Build recording and playback system",
    ],
    "email_provider": [
        "Configure email service provider",
        "Design email templates",
        "Implement email sending queue",
        "Add delivery tracking and bounce handling",
    ],
    "location_service": [
        "Integrate maps API",
        "Implement geocoding and reverse geocoding",
        "Build location tracking system",
        "Add geofencing capabilities",
    ],

    # --- Data layer ---
    "main_db": [
        "Design database schema and migrations",
        "Set up ORM models and relationships",
        "Implement database seeding scripts",
        "Add indexing and query optimization",
    ],
    "cache": [
        "Set up Redis/cache layer",
        "Implement cache invalidation strategy",
        "Add cache warming for frequently accessed data",
        "Configure cache TTL policies",
    ],
    "media_storage": [
        "Set up file storage service (S3/local)",
        "Implement file upload with size/type validation",
        "Add image resizing and thumbnail generation",
        "Build CDN integration for media delivery",
    ],
    "file_storage": [
        "Configure cloud/local file storage",
        "Implement secure file upload endpoints",
        "Add file versioning support",
        "Build file access permission system",
    ],

    # --- Specialized services ---
    "chat_service": [
        "Design chat message data model",
        "Implement real-time message delivery",
        "Add conversation management (create/archive)",
        "Build message search and history",
    ],
    "websocket_server": [
        "Set up WebSocket server infrastructure",
        "Implement connection management and heartbeat",
        "Build event broadcasting system",
        "Add reconnection and offline message queue",
    ],
    "review_service": [
        "Implement review submission and validation",
        "Build rating aggregation system",
        "Add review moderation pipeline",
        "Create review display components",
    ],
    "recommendation_engine": [
        "Design recommendation algorithm",
        "Build user behavior tracking",
        "Implement collaborative filtering logic",
        "Add A/B testing for recommendation quality",
    ],
    "moderation_service": [
        "Set up content scanning pipeline",
        "Implement automated content filters",
        "Build moderation queue and review UI",
        "Add reporting and appeal system",
    ],
    "order_service": [
        "Design order lifecycle state machine",
        "Implement order creation and validation",
        "Build order tracking and status updates",
        "Add order history and receipts",
    ],
    "product_service": [
        "Design product data model",
        "Implement product CRUD operations",
        "Build product categorization system",
        "Add product image management",
    ],
    "cart_service": [
        "Implement add/remove/update cart items",
        "Build cart persistence (session/database)",
        "Add cart total calculation with taxes",
        "Implement cart expiration and cleanup",
    ],
}

# ────────────────────────────────────────────────────────────────────────────
#  Generic fallback tasks by component type
# ────────────────────────────────────────────────────────────────────────────
GENERIC_TASKS = {
    "frontend": [
        "Design UI mockups and implement layouts",
        "Build interactive components",
        "Add form handling and validation",
        "Implement responsive design",
    ],
    "backend": [
        "Design and implement service logic",
        "Build API endpoints",
        "Add input validation and error handling",
        "Write unit tests",
    ],
    "database": [
        "Design schema and data model",
        "Set up migrations",
        "Add indexing for performance",
        "Implement backup strategy",
    ],
    "integration": [
        "Research and select third-party provider",
        "Implement API integration",
        "Add error handling and retry logic",
        "Build integration tests",
    ],
    "storage": [
        "Configure storage service",
        "Implement upload/download logic",
        "Add access control",
        "Set up backup and retention policies",
    ],
    "cache": [
        "Set up caching layer",
        "Implement cache strategies",
        "Add monitoring and metrics",
        "Configure eviction policies",
    ],
}


async def break_into_tasks(architecture: dict) -> list[dict]:
    """
    Break each architecture component into concrete development tasks.

    Args:
        architecture: The generated architecture with components and connections.

    Returns:
        List of task dicts: [{"name": str, "component": str, "type": str}, ...]
    """
    all_tasks = []

    for component in architecture.get("components", []):
        comp_id = component["id"]
        comp_name = component["name"]
        comp_type = component.get("type", "backend")

        # Try template match first
        tasks = _get_template_tasks(comp_id, comp_type)

        # If no template match, try LLM
        if not tasks:
            try:
                tasks = await _llm_task_breakdown(comp_name, comp_type)
            except Exception as e:
                logger.warning(f"LLM task breakdown failed for {comp_name}: {e}")
                tasks = None

        # Final fallback: generic tasks by type
        if not tasks:
            tasks = GENERIC_TASKS.get(comp_type, GENERIC_TASKS["backend"])

        # Add tasks with component metadata
        for task_name in tasks:
            all_tasks.append({
                "name": task_name,
                "component": comp_name,
                "component_id": comp_id,
                "type": _classify_task_type(task_name, comp_type),
            })

    logger.info(f"Task breakdown: {len(architecture.get('components', []))} components → {len(all_tasks)} tasks")
    return all_tasks


def _get_template_tasks(comp_id: str, comp_type: str) -> list[str] | None:
    """Look up tasks from the template dictionary."""
    # Try exact component ID match
    if comp_id in TASK_TEMPLATES:
        return list(TASK_TEMPLATES[comp_id])

    # Try matching by component type
    if comp_type in TASK_TEMPLATES:
        return list(TASK_TEMPLATES[comp_type])

    # Try substring match on component ID
    for key in TASK_TEMPLATES:
        if key in comp_id or comp_id in key:
            return list(TASK_TEMPLATES[key])

    return None


async def _llm_task_breakdown(comp_name: str, comp_type: str) -> list[str] | None:
    """Use LLM to generate tasks for an unrecognized component."""
    system_prompt = """You are a software project manager. Generate 3-4 concrete development tasks for building a specific software component.
Return ONLY a JSON array of strings. No explanation, no numbering."""

    user_prompt = f"Component: {comp_name} (type: {comp_type})\nGenerate 3-4 specific development tasks for this component."

    response = await call_llm(system_prompt, user_prompt, json_mode=True)
    result = parse_json_response(response)

    if isinstance(result, list) and all(isinstance(t, str) for t in result):
        return result[:4]  # Cap at 4 tasks

    return None


def _classify_task_type(task_name: str, comp_type: str) -> str:
    """Classify a task as UI, integration, backend, setup, or testing."""
    name_lower = task_name.lower()

    if any(kw in name_lower for kw in ["ui", "layout", "design", "responsive", "component", "mockup", "css", "display", "view"]):
        return "ui"
    elif any(kw in name_lower for kw in ["integrate", "api", "provider", "third-party", "webhook", "connect"]):
        return "integration"
    elif any(kw in name_lower for kw in ["test", "testing", "qa", "quality", "verify"]):
        return "testing"
    elif any(kw in name_lower for kw in ["set up", "setup", "configure", "install", "init", "scaffold", "migration", "schema"]):
        return "setup"
    elif comp_type == "frontend":
        return "ui"
    elif comp_type == "integration":
        return "integration"
    else:
        return "backend"
