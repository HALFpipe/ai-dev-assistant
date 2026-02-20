# rag/llm_reasoning.py
from __future__ import annotations


from .config import LLM_MODEL
from ai_dev_assistant.infra.ai_client import get_ai_client


def build_prompt(
    *,
    query: str,
    context: str,
    conversational_directive: str,
    memory: str | None = None,
) -> str:
    """
    Build the final LLM prompt.

    The conversational_directive is injected from the selected ConversationMode policy.
    """

    parts: list[str] = []

    # System framing
    parts.append("You are a senior engineer helping a teammate understand a codebase.")

    # Mode-specific reasoning style
    parts.append(conversational_directive)

    # Conversation memory (optional)
    if memory:
        parts.append("\n=== Conversation Memory ===\n")
        parts.append(memory)

    # Code context
    parts.append("\n=== Code Context ===\n")
    parts.append(context)

    # User question
    parts.append("\n=== Question ===\n")
    parts.append(query)

    # Instruction
    parts.append("\nAnswer clearly and directly, as in a code review discussion.")

    return "\n".join(parts).strip()


def explain_llm(
    prompt: str,
    model: str = LLM_MODEL,
) -> str:
    """
    Core LLM call.
    No cost logic. No printing. No env vars.
    """
    client = get_ai_client()

    if client is None:
        return "[DRY RUN]"


    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content

