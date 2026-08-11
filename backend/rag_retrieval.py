"""
rag_retrieval.py — Step 2: FAISS similarity search over seed templates
Embeds seed template descriptions with sentence-transformers (all-MiniLM-L6-v2),
builds a FAISS index in memory, and retrieves top-k similar architectures.
"""
import os
import json
import logging
import numpy as np

logger = logging.getLogger(__name__)

# Module-level state — initialized once at startup
_faiss_index = None
_seed_templates = []
_model = None


def initialize_rag():
    """
    Load seed templates, embed them, and build the FAISS index.
    Called once at application startup.
    """
    global _faiss_index, _seed_templates, _model

    # Load seed templates
    data_path = os.path.join(os.path.dirname(__file__), "data", "seed_templates.json")
    with open(data_path, "r", encoding="utf-8") as f:
        _seed_templates = json.load(f)

    logger.info(f"Loaded {len(_seed_templates)} seed templates")

    # Load the sentence-transformer model
    try:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("Sentence-transformer model loaded (all-MiniLM-L6-v2)")
    except Exception as e:
        logger.error(f"Failed to load sentence-transformer model: {e}")
        logger.warning("RAG retrieval will return random templates as fallback")
        _model = None
        return

    # Embed all template descriptions
    descriptions = [t["description"] for t in _seed_templates]
    embeddings = _model.encode(descriptions, convert_to_numpy=True, show_progress_bar=False)

    # Build FAISS index
    try:
        import faiss

        dimension = embeddings.shape[1]
        _faiss_index = faiss.IndexFlatL2(dimension)
        _faiss_index.add(embeddings.astype(np.float32))
        logger.info(f"FAISS index built with {_faiss_index.ntotal} vectors (dim={dimension})")
    except Exception as e:
        logger.error(f"Failed to build FAISS index: {e}")
        _faiss_index = None


def retrieve_similar(features: list[str], top_k: int = 3) -> list[dict]:
    """
    Find the top-k most similar seed templates to the given features.

    Args:
        features: List of feature keywords extracted from the user's idea.
        top_k: Number of similar templates to return.

    Returns:
        List of architecture dicts from the most similar seed templates.
    """
    if not _seed_templates:
        initialize_rag()
    if not _seed_templates:
        logger.warning("No seed templates loaded — returning empty results")
        return []

    # If FAISS or model not available, return random templates as fallback
    if _faiss_index is None or _model is None:
        logger.warning("FAISS/model not available — returning first {top_k} templates")
        return [t["architecture"] for t in _seed_templates[:top_k]]

    # Embed the query (join features into a descriptive string)
    query_text = ", ".join(features)
    query_embedding = _model.encode([query_text], convert_to_numpy=True).astype(np.float32)

    # Search FAISS
    k = min(top_k, len(_seed_templates))
    distances, indices = _faiss_index.search(query_embedding, k)

    results = []
    for idx in indices[0]:
        if 0 <= idx < len(_seed_templates):
            template = _seed_templates[idx]
            results.append({
                "id": template["id"],
                "description": template["description"],
                "architecture": template["architecture"],
            })

    logger.info(f"RAG retrieved {len(results)} similar templates for features: {features}")
    return results
