# services/inspect_repo.py
"""
services.search

Semantic search API.

This module is responsible for **semantic retrieval only**:
- embeds a user query
- searches the FAISS vector index
- returns the most relevant chunk IDs with similarity scores

It does NOT:
- build prompt context
- expand full code
- call the LLM

Rule:
"inspect_repo.py answers: which parts of the codebase are relevant?"
"""

from typing import Dict

from ai_dev_assistant.infra.config import is_dry_run, EMBEDDING_MODEL
from ai_dev_assistant.infra.embeddings import embed_query
from ai_dev_assistant.rag.cost import estimate_embedding_cost
from ai_dev_assistant.rag.semantic_search import search


def search_query(
    query: str,
    k: int = 5,
    model: str = EMBEDDING_MODEL,
) -> Dict:
    """
    Perform semantic search over the embedded codebase.

    Input:
    - query: natural language question
    - k: number of top chunks to retrieve
    - model: embedding model

    Output (dict):
    {
        "query": str,
        "chunks": [
            {"chunk_id": str, "score": float},
            ...
        ],
        "dry_run": bool,
        "cost": {
            "embedding_tokens": int,
            "estimated_cost": float
        }
    }

    Notes:
    - Safe to call frequently
    - Cheap compared to LLM calls
    - Deterministic for a given index
    """
    tokens, cost = estimate_embedding_cost([query], model)

    if is_dry_run():
        return {
            "query": query,
            "chunks": [],
            "dry_run": True,
            "cost": {
                "embedding_tokens": tokens,
                "estimated_cost": cost,
            },
        }

    vector = embed_query(query, model=model)
    results = search(vector, k=k)

    return {
        "query": query,
        "chunks": [{"chunk_id": cid, "score": score} for cid, score in results],
        "dry_run": False,
        "cost": {
            "embedding_tokens": tokens,
            "estimated_cost": cost,
        },
    }
