# rag/llm_reasoning.py
from __future__ import annotations

from openai import OpenAI
from .config import LLM_MODEL

_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


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
    parts.append(
        "You are a senior engineer helping a teammate understand a codebase."
    )

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
    parts.append(
        "\nAnswer clearly and directly, as in a code review discussion."
    )

    return "\n".join(parts).strip()




def explain_llm(
    prompt: str,
    model: str = LLM_MODEL,
) -> str:
    """
    Core LLM call.
    No cost logic. No printing. No env vars.
    """
    client = get_client()

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content




# from openai import OpenAI
# from rag.cost import estimate_llm_cost, LLM_PRICES_PER_1M
# import os



#
# MODEL = "gpt-4.1-mini"
#
# DRY_RUN = os.environ.get("RAG_DRY_RUN", "0") == "1"
#
# client = OpenAI()
#
#
# def explain(query: str, context: str) -> str:
#     prompt = f"""
#     You are a senior engineer helping a teammate understand a codebase.
#
#     Answer the question using the provided context.
#
#     Be concise.
#     Be practical.
#     Explain behavior — not structure.
#     Avoid generic architectural wording.
#
#     Question:
#     {query}
#
#     Context:
#     {context}
#
#     Answer like you would in a code review discussion.
#     """
#
#     cost = estimate_llm_cost(
#         prompt,
#         expected_output_tokens=400,
#         model=MODEL,
#     )
#
#     print("=== LLM COST ESTIMATE ===")
#     print(cost)
#     print("=========================")
#
#     if DRY_RUN:
#         return "\n[DRY RUN — explanation skipped]\n"
#
#     response = client.chat.completions.create(
#         model=MODEL,
#         messages=[{"role": "user", "content": prompt}],
#     )
#
#     return response.choices[0].message.content
