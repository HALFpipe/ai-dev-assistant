"""
tests/manual/semantic_search_demo.py

Manual retrieval sanity check.

- Runs semantic search only
- No context building
- No LLM calls
"""

from ai_dev_assistant.services.search import search_query

QUERY = "How does FmriprepAdapterFactory work?"
TOP_K = 5


def main():
    result = search_query(QUERY, k=TOP_K)

    print("=== QUERY ===")
    print(result["query"])

    print("\n=== RETRIEVED CHUNKS ===")
    for item in result["chunks"]:
        print(f"{item['chunk_id']}  score={item['score']:.4f}")

    print("\n=== COST ===")
    print(result["cost"])


if __name__ == "__main__":
    main()
