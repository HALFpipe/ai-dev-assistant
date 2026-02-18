# rag/semantic_search.py
from __future__ import annotations

from typing import List, Tuple

from ai_dev_assistant.infra.vector_store import VectorStore


def search(
    query_vector: List[float],
    k: int = 5,
) -> List[Tuple[str, float]]:
    """
    Core vector retrieval.
    No cost logic. No OpenAI calls except embedding.
    """
    store = VectorStore.load()
    return store.search(query_vector, k=k)
