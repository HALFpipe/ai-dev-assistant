# rag/vector_store.py
from __future__ import annotations

import json
from typing import Iterable, List, Tuple

import faiss
import numpy as np

from ai_dev_assistant.tools.defaults import get_faiss_index_path, get_faiss_meta_path


# ============================================================
# VECTOR STORE
# ============================================================


class VectorStore:
    """
    FAISS-backed vector store for semantic search.
    """

    def __init__(self, dim: int):
        # Inner product index (use normalized vectors = cosine similarity)
        self.index = faiss.IndexFlatIP(dim)
        self.ids: list[str] = []

    # --------------------------------------------------
    # BUILD
    # --------------------------------------------------

    def build(self, records: Iterable[dict]) -> None:
        """
        Build FAISS index from embedding records.

        Each record must contain:
        - id: str
        - embedding: List[float]
        """

        vectors: list[list[float]] = []
        ids: list[str] = []

        for record in records:
            vectors.append(record["embedding"])
            ids.append(record["id"])

        if not vectors:
            raise ValueError("No vectors provided to build FAISS index")

        matrix = np.array(vectors, dtype="float32")

        # Normalize for cosine similarity
        faiss.normalize_L2(matrix)

        self.index.add(matrix)
        self.ids = ids

    # --------------------------------------------------
    # SAVE / LOAD
    # --------------------------------------------------

    def save(self) -> None:
        get_faiss_index_path().parent.mkdir(parents=True, exist_ok=True)

        faiss.write_index(self.index, str(get_faiss_index_path()))
        get_faiss_meta_path().write_text(
            json.dumps(
                {
                    "ids": self.ids,
                    "dim": self.index.d,
                },
                indent=2,
            )
        )

    @classmethod
    def load(cls) -> "VectorStore":
        if not get_faiss_index_path().exists() or not get_faiss_meta_path().exists():
            raise FileNotFoundError("FAISS index or metadata not found")

        meta = json.loads(get_faiss_meta_path().read_text())
        store = cls(dim=meta["dim"])
        store.index = faiss.read_index(str(get_faiss_index_path()))
        store.ids = meta["ids"]

        return store

    # --------------------------------------------------
    # SEARCH
    # --------------------------------------------------

    def search(
        self,
        query_vector: List[float],
        k: int = 5,
    ) -> List[Tuple[str, float]]:
        """
        Search for nearest neighbors.

        Returns:
        [(chunk_id, score), ...]
        """

        vector = np.array([query_vector], dtype="float32")
        faiss.normalize_L2(vector)

        scores, indices = self.index.search(vector, k)

        results: list[Tuple[str, float]] = []

        for idx, score in zip(indices[0], scores[0], strict=True):
            if idx < 0:
                continue
            results.append((self.ids[idx], float(score)))

        return results
