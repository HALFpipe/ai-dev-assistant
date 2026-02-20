"""
cli.chat

Interactive conversational CLI with persistent memory.

Features:
- Semantic search
- Context expansion
- LLM explanation
- SQLite-backed conversation memory
- REPL-style interaction

Exit with Ctrl+C or 'exit'.
"""

from __future__ import annotations
import readline  # noqa: F401
import argparse
import uuid

from ai_dev_assistant.app.ask_with_memory import ask_with_memory
from ai_dev_assistant.rag.modes import ConversationMode
from ai_dev_assistant.tools.utils import print_answer
from ai_dev_assistant.tools.defaults import get_active_repo_name

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Interactive conversational RAG with memory."
    )

    parser.add_argument(
        "--conversation-id",
        type=str,
        default=None,
        help="Conversation ID to resume (default: new conversation)",
    )

    parser.add_argument(
        "--mode",
        type=str,
        choices=[m.value for m in ConversationMode],
        default=ConversationMode.DOCUMENTATION.value,
        help="Conversation mode",
    )

    parser.add_argument(
        "--k",
        type=int,
        default=5,
        help="Number of chunks to retrieve per query",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    conversation_id = args.conversation_id or str(uuid.uuid4())
    mode = args.mode

    try:
        repo_name = get_active_repo_name()
    except RuntimeError as e:
        print("❌ No active repository.")
        print(e)
        print("\nRun:")
        print("  ai-dev-assistant init-data")
        return

    print("🧠 Conversational RAG started")
    print(f"📦 Active repository: {repo_name}")
    print(f"📌 Conversation ID: {conversation_id}")
    print(f"🧩 Mode: {mode}")
    print("Type 'exit' or press Ctrl+C to quit.\n")

    try:
        while True:
            query = input(">>> ").strip()

            if not query:
                continue

            if query.lower() in {"exit", "quit"}:
                print("👋 Goodbye")
                break

            result = ask_with_memory(
                query=query,
                conversation_id=conversation_id,
                mode=mode,
                k=args.k,
            )

            print("\n=== ANSWER ===\n")
            print_answer(result["explanation"])

            mem = result["memory"]
            print("\n=== MEMORY ===")
            print(f"Summary present: {bool(mem['summary'])}")
            print(f"Recent turns:    {mem['recent_turns']}")
            print()

    except KeyboardInterrupt:
        print("\n👋 Conversation ended")


if __name__ == "__main__":
    main()
