# app/ask_wth_memory.py
from __future__ import annotations

import uuid
from typing import Dict

from ai_dev_assistant.app.ask import ask
from ai_dev_assistant.infra.memory_sqlite import (
    load_conversation,
    save_conversation,
)
from ai_dev_assistant.rag.memory import (
    append_turn,
    build_memory_context,
    init_conversation,
)
from ai_dev_assistant.services.memory_summary import maybe_summarize


def ask_with_memory(
    query: str,
    *,
    conversation_id: str | None = None,
    mode: str | None = None,
    k: int = 5,
) -> Dict:
    """
    High-level conversational entrypoint with memory support.
    """

    # ---------------------------------
    # Conversation identity
    # ---------------------------------
    if conversation_id is None:
        conversation_id = str(uuid.uuid4())

    # ---------------------------------
    # Load or initialize memory
    # ---------------------------------
    state = load_conversation(conversation_id)
    if state is None:
        state = init_conversation()

    # ---------------------------------
    # Inject memory into prompt context
    # ---------------------------------
    memory_context = build_memory_context(state)

    # ---------------------------------
    # Run core RAG pipeline
    # ---------------------------------
    result = ask(
        query=query,
        k=k,
        mode=mode,
        memory=memory_context,
    )

    # ---------------------------------
    # Update memory with new turns
    # ---------------------------------
    append_turn(state, "user", query)

    answer_text = (result.get("explanation", {}) or {}).get("answer")

    if answer_text:
        append_turn(state, "assistant", answer_text)

    # ---------------------------------
    # Summarize if needed
    # ---------------------------------
    maybe_summarize(state)
    print(state)
    # ---------------------------------
    # Persist memory
    # ---------------------------------
    save_conversation(conversation_id, state)

    return {
        **result,
        "conversation_id": conversation_id,
        "memory": {
            "summary": state["summary"],
            "recent_turns": len(state["recent_turns"]),
        },
    }
