"""
cli.ask

Ask a single question against an indexed repository.

Pipeline:
- semantic search
- context assembly
- LLM explanation

Repository resolution:
- --repo <name> takes precedence
- otherwise uses LAST_ACTIVE_REPO
- errors if no repo is available
"""

from __future__ import annotations

import argparse

from ai_dev_assistant.rag.modes import ConversationMode
from ai_dev_assistant.services.context import build_query_context
from ai_dev_assistant.services.explain import explain_query
from ai_dev_assistant.services.search import search_query
from ai_dev_assistant.tools.defaults import (
    get_active_repo_name,
    get_repo_dir,
    set_active_repo_name,
)
from ai_dev_assistant.tools.utils import print_answer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ask a question about an indexed repository.")

    parser.add_argument(
        "query",
        type=str,
        help="Question to ask",
    )

    parser.add_argument(
        "--repo",
        type=str,
        default=None,
        help="Repository name (defaults to last active repo)",
    )

    parser.add_argument(
        "--k",
        type=int,
        default=5,
        help="Number of chunks to retrieve (default: 5)",
    )

    parser.add_argument(
        "--mode",
        type=str,
        choices=[m.value for m in ConversationMode],
        default=ConversationMode.DEBUGGING.value,
        help="Conversation mode (default: DEBUGGING)",
    )

    return parser.parse_args()


def resolve_repo(repo_arg: str | None) -> str:
    """
    Resolve repository context.

    Priority:
    1) --repo argument
    2) LAST_ACTIVE_REPO

    Raises if no repo is available.
    """
    if repo_arg:
        repo_dir = get_repo_dir(repo_arg)
        if not repo_dir.exists():
            raise RuntimeError(f"Repository '{repo_arg}' is not indexed.\nRun init_data or index_repo first.")
        set_active_repo_name(repo_arg)
        return repo_arg

    # fallback to last active
    try:
        return get_active_repo_name()
    except RuntimeError as err:
        raise RuntimeError("No active repository.\nRun init_data or specify --repo <name>.") from err


def main() -> None:
    args = parse_args()

    repo_name = resolve_repo(args.repo)

    print(f"📦 Repository: {repo_name}")

    # --------------------------------------------------
    # 1) Semantic search
    # --------------------------------------------------
    search_result = search_query(
        args.query,
        k=args.k,
    )

    # --------------------------------------------------
    # 2) Context assembly
    # --------------------------------------------------
    context_result = build_query_context(
        search_result["chunks"],
        mode=ConversationMode(args.mode),
    )

    context_text = context_result["context"]

    print("\n=== QUERY ===")
    print(args.query)

    print("\n=== CONTEXT SUMMARY ===")
    print(f"Chunks: {context_result['chunk_count']}")

    # --------------------------------------------------
    # 3) LLM explanation
    # --------------------------------------------------
    print("\n=== EXPLANATION ===\n")

    answer = explain_query(
        query=args.query,
        context=context_text,
        mode=ConversationMode(args.mode),
    )

    print_answer(answer)


if __name__ == "__main__":
    main()
