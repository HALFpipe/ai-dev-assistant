"""
cli.init_data

Run the full ai_dev_assistant indexing pipeline:

1. Chunk repository
2. Build embeddings
3. Build vector store
4. Export YAML preview

This is the canonical entrypoint for indexing a repository.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from ai_dev_assistant.tools.index_repo import index_repo
from ai_dev_assistant.tools.rebuild_embeddings import main as rebuild_embeddings
from ai_dev_assistant.tools.build_vector_store import main as build_vector_store
from ai_dev_assistant.tools.export_yaml_preview import main as export_yaml_preview
from ai_dev_assistant.tools.defaults import (
    repo_name_from_path,
    set_active_repo_name,
)


# ------------------------------------------------------------
# CLI
# ------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Initialize assistant data for a repository."
    )

    parser.add_argument(
        "--repo",
        type=Path,
        required=True,
        help="Path to the repository to index",
    )

    return parser.parse_args()


# ------------------------------------------------------------
# PIPELINE
# ------------------------------------------------------------

def main() -> None:
    args = parse_args()

    repo_root = args.repo.expanduser().resolve()
    if not repo_root.exists():
        raise RuntimeError(f"Repository does not exist: {repo_root}")

    repo_name = repo_name_from_path(repo_root)

    print(f"📦 Indexing repository: {repo_name}")
    print(f"📁 Repo path: {repo_root}")

    # 1️⃣ Set active repo
    set_active_repo_name(repo_name)

    # 2️⃣ Run pipeline
    index_repo(repo_root=repo_root)
    rebuild_embeddings()
    build_vector_store()
    export_yaml_preview()

    print("\n✅ Indexing complete")
    print(f"Active repository: {repo_name}")


if __name__ == "__main__":
    main()
