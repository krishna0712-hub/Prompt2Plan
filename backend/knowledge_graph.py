"""
knowledge_graph.py — Step 3: Look up component dependencies from kg.json
Uses fuzzy substring/synonym matching to map extracted features to required components.
"""
import os
import json
import logging

logger = logging.getLogger(__name__)

# Module-level state
_kg_data: dict = {}


def initialize_kg():
    """Load the knowledge graph from kg.json at startup."""
    global _kg_data

    data_path = os.path.join(os.path.dirname(__file__), "data", "kg.json")
    with open(data_path, "r", encoding="utf-8") as f:
        _kg_data = json.load(f)

    logger.info(f"Knowledge graph loaded with {len(_kg_data)} feature entries")


def lookup_components(features: list[str]) -> dict:
    """
    Look up required components and dependencies for the given features.
    Uses fuzzy substring + synonym matching.

    Args:
        features: List of feature keywords (e.g., ["payments", "chat", "user_auth"])

    Returns:
        {
            "components": [{"id": str, "name": str, "type": str}, ...],
            "dependencies": [{"from": str, "to": str, "label": str}, ...]
        }
    """
    if not _kg_data:
        initialize_kg()
    if not _kg_data:
        logger.warning("Knowledge graph not loaded — returning empty results")
        return {"components": [], "dependencies": []}

    all_components = {}  # id -> component dict (deduplicated)
    all_dependencies = []  # list of dependency edges
    seen_deps = set()  # for dedup

    for feature in features:
        matched_key = _fuzzy_match(feature)
        if matched_key is None:
            logger.debug(f"No KG match for feature: {feature}")
            continue

        entry = _kg_data[matched_key]
        logger.debug(f"Feature '{feature}' matched KG key '{matched_key}'")

        # Collect components (deduplicate by id)
        for comp in entry.get("components", []):
            comp_id = comp["id"]
            if comp_id not in all_components:
                all_components[comp_id] = comp

        # Collect dependencies (deduplicate by from+to)
        for dep in entry.get("dependencies", []):
            dep_key = (dep["from"], dep["to"])
            if dep_key not in seen_deps:
                seen_deps.add(dep_key)
                all_dependencies.append(dep)

    result = {
        "components": list(all_components.values()),
        "dependencies": all_dependencies,
    }

    logger.info(
        f"KG lookup: {len(features)} features → "
        f"{len(result['components'])} components, "
        f"{len(result['dependencies'])} dependencies"
    )

    return result


def _fuzzy_match(feature: str) -> str | None:
    """
    Find the best matching key in the knowledge graph for a given feature string.
    Uses exact match first, then synonym matching, then substring matching.
    """
    feature_lower = feature.lower().strip()

    # 1. Exact key match
    if feature_lower in _kg_data:
        return feature_lower

    # 2. Check synonyms in each KG entry
    for key, entry in _kg_data.items():
        synonyms = entry.get("synonyms", [])
        if feature_lower in synonyms:
            return key
        # Also check if any synonym is a substring of the feature or vice versa
        for syn in synonyms:
            if syn in feature_lower or feature_lower in syn:
                return key

    # 3. Substring match on key names
    for key in _kg_data:
        if key in feature_lower or feature_lower in key:
            return key

    # 4. Partial word overlap
    feature_words = set(feature_lower.replace("_", " ").replace("-", " ").split())
    best_key = None
    best_overlap = 0
    for key in _kg_data:
        key_words = set(key.replace("_", " ").replace("-", " ").split())
        overlap = len(feature_words & key_words)
        if overlap > best_overlap:
            best_overlap = overlap
            best_key = key

    if best_overlap > 0:
        return best_key

    return None
