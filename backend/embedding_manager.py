"""
embedding_manager.py — Thread-safe, lazy-loaded singleton embedding model manager.

Provides:
1. Thread-safe singleton SentenceTransformer instance ("all-MiniLM-L6-v2").
2. Lazy initialization: model is loaded only when first embedding is requested.
3. PyTorch memory optimizations (single thread, gradients disabled).
4. In-memory LRU query/text embedding cache to prevent redundant neural forward passes.
5. Batch encoding support for efficient task evaluation.
6. Shared across RAG retrieval and AI effort estimation to prevent duplicate models in RAM.
"""
import os
import gc
import logging
import threading
from typing import List, Union, Optional
from collections import OrderedDict
import numpy as np

logger = logging.getLogger(__name__)

# Model configuration
DEFAULT_MODEL_NAME = "all-MiniLM-L6-v2"
MAX_CACHE_SIZE = 256


class EmbeddingManager:
    """Singleton manager for shared, lazy-loaded SentenceTransformer embedding model."""

    _instance: Optional["EmbeddingManager"] = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(EmbeddingManager, cls).__new__(cls)
                    cls._instance._init_manager()
        return cls._instance

    def _init_manager(self):
        """Internal initialization of manager state."""
        self._model = None
        self._model_lock = threading.Lock()
        self._cache = OrderedDict()
        self._cache_lock = threading.Lock()
        self._model_name = DEFAULT_MODEL_NAME
        self._hits = 0
        self._misses = 0

    def is_initialized(self) -> bool:
        """Check if model is currently loaded in memory."""
        return self._model is not None

    def get_model(self):
        """
        Lazily initialize and return the shared SentenceTransformer instance.
        Thread-safe: prevents duplicate model loading under concurrent requests.
        """
        if self._model is not None:
            return self._model

        with self._model_lock:
            if self._model is not None:
                return self._model

            logger.info(f"Loading shared embedding model ({self._model_name}) into memory...")
            try:
                # Configure thread environment variables before PyTorch loads native OpenMP/MKL thread pools
                for var in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS", "TORCH_NUM_THREADS"):
                    os.environ.setdefault(var, "1")

                # Configure PyTorch for minimal memory footprint before loading model
                import torch
                torch.set_num_threads(1)
                try:
                    torch.set_num_interop_threads(1)
                except Exception:
                    pass
                torch.set_grad_enabled(False)
            except Exception as e:
                logger.warning(f"Could not configure PyTorch thread/grad settings: {e}")

            try:
                from sentence_transformers import SentenceTransformer

                # Try loading from local cache first to avoid slow Hub network checks / timeouts
                try:
                    model = SentenceTransformer(self._model_name, local_files_only=True)
                except Exception as local_err:
                    logger.info(f"Local model load deferred to remote: {local_err}")
                    model = SentenceTransformer(self._model_name)

                # Set evaluation mode
                model.eval()
                self._model = model
                logger.info(f"✓ Shared embedding model ({self._model_name}) loaded successfully.")
                gc.collect()
                return self._model

            except Exception as e:
                logger.error(f"Failed to load shared embedding model: {e}", exc_info=True)
                self._model = None
                raise e

    def encode(
        self,
        texts: Union[str, List[str]],
        normalize: bool = False,
        show_progress_bar: bool = False,
    ) -> np.ndarray:
        """
        Encode text or list of texts into embeddings using the shared model with LRU caching.

        Args:
            texts: Single text string or list of text strings.
            normalize: If True, L2-normalizes the vectors.
            show_progress_bar: Show tqdm progress bar if True.

        Returns:
            np.ndarray of shape (N, dim) or (dim,) of type float32.
        """
        is_single = isinstance(texts, str)
        text_list = [texts] if is_single else list(texts)

        if not text_list:
            return np.empty((0, 384), dtype=np.float32)

        # Check cache for each text
        results: List[Optional[np.ndarray]] = [None] * len(text_list)
        missing_indices = []
        missing_texts = []

        with self._cache_lock:
            for i, t in enumerate(text_list):
                cache_key = (t.strip(), normalize)
                if cache_key in self._cache:
                    self._cache.move_to_end(cache_key)
                    results[i] = self._cache[cache_key].copy()
                    self._hits += 1
                else:
                    missing_indices.append(i)
                    missing_texts.append(t)
                    self._misses += 1

        # Compute embeddings for missing items using shared model
        if missing_texts:
            model = self.get_model()
            with self._model_lock:
                computed_embeddings = model.encode(
                    missing_texts,
                    convert_to_numpy=True,
                    normalize_embeddings=normalize,
                    show_progress_bar=show_progress_bar,
                ).astype(np.float32)

            with self._cache_lock:
                for idx, t, emb in zip(missing_indices, missing_texts, computed_embeddings):
                    cache_key = (t.strip(), normalize)
                    self._cache[cache_key] = emb
                    if len(self._cache) > MAX_CACHE_SIZE:
                        self._cache.popitem(last=False)
                    results[idx] = emb

        output_array = np.array(results, dtype=np.float32)
        return output_array[0] if is_single else output_array

    def get_stats(self) -> dict:
        """Return cache and model usage stats."""
        return {
            "model_loaded": self._model is not None,
            "cache_size": len(self._cache),
            "cache_hits": self._hits,
            "cache_misses": self._misses,
            "hit_ratio": round(self._hits / max(1, self._hits + self._misses), 3),
        }

    def clear_cache(self):
        """Clear LRU cache to free RAM if needed."""
        with self._cache_lock:
            self._cache.clear()
        gc.collect()


# Module-level convenience singleton getter
_manager_instance: Optional[EmbeddingManager] = None


def get_embedding_manager() -> EmbeddingManager:
    """Retrieve the global EmbeddingManager singleton instance."""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = EmbeddingManager()
    return _manager_instance


def get_embedding_model():
    """Retrieve the shared SentenceTransformer model instance (lazy loaded)."""
    return get_embedding_manager().get_model()
