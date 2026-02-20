"""
cli.build_vector_store

CLI entrypoint for building a FAISS vector store.

Usage:

    python -m ai_dev_assistant.cli.build_vector_store

Optional:

    python -m ai_dev_assistant.cli.build_vector_store --repo /path/to/repo

Notes:
- If --repo is provided, it becomes the active repository.
- Otherwise, the last active repository is used.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from ai_dev_assistant.tools.build_vector_store import main as build_vector_store
from ai_dev_assistant.tools.defaults import (
    set_active_repo_name,
    repo_name_from_path,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build FAISS vector store for an indexed repository."
    )

    parser.add_argument(
        "--repo",
        type=Path,
        help="Path to repository root (optional; overrides active repo)",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.repo:
        repo_root = args.repo.expanduser().resolve()
        if not repo_root.exists():
            raise RuntimeError(f"Repository does not exist: {repo_root}")

        repo_name = repo_name_from_path(repo_root)
        set_active_repo_name(repo_name)

    build_vector_store()


if __name__ == "__main__":
    main()
