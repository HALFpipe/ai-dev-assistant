# services/explain.py
"""
services.explain

LLM reasoning API.

This module is responsible for **reasoning and explanation**:
- builds the final prompt
- estimates LLM cost
- calls the LLM (unless DRY_RUN)
- returns the generated explanation

It does NOT:
- search vectors
- expand code context
- decide which chunks are relevant

Rule:
"explain.py answers: what does this code do and why?"
"""

from __future__ import annotations
from typing import Dict

from ai_dev_assistant.rag.modes import ConversationMode, get_mode_policy
from ai_dev_assistant.rag.cost import estimate_llm_cost
from ai_dev_assistant.infra.llm_reasoning import build_prompt, explain_llm
from ai_dev_assistant.infra.config import DRY_RUN, LLM_MODEL


def explain_query(
    *,
    query: str,
    context: str,
    mode: ConversationMode,
    memory: str | None = None,
    expected_output_tokens: int = 400,
) -> Dict:
    """
    Generate an explanation for a query using provided context, mode,
    and optional conversation memory.

    Input:
    - query: user question
    - context: fully assembled prompt context
    - mode: conversation mode (controls reasoning style)
    - memory: optional conversation memory text
    - expected_output_tokens: estimate for cost calculation

    Output (dict):
    {
        "query": str,
        "answer": str | None,
        "dry_run": bool,
        "cost": {
            "input_tokens": int,
            "output_tokens": int,
            "total_tokens": int,
            "estimated_cost": float
        }
    }
    """

    policy = get_mode_policy(mode)

    prompt = build_prompt(
        query=query,
        context=context,
        conversational_directive=policy.conversational_directive,
        memory=memory,
    )

    cost = estimate_llm_cost(
        prompt=prompt,
        expected_output_tokens=expected_output_tokens,
        model=LLM_MODEL,
    )

    if DRY_RUN:
        return {
            "query": query,
            "answer": None,
            "dry_run": True,
            "cost": cost,
        }

    answer = explain_llm(
        prompt,
        model=LLM_MODEL,
    )

    return {
        "query": query,
        "answer": answer,
        "dry_run": False,
        "cost": cost,
    }
