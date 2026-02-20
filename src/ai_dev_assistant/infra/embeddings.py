# infra/embeddings.py
from __future__ import annotations

from typing import List

from ai_dev_assistant.infra.ai_client import get_ai_client

from .config import EMBEDDING_MODEL


def embed_texts(
    texts: List[str],
    model: str,
    batch_size: int = 64,
) -> List[List[float]]:
    """
    Low-level embedding call.

    - No domain logic
    - No cost estimation
    - No printing
    - No DRY_RUN
    """
    client = get_ai_client()

    if client is None:
        raise RuntimeError("Embedding requested in dry-run mode.\nThis should have been skipped earlier.")

    vectors: List[List[float]] = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = client.embeddings.create(
            model=model,
            input=batch,
        )
        vectors.extend(item.embedding for item in response.data)

    return vectors


def embed_query(
    query: str,
    model: str = EMBEDDING_MODEL,
) -> List[float]:
    client = get_ai_client()

    response = client.embeddings.create(
        model=model,
        input=query,
    )

    return response.data[0].embedding
