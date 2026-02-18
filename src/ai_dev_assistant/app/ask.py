# services/ask.py
"""
services.ask

High-level orchestration API.

This module coordinates the full RAG pipeline:
1. semantic search
2. context assembly
3. LLM explanation

It exists for convenience and UI simplicity.

It does NOT:
- contain business logic
- know embedding details
- know LLM internals

Rule:
"ask.py answers: give me the final answer."
"""


# services/ask.py
from __future__ import annotations
from typing import Dict

from ai_dev_assistant.rag.config import DEFAULT_MODE
from ai_dev_assistant.rag.modes import ConversationMode, get_mode_policy
from ai_dev_assistant.services.search import search_query
from ai_dev_assistant.services.explain import explain_query
from ai_dev_assistant.rag.context import build_context, ContextOptions


def ask(
    query: str,
    k: int = 5,
    mode: str | None = None,
    *,
    memory: str | None = None,   # NEW
) -> Dict:
    """
    High-level API entrypoint.
    Execute the full RAG pipeline for a user query.

    This function is memory-agnostic by default.
    Conversation memory (if any) must be injected explicitly
    by higher-level orchestration (e.g. app.ask_with_memory).

    Pipeline:
    - search_query → retrieve relevant chunks
    - build_query_context → assemble LLM context
    - explain_query → generate explanation
    according to the selected conversation mode.

    Output (dict):
    {
        "query": str,
        "search": {...},
        "context": {...} | None,
        "answer": {...} | None,
        "dry_run": bool
    }

    Notes:
    - Best entry point for GUI / API consumers
    - Internally composed of smaller API units

    """

    # ----------------------------
    # Resolve mode
    # ----------------------------
    try:
        resolved_mode = ConversationMode(mode) if mode else DEFAULT_MODE
    except ValueError:
        raise ValueError(f"Unknown conversation mode: {mode}")

    policy = get_mode_policy(resolved_mode)

    # ----------------------------
    # Retrieval (optional)
    # ----------------------------
    if policy.use_retrieval:
        retrieval = search_query(query, k=k)
    else:
        retrieval = {
            "query": query,
            "results": [],
            "dry_run": False,
            "cost": None,
        }

    if retrieval.get("dry_run"):
        return {
            "query": query,
            "mode": resolved_mode.value,
            "retrieval": retrieval,
            "context": None,
            "explanation": None,
            "dry_run": True,
        }

    # ----------------------------
    # Context construction
    # ----------------------------
    options = ContextOptions(
        prefer_full_code=policy.prefer_full_code,
        expand_inheritance_depth=policy.expand_inheritance_depth,
        inject_project_overview=policy.inject_project_overview,
    )
    chunks = retrieval.get("chunks", [])

    assert isinstance(chunks, list), f"Invalid chunks type: {type(chunks)}"

    results = [(r["chunk_id"], r["score"]) for r in chunks]
    context = build_context(results, options)


    # ----------------------------
    # Explanation (optional)
    # ----------------------------
    explanation = (
        explain_query(
            query=query,
            context=context,
            mode=resolved_mode,     # NEW (mode, not directive)
            memory=memory,          # NEW
        )
        if policy.use_llm
        else None
    )

    return {
        "query": query,
        "mode": resolved_mode.value,
        "policy": {
            "use_retrieval": policy.use_retrieval,
            "use_llm": policy.use_llm,
            "prefer_full_code": policy.prefer_full_code,
            "expand_inheritance_depth": policy.expand_inheritance_depth,
            "inject_project_overview": policy.inject_project_overview,
        },
        "retrieval": retrieval,
        "context": context,
        "explanation": explanation,
        "dry_run": False,
    }
