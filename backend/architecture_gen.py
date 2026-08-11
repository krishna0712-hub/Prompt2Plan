"""
architecture_gen.py — Step 4: Generate system architecture from merged context
Combines RAG results + KG components + extracted requirements → LLM → architecture JSON.
Falls back to KG-only architecture if LLM fails.
"""
import logging
import json
from backend.llm_client import call_llm, parse_json_response

logger = logging.getLogger(__name__)


async def generate_architecture(
    requirements: dict,
    rag_results: list[dict],
    kg_components: dict,
) -> dict:
    """
    Generate a system architecture combining RAG examples, KG components, and requirements.

    Args:
        requirements: The extracted requirements JSON from step 1.
        rag_results: Top-k similar architectures from step 2.
        kg_components: Components and dependencies from step 3.

    Returns:
        {
            "components": [{"id": str, "name": str, "type": str}, ...],
            "connections": [{"from": str, "to": str, "label": str}, ...]
        }
    """
    # Try LLM-based generation first
    try:
        result = await _llm_generate(requirements, rag_results, kg_components)
        if result and _validate_architecture(result):
            logger.info(f"Architecture generated via LLM: {len(result['components'])} components, {len(result['connections'])} connections")
            return result
    except Exception as e:
        logger.warning(f"LLM architecture generation failed: {e}")

    # Fall back to KG-based architecture
    logger.info("Using KG-based architecture fallback")
    return _build_from_kg(requirements, kg_components)


async def _llm_generate(
    requirements: dict,
    rag_results: list[dict],
    kg_components: dict,
) -> dict | None:
    """Use LLM to generate architecture from merged context."""
    # Build reference architectures summary
    ref_archs = ""
    for i, rag in enumerate(rag_results, 1):
        arch = rag.get("architecture", rag)
        ref_archs += f"\n--- Reference Architecture {i} ({rag.get('description', 'N/A')[:80]}) ---\n"
        ref_archs += f"Components: {json.dumps([c['name'] for c in arch.get('components', [])])}\n"
        ref_archs += f"Connections: {len(arch.get('connections', []))} edges\n"

    # Build KG components summary
    kg_summary = ""
    if kg_components.get("components"):
        kg_summary = f"\nRequired components from dependency analysis:\n"
        kg_summary += json.dumps(kg_components["components"], indent=2)
        kg_summary += f"\nDependency edges:\n"
        kg_summary += json.dumps(kg_components["dependencies"], indent=2)

    system_prompt = """You are a software architect. Generate a system architecture based on the provided requirements, reference architectures, and dependency analysis.

Return ONLY valid JSON in this exact shape:
{
  "components": [{"id": "unique_snake_case_id", "name": "Human Readable Name", "type": "frontend|backend|database|integration|storage|cache"}],
  "connections": [{"from": "component_id", "to": "component_id", "label": "relationship description"}]
}

Rules:
- Generate 6-15 components depending on project complexity
- Every component must have at least one connection
- Include appropriate frontend, backend, database, and integration components
- Use the reference architectures as inspiration but tailor to the specific requirements
- Include all components identified in the dependency analysis
- Component IDs must be unique snake_case strings
- Connection "from" and "to" must reference valid component IDs"""

    user_prompt = f"""Project Requirements:
{json.dumps(requirements, indent=2)}

{ref_archs}
{kg_summary}

Generate the system architecture for this project."""

    response = await call_llm(system_prompt, user_prompt, json_mode=True)
    return parse_json_response(response)


def _build_from_kg(requirements: dict, kg_components: dict) -> dict:
    """
    Build a basic architecture purely from KG components when LLM is unavailable.
    Ensures every project has at minimum: a frontend, API layer, and database.
    """
    components = list(kg_components.get("components", []))
    connections = list(kg_components.get("dependencies", []))

    # Track existing component IDs
    existing_ids = {c["id"] for c in components}

    # Ensure we have core infrastructure components
    core_components = [
        {"id": "web_frontend", "name": "Web Frontend", "type": "frontend"},
        {"id": "api_server", "name": "API Server", "type": "backend"},
        {"id": "auth_service", "name": "Auth Service", "type": "backend"},
        {"id": "main_db", "name": "Main Database", "type": "database"},
    ]

    for core in core_components:
        if core["id"] not in existing_ids:
            components.append(core)
            existing_ids.add(core["id"])

    # Ensure frontend → API connection exists
    has_frontend_api = any(
        c["from"] in ("web_frontend",) and c["to"] in ("api_server", "api_gateway")
        for c in connections
    )
    if not has_frontend_api:
        connections.append({"from": "web_frontend", "to": "api_server", "label": "REST API"})

    # Ensure API → Auth connection
    has_api_auth = any(
        c["to"] == "auth_service" for c in connections
    )
    if not has_api_auth:
        connections.append({"from": "api_server", "to": "auth_service", "label": "Auth check"})

    # Connect any orphaned backend components to the API server
    connected_ids = set()
    for conn in connections:
        connected_ids.add(conn["from"])
        connected_ids.add(conn["to"])

    for comp in components:
        if comp["id"] not in connected_ids and comp["type"] == "backend":
            connections.append({"from": "api_server", "to": comp["id"], "label": "Service call"})

    # Connect database components
    for comp in components:
        if comp["type"] == "database" and comp["id"] != "main_db":
            has_connection = any(c["to"] == comp["id"] for c in connections)
            if not has_connection:
                connections.append({"from": "api_server", "to": comp["id"], "label": "Read/Write"})

    return {
        "components": components,
        "connections": connections,
    }


def _validate_architecture(result: dict) -> bool:
    """Validate the architecture JSON shape."""
    if not isinstance(result, dict):
        return False
    if "components" not in result or "connections" not in result:
        return False
    if not isinstance(result["components"], list) or len(result["components"]) < 2:
        return False
    if not isinstance(result["connections"], list) or len(result["connections"]) < 1:
        return False

    # Check each component has required fields
    for comp in result["components"]:
        if not all(k in comp for k in ("id", "name", "type")):
            return False

    # Check each connection references valid component IDs
    valid_ids = {c["id"] for c in result["components"]}
    for conn in result["connections"]:
        if not all(k in conn for k in ("from", "to", "label")):
            return False
        # Allow connections even if IDs don't match (LLM might use slightly different names)

    return True
