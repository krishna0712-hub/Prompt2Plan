"""
rag_retrieval.py — Step 2: FAISS similarity search over seed templates.

Memory-optimized implementation:
- Uses shared singleton EmbeddingManager (lazy loaded).
- Reuses precomputed template embeddings (seed_templates_embeddings.npy) to avoid startup re-embedding.
- Preserves exact FAISS vector similarity search and top-k retrieval quality.
- Thread-safe lazy initialization.
- In-memory LRU query cache to eliminate duplicate neural forward passes.
"""
import os
import gc
import json
import logging
import threading
from typing import List, Dict, Any, Optional
import numpy as np

from backend.embedding_manager import get_embedding_manager

logger = logging.getLogger(__name__)

# Module-level state — lazily initialized
_faiss_index = None
_seed_templates: List[Dict[str, Any]] = []
_rag_lock = threading.Lock()
_query_cache: Dict[str, List[Dict[str, Any]]] = {}
_cache_lock = threading.Lock()
MAX_RAG_CACHE = 128


def initialize_rag(force_recompute: bool = False):
    """
    Load seed templates, retrieve/compute embeddings, and build the FAISS index.
    Thread-safe and lazy: can be called at startup or on first request.
    """
    global _faiss_index, _seed_templates

    with _rag_lock:
        if _faiss_index is not None and _seed_templates and not force_recompute:
            return

        # 1. Load seed templates JSON
        data_path = os.path.join(os.path.dirname(__file__), "data", "seed_templates.json")
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                _seed_templates = json.load(f)
            logger.info(f"Loaded {len(_seed_templates)} seed templates")
        except Exception as e:
            logger.error(f"Failed to load seed templates from {data_path}: {e}")
            _seed_templates = []
            _faiss_index = None
            return

        # 2. Check for precomputed embeddings to avoid loading embedding model into memory at startup
        npy_path = os.path.join(os.path.dirname(__file__), "data", "seed_templates_embeddings.npy")
        embeddings = None

        if os.path.exists(npy_path) and not force_recompute:
            try:
                embeddings = np.load(npy_path).astype(np.float32)
                if len(embeddings) != len(_seed_templates):
                    logger.warning("Precomputed embeddings count mismatch with templates. Recomputing...")
                    embeddings = None
                else:
                    logger.info(f"Loaded precomputed seed template embeddings from {npy_path} (shape: {embeddings.shape})")
            except Exception as e:
                logger.warning(f"Failed to read precomputed embeddings: {e}. Falling back to dynamic embedding.")
                embeddings = None

        # 3. Generate embeddings with shared model if not loaded from precomputed cache
        if embeddings is None:
            try:
                em = get_embedding_manager()
                descriptions = [t["description"] for t in _seed_templates]
                embeddings = em.encode(descriptions, show_progress_bar=False).astype(np.float32)
                # Persist to disk for future zero-cost startups
                try:
                    np.save(npy_path, embeddings)
                    logger.info(f"Saved precomputed seed template embeddings to {npy_path}")
                except Exception as save_err:
                    logger.warning(f"Could not cache embeddings to disk: {save_err}")
            except Exception as e:
                logger.error(f"Failed to compute seed template embeddings: {e}")
                _faiss_index = None
                return

        # 4. Build FAISS index
        try:
            import faiss

            dimension = embeddings.shape[1]
            # Use IndexFlatL2 for exact Euclidean distance matching (same as baseline)
            index = faiss.IndexFlatL2(dimension)
            index.add(embeddings.astype(np.float32))
            _faiss_index = index
            logger.info(f"FAISS index built with {_faiss_index.ntotal} vectors (dim={dimension})")
        except Exception as e:
            logger.error(f"Failed to build FAISS index: {e}")
            _faiss_index = None

        gc.collect()


def retrieve_similar(features: List[str], top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Find the top-k most similar seed templates to the given features.
    Preserves exact semantic search relevance and ranking behavior.

    Args:
        features: List of feature keywords extracted from the user's idea.
        top_k: Number of similar templates to return (default: 3).

    Returns:
        List of architecture dicts from the most similar seed templates.
    """
    if not features:
        return []

    # Check in-memory query cache for instant retrieval without re-encoding
    cache_key = f"{','.join(sorted(features))}_{top_k}"
    with _cache_lock:
        if cache_key in _query_cache:
            return _query_cache[cache_key]

    if not _seed_templates or _faiss_index is None:
        initialize_rag()

    if not _seed_templates:
        logger.warning("No seed templates loaded — returning empty results")
        return []

    # If FAISS not available, return first top_k templates as fallback
    if _faiss_index is None:
        logger.warning(f"FAISS index unavailable — returning first {top_k} templates")
        fallback = [
            {
                "id": t["id"],
                "description": t["description"],
                "architecture": t["architecture"],
            }
            for t in _seed_templates[:top_k]
        ]
        return fallback

    # Embed the query with shared EmbeddingManager
    query_text = ", ".join(features)
    em = get_embedding_manager()
    query_vec = em.encode(query_text).reshape(1, -1).astype(np.float32)

    # Search FAISS
    k = min(top_k, len(_seed_templates))
    distances, indices = _faiss_index.search(query_vec, k)

    results = []
    for idx in indices[0]:
        if 0 <= idx < len(_seed_templates):
            template = _seed_templates[idx]
            results.append({
                "id": template["id"],
                "description": template["description"],
                "architecture": template["architecture"],
            })

    # Cache result
    with _cache_lock:
        if len(_query_cache) >= MAX_RAG_CACHE:
            _query_cache.pop(next(iter(_query_cache)))
        _query_cache[cache_key] = results

    logger.info(f"RAG retrieved {len(results)} similar templates for features: {features}")
    return results
