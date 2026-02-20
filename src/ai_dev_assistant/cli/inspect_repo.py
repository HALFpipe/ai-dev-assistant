"""
cli.inspect

Inspect retrieval results with optional context expansion.

Purpose:
- Debug semantic search results
- Inspect expanded context (inheritance, overviews, neighbors)
- Validate chunk expansion logic
- No LLM calls

Pipeline:
- semantic search
- optional context expansion via build_query_context

Repository resolution:
- --repo <name> takes precedence
- otherwise uses LAST_ACTIVE_REPO
"""

from __future__ import annotations

import argparse

from ai_dev_assistant.rag.modes import ConversationMode
from ai_dev_assistant.services.context import build_query_context
from ai_dev_assistant.services.search import search_query
from ai_dev_assistant.tools.defaults import (
    get_active_repo_name,
    get_repo_dir,
    set_active_repo_name,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect semantic search results with optional context expansion.")

    parser.add_argument(
        "query",
        type=str,
        help="Query text",
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
        "--expand",
        action="store_true",
        help="Expand context (inheritance, overviews, neighbors)",
    )

    parser.add_argument(
        "--mode",
        type=str,
        choices=[m.value for m in ConversationMode],
        default=ConversationMode.DEBUGGING.value,
        help="Expansion mode (default: DEBUGGING)",
    )

    return parser.parse_args()


def resolve_repo(repo_arg: str | None) -> str:
    if repo_arg:
        repo_dir = get_repo_dir(repo_arg)
        if not repo_dir.exists():
            raise RuntimeError(f"Repository '{repo_arg}' is not indexed.\nRun init_data first.")
        set_active_repo_name(repo_arg)
        return repo_arg

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
    search_result = search_query(args.query, k=args.k)

    print("\n=== QUERY ===")
    print(args.query)

    print("\n=== RETRIEVED CHUNKS ===")
    for item in search_result["chunks"]:
        print(f"{item['chunk_id']}  score={item['score']:.4f}")

    # --------------------------------------------------
    # 2) Optional context expansion
    # --------------------------------------------------
    if args.expand:
        context_result = build_query_context(
            search_result["chunks"],
            mode=ConversationMode(args.mode),
        )

        print("\n=== CONTEXT (EXPANDED) ===")
        print(context_result["context"])

        print("\n=== CONTEXT STATS ===")
        print(f"Chunks: {context_result['chunk_count']}")
    else:
        print("\n(context expansion disabled)")


if __name__ == "__main__":
    main()
