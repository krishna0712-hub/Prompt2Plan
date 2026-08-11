"""
nlp_extraction.py — Step 1: Extract structured requirements from user's project idea
Uses LLM with strict JSON output. Falls back to rule-based keyword extraction.
"""
import logging
from backend.llm_client import call_llm, parse_json_response

logger = logging.getLogger(__name__)

# Rule-based fallback keywords for when all LLM providers fail
DOMAIN_KEYWORDS = {
    "e-commerce": ["shop", "store", "buy", "sell", "product", "cart", "marketplace", "ecommerce", "e-commerce", "retail"],
    "healthcare": ["health", "medical", "doctor", "patient", "hospital", "clinic", "telemedicine", "pharma"],
    "education": ["learn", "course", "student", "teacher", "school", "university", "education", "training", "tutor"],
    "finance": ["bank", "finance", "payment", "money", "invest", "budget", "fintech", "transaction", "crypto"],
    "social": ["social", "community", "friend", "post", "share", "follow", "network", "forum"],
    "logistics": ["delivery", "shipping", "track", "warehouse", "logistics", "fleet", "transport"],
    "entertainment": ["music", "video", "stream", "game", "play", "media", "content"],
    "real_estate": ["property", "real estate", "house", "apartment", "rent", "listing", "estate"],
    "food": ["food", "restaurant", "recipe", "meal", "order", "delivery", "catering"],
    "travel": ["travel", "hotel", "flight", "booking", "trip", "tour", "vacation"],
    "fitness": ["fitness", "workout", "gym", "exercise", "health", "yoga", "sport"],
    "hr": ["employee", "hr", "human resource", "payroll", "recruitment", "hiring"],
    "iot": ["iot", "sensor", "device", "smart", "connected", "embedded", "hardware"],
}

FEATURE_KEYWORDS = {
    "user_auth": ["login", "signup", "auth", "register", "account", "password", "oauth", "sso"],
    "payments": ["payment", "pay", "checkout", "billing", "stripe", "transaction", "purchase", "buy", "subscription"],
    "chat": ["chat", "message", "messaging", "dm", "conversation", "instant"],
    "notifications": ["notification", "alert", "remind", "push", "email notification"],
    "search": ["search", "filter", "find", "discover", "browse"],
    "reviews": ["review", "rating", "feedback", "testimonial", "star"],
    "admin_dashboard": ["admin", "dashboard", "manage", "backoffice", "control panel"],
    "analytics": ["analytics", "metric", "report", "insight", "statistics", "data visualization"],
    "file_upload": ["upload", "file", "image", "photo", "media", "document", "attachment"],
    "real_time_tracking": ["real-time", "realtime", "live", "tracking", "gps", "location"],
    "video_streaming": ["video", "stream", "live stream", "webrtc", "conference"],
    "shopping_cart": ["cart", "basket", "wishlist", "add to cart"],
    "order_tracking": ["order", "tracking", "shipment", "delivery status", "fulfillment"],
    "appointments": ["appointment", "booking", "schedule", "calendar", "reservation"],
    "social_features": ["follow", "like", "share", "friend", "social", "community", "feed"],
    "recommendations": ["recommend", "suggestion", "personalize", "for you", "discover"],
    "product_listing": ["product", "listing", "catalog", "inventory", "item", "marketplace"],
    "user_profiles": ["profile", "bio", "avatar", "account settings"],
    "collaboration": ["collaborate", "shared", "team", "workspace", "co-edit"],
    "ai_chatbot": ["chatbot", "ai assistant", "virtual assistant", "bot"],
    "content_moderation": ["moderation", "content filter", "spam", "abuse"],
    "multi_language": ["multi-language", "i18n", "translation", "localization", "multilingual"],
}

SCALE_KEYWORDS = {
    "small": ["simple", "basic", "small", "personal", "portfolio", "prototype", "mvp", "minimal"],
    "medium": ["standard", "medium", "startup", "team", "moderate"],
    "large": ["enterprise", "large", "scale", "million", "global", "massive", "complex", "platform"],
}

PROJECT_TYPE_KEYWORDS = {
    "web_app": ["web", "website", "webapp", "web app", "portal", "platform", "site"],
    "mobile_app": ["mobile", "ios", "android", "app", "phone"],
    "api_service": ["api", "backend", "service", "microservice", "server"],
    "desktop_app": ["desktop", "electron", "native", "windows", "mac"],
    "cli_tool": ["cli", "command line", "terminal", "console"],
}


async def extract_requirements(idea_text: str) -> dict:
    """
    Extract structured requirements from a plain-text project idea.

    Returns:
        {
            "project_type": str,
            "features": list[str],
            "scale": str,
            "domain": str
        }
    """
    # Try LLM extraction first
    try:
        result = await _llm_extract(idea_text)
        if result and _validate_extraction(result):
            logger.info("NLP extraction succeeded via LLM")
            return result
    except Exception as e:
        logger.warning(f"LLM extraction failed: {e}")

    # Fall back to rule-based extraction
    logger.info("Using rule-based extraction fallback")
    return _rule_based_extract(idea_text)


async def _llm_extract(idea_text: str) -> dict | None:
    """Use LLM to extract structured requirements."""
    system_prompt = """You are a software requirements analyst. Extract structured requirements from the project idea.
Return ONLY valid JSON in this exact shape:
{"project_type": string, "features": string[], "scale": string, "domain": string}

Rules:
- project_type: one of "web_app", "mobile_app", "api_service", "desktop_app", "cli_tool"
- features: array of feature keywords like "user_auth", "payments", "chat", "search", "notifications", "reviews", "admin_dashboard", "analytics", "file_upload", "real_time_tracking", "video_streaming", "shopping_cart", "order_tracking", "appointments", "social_features", "recommendations", "product_listing", "user_profiles", "collaboration", "ai_chatbot", "content_moderation", "multi_language"
- scale: one of "small", "medium", "large"
- domain: the primary business domain (e.g., "e-commerce", "healthcare", "education", "finance")"""

    response = await call_llm(system_prompt, idea_text, json_mode=True)
    return parse_json_response(response)


def _rule_based_extract(idea_text: str) -> dict:
    """Rule-based fallback extraction using keyword matching."""
    text_lower = idea_text.lower()

    # Detect domain
    domain = "general"
    best_domain_score = 0
    for d, keywords in DOMAIN_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > best_domain_score:
            best_domain_score = score
            domain = d

    # Detect features
    features = []
    for feature, keywords in FEATURE_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            features.append(feature)

    # Always include auth if not explicitly detected (most apps need it)
    if not features:
        features = ["user_auth"]
    elif "user_auth" not in features:
        features.append("user_auth")

    # Detect scale
    scale = "medium"  # default
    best_scale_score = 0
    for s, keywords in SCALE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > best_scale_score:
            best_scale_score = score
            scale = s

    # Detect project type
    project_type = "web_app"  # default
    best_type_score = 0
    for pt, keywords in PROJECT_TYPE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > best_type_score:
            best_type_score = score
            project_type = pt

    return {
        "project_type": project_type,
        "features": features,
        "scale": scale,
        "domain": domain,
    }


def _validate_extraction(result: dict) -> bool:
    """Validate that the extraction result has the expected shape."""
    required_keys = {"project_type", "features", "scale", "domain"}
    if not isinstance(result, dict):
        return False
    if not required_keys.issubset(result.keys()):
        return False
    if not isinstance(result.get("features"), list):
        return False
    if len(result["features"]) == 0:
        return False
    return True
