"""
services/embedding_service.py

Builds a per-request FAISS index from document chunks and retrieves
the top-k most relevant chunks for a given query.

pip install faiss-cpu sentence-transformers
"""

import numpy as np

import faiss
from sentence_transformers import SentenceTransformer

# Load the embedding model once at module level (cached across requests)
_MODEL_NAME = "all-MiniLM-L6-v2"   # fast, lightweight, good quality
_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(_MODEL_NAME)
    return _model


class EmbeddingService:
    """
    Ephemeral FAISS index built from a list of text chunks.
    Create a new instance per request — no shared mutable state.
    """

    def __init__(self, chunks: list[str]) -> None:
        """
        Build the FAISS flat-L2 index from *chunks*.

        Parameters
        ----------
        chunks : list[str]
            Non-empty text chunks from DocumentService.
        """
        if not chunks:
            raise ValueError("Cannot build an index from an empty chunk list.")

        self._chunks = chunks
        model        = _get_model()

        # Encode all chunks → (N, D) float32 array
        embeddings: np.ndarray = model.encode(
            chunks,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=True,   # cosine via inner-product on unit vecs
        ).astype("float32")

        dim         = embeddings.shape[1]
        self._index = faiss.IndexFlatIP(dim)   # inner-product = cosine for normalised vecs
        self._index.add(embeddings)

    # ── Public API ────────────────────────────────────────────────────────────

    def search(self, query: str, k: int = 5) -> list[str]:
        """
        Return the top-*k* chunks most semantically similar to *query*.

        Parameters
        ----------
        query : str   The user's question.
        k     : int   Number of chunks to retrieve (default 5).

        Returns
        -------
        list[str]  Ordered list of relevant chunks (best match first).
        """
        k = min(k, len(self._chunks))   # can't retrieve more than we have

        model     = _get_model()
        query_emb = model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).astype("float32")

        _, indices = self._index.search(query_emb, k)

        return [self._chunks[i] for i in indices[0] if i < len(self._chunks)]