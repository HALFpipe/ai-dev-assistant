"""
tests/manual/context_expansion_demo.py
Manual retrieval + context expansion sanity check.

- Semantic search
- Context assembly
- Inheritance + overview expansion
- No LLM calls
"""

from ai_dev_assistant.rag.modes import ConversationMode
from ai_dev_assistant.services.context import build_query_context
from ai_dev_assistant.services.search import search_query

QUERY = "How does FmriprepAdapterFactory work?"
TOP_K = 5


def main():
    search_result = search_query(QUERY, k=TOP_K)

    context_result = build_query_context(
        search_result["chunks"],
        mode=ConversationMode.FULL,
    )

    print("=== QUERY ===")
    print(QUERY)

    print("\n=== RETRIEVED CHUNKS ===")
    for item in search_result["chunks"]:
        print(f"{item['chunk_id']}  score={item['score']:.4f}")

    print("\n=== CONTEXT (EXPANDED) ===")
    print(context_result["context"])

    print("\n=== CONTEXT STATS ===")
    print(f"Chunks: {context_result['chunk_count']}")


if __name__ == "__main__":
    main()
