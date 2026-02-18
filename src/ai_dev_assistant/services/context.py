# services/context.py
"""
services.context

Context assembly API.

This module transforms retrieved chunk IDs into a **LLM-ready context**:
- expands overview → full code
- injects project overview when appropriate
- deduplicates overlapping content
- produces a single structured text block

It does NOT:
- embed queries
- search vectors
- call the LLM

Rule:
"context.py answers: what exactly should the LLM see?"
"""

from typing import Dict, List

from ai_dev_assistant.rag.context import ContextOptions, build_context
from ai_dev_assistant.rag.modes import ConversationMode, get_mode_policy


def build_query_context(
    chunks: List[Dict],
    *,
    mode: ConversationMode = ConversationMode.EXPLORATION,
) -> Dict:
    """
    Build a prompt-ready context from retrieved chunks.

    Input:
    - chunks: list of {"chunk_id", "score"} dicts

    Output (dict):
    {
        "context": str,        # fully expanded context text
        "chunk_count": int     # number of chunks included
    }

    Notes:
    - Pure function (no AI calls)
    - Deterministic
    - Safe to preview in UI before spending tokens
    """

    pairs = [(c["chunk_id"], c["score"]) for c in chunks]

    policy = get_mode_policy(mode)

    options = ContextOptions(
        prefer_full_code=policy.prefer_full_code,
        expand_inheritance_depth=policy.expand_inheritance_depth,
        inject_project_overview=policy.inject_project_overview,
    )

    context = build_context(pairs, options)

    return {
        "context": context,
        "chunk_count": len(chunks),
    }
