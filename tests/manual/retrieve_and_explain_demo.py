"""
tests/manual/retrieve_and_explain_demo.py
End-to-end retrieval + explanation smoke test.

- Semantic search
- Context expansion
- LLM explanation
"""
"""
Manual retrieval + context + LLM explanation sanity check.

- Semantic search
- Context assembly via service layer
- Mode-driven behavior
- LLM explanation
"""

from ai_dev_assistant.services.search import search_query
from ai_dev_assistant.services.context import build_query_context
from ai_dev_assistant.services.explain import explain_query
from ai_dev_assistant.rag.modes import ConversationMode
from tests.manual.utils import print_answer

QUERY = "How does FmriprepAdapterFactory work?"
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
        mode=ConversationMode.DOCUMENTATION,
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
        mode=ConversationMode.DOCUMENTATION,
    )

    print_answer(answer)

if __name__ == "__main__":
    main()
