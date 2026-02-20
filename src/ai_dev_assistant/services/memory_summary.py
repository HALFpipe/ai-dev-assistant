# services/memory_summary.py

"""
services.memory_summary

Conversation memory summarization service.

Responsibilities:
- decide when summarization is needed
- build summarization prompt
- call LLM (unless DRY_RUN)
- apply summary to conversation state

It does NOT:
- store memory
- track retrieval
- format UI output
"""

from ai_dev_assistant.infra.config import is_dry_run, LLM_MODEL
from ai_dev_assistant.infra.llm_reasoning import explain_llm
from ai_dev_assistant.rag.memory import (
    ConversationState,
    apply_summary,
    build_summarization_prompt,
    needs_summarization,
)


def maybe_summarize(
    state: ConversationState,
    *,
    max_turns: int = 6,
    keep_last_n: int = 2,
) -> bool:
    """
    Conditionally summarize conversation memory.

    Returns
    -------
    bool
        True if summarization was performed.
    """

    if not needs_summarization(state, max_turns=max_turns):
        return False

    prompt = build_summarization_prompt(
        summary=state["summary"],
        turns=state["recent_turns"],
    )

    if is_dry_run():
        # In dry run, do NOT modify memory
        return False

    new_summary = explain_llm(
        prompt,
        model=LLM_MODEL,
    )

    apply_summary(
        state,
        new_summary=new_summary,
        keep_last_n=keep_last_n,
    )

    return True
