"""
tests/manual/ask_with_memory_demo.py

End-to-end conversational RAG demo WITH memory.

- Semantic search
- Context expansion
- Mode-driven behavior
- LLM explanation
- Persistent conversation memory (SQLite)

Run this multiple times with the same conversation_id
to observe memory accumulation and summarization.
"""

from ai_dev_assistant.app.ask_with_memory import ask_with_memory
from ai_dev_assistant.rag.modes import ConversationMode
from tests.manual.utils import print_answer


CONVERSATION_ID = "demo-fmriprep-memory"   # stable ID for testing
MODE = ConversationMode.DOCUMENTATION.value


def run_query(query: str):
    result = ask_with_memory(
        query=query,
        conversation_id=CONVERSATION_ID,
        mode=MODE,
        k=5,
    )

    print("\n=== QUERY ===")
    print(query)

    print("\n=== ANSWER ===\n")
    print_answer(result["explanation"])

    print("\n=== MEMORY STATE ===")
    print(f"Conversation ID: {result['conversation_id']}")
    print(f"Summary present: {bool(result['memory']['summary'])}")
    print(f"Recent turns kept: {result['memory']['recent_turns']}")


def main():
    # -----------------------------------------
    # First question (creates conversation)
    # -----------------------------------------
    run_query("How does FmriprepAdapterFactory work?")

    # -----------------------------------------
    # Follow-up question (uses memory)
    # -----------------------------------------
    run_query("How is it different from FmriprepFactory?")


if __name__ == "__main__":
    main()
