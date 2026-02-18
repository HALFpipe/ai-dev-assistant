"""
rag.memory
==========

Conversation memory management for the RAG system.

This module is responsible for:
- tracking conversation state
- deciding when summarization is needed
- producing compact summaries of earlier dialogue
- storing only the minimal context needed for follow-up questions

DESIGN RULES
----------------------
- This module contains *domain logic*, not API logic.
- It must NOT import FastAPI, GUI code, or printing utilities.
- It must NOT know *how* memory is persisted (file/db/etc).
- It must NOT talk directly to OpenAI.

"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Literal, Optional, TypedDict

# ============================================================
# TYPES
# ============================================================

Role = Literal["user", "assistant"]

ROLE_LABELS = {
    "user": "User",
    "assistant": "Assistant",
}


@dataclass(frozen=True)
class ConversationTurn:
    role: Role
    content: str


class ConversationState(TypedDict):
    summary: Optional[str]
    recent_turns: List[ConversationTurn]


# ============================================================
# HELPERS
# ============================================================


def turn_to_dict(turn: ConversationTurn) -> dict:
    return {
        "role": turn.role,
        "content": turn.content,
    }


def turn_from_dict(data: dict) -> ConversationTurn:
    return ConversationTurn(
        role=data["role"],
        content=data["content"],
    )


# ============================================================
# INITIALIZATION
# ============================================================


def init_conversation() -> ConversationState:
    return {
        "summary": None,
        "recent_turns": [],
    }


# ============================================================
# MEMORY UPDATES
# ============================================================


def append_turn(
    state: ConversationState,
    role: Role,
    content: str,
) -> None:
    state["recent_turns"].append(
        ConversationTurn(
            role=role,
            content=content.strip(),
        )
    )


# ============================================================
# SUMMARIZATION POLICY
# ============================================================


def needs_summarization(
    state: ConversationState,
    max_turns: int = 6,
) -> bool:
    return len(state["recent_turns"]) > max_turns


# ============================================================
# SUMMARIZATION
# ============================================================


def build_summarization_prompt(
    summary: Optional[str],
    turns: List[ConversationTurn],
) -> str:
    previous_summary = summary or "None"

    dialogue = "\n".join(f"{ROLE_LABELS[t.role]}: {t.content}" for t in turns)

    return f"""
You are summarizing a technical conversation between a user and an assistant.

Your goal:
- Preserve key facts, decisions, and explanations
- Remove repetition and irrelevant details
- Keep it short and precise
- Assume the reader is technical

Previous summary:
{previous_summary}

New dialogue to integrate:
{dialogue}

Produce an updated summary:
""".strip()


def apply_summary(
    state: ConversationState,
    new_summary: str,
    keep_last_n: int = 2,
) -> None:
    state["summary"] = new_summary
    state["recent_turns"] = state["recent_turns"][-keep_last_n:]


# ============================================================
# CONTEXT EXPORT
# ============================================================


def build_memory_context(state: ConversationState) -> str:
    parts: List[str] = []

    if state["summary"]:
        parts.append("Conversation summary:")
        parts.append(state["summary"])

    if state["recent_turns"]:
        parts.append("\nRecent conversation:")
        for t in state["recent_turns"]:
            parts.append(f"{ROLE_LABELS[t.role]}: {t.content}")

    return "\n".join(parts).strip()
