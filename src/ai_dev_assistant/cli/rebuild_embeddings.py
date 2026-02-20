"""
cli.rebuild_embeddings

CLI entrypoint for rebuilding embeddings for an indexed repository.

Usage:

    python -m ai_dev_assistant.cli.rebuild_embeddings

Optional:

    python -m ai_dev_assistant.cli.rebuild_embeddings --repo /path/to/repo

Notes:
- If --repo is provided, it becomes the active repository.
- Otherwise, the last active repository is used.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from ai_dev_assistant.tools.defaults import (
    repo_name_from_path,
    set_active_repo_name,
)
from ai_dev_assistant.tools.rebuild_embeddings import main as rebuild_embeddings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rebuild embeddings for an indexed repository.")

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

    rebuild_embeddings()


if __name__ == "__main__":
    main()
