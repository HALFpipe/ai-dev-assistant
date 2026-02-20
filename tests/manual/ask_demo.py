"""
tests/manual/ask_demo.py

Manual retrieval + context + LLM explanation sanity check.

- Semantic search
- Context assembly via service layer
- Mode-driven behavior
- LLM explanation
"""

from utils import print_answer

from ai_dev_assistant.rag.modes import ConversationMode
from ai_dev_assistant.services.context import build_query_context
from ai_dev_assistant.services.explain import explain_query
from ai_dev_assistant.services.search import search_query

# QUERY = "How does FmriprepAdapterFactory work?"
QUERY = "How is the TotalReadoutTime field in the json fmap sidecar file suplied to the recreated rawdata structure"

TOP_K = 5


def main():
    # --------------------------------------------------
    # 1) Semantic search
    # --------------------------------------------------
    search_result = search_query(QUERY, k=TOP_K)

    # --------------------------------------------------
    # 2) Context assembly (mode-driven)
    # --------------------------------------------------
    context_result = build_query_context(
        search_result["chunks"],
        mode=ConversationMode.DEBUGGING,
    )

    context_text = context_result["context"]

    print("=== QUERY ===")
    print(QUERY)

    print("\n=== CONTEXT SUMMARY ===")
    print(f"Chunks: {context_result['chunk_count']}")

    # --------------------------------------------------
    # 3) LLM explanation
    # --------------------------------------------------
    print("\n=== EXPLANATION ===\n")

    answer = explain_query(
        query=QUERY,
        context=context_text,
        mode=ConversationMode.DEBUGGING,
    )

    print_answer(answer)


if __name__ == "__main__":
    main()
