"""
tools/index_repo.py

Extract structural code chunks from a repository
and write them to the assistant data workspace.

This is a pure pipeline step:
- no CLI
- no env parsing
- no interactive defaults
"""

from __future__ import annotations

import json
from pathlib import Path

from ai_dev_assistant.rag.chunking import (
    chunk_project_overview,
    chunk_python_file,
)
from ai_dev_assistant.tools.defaults import (
    get_chunks_path,
    set_active_repo_name,
)


def main(*, repo_root: Path) -> None:
    """
    Index a repository into the assistant workspace.

    Parameters
    ----------
    repo_root : Path
        Root directory of the repository to index (READ ONLY).
    """
    repo_root = repo_root.expanduser().resolve()
    if not repo_root.exists():
        raise RuntimeError(f"Repository does not exist: {repo_root}")

    repo_name = repo_root.name  # ← stable, intentional

    print(f"Indexing repo '{repo_name}'")

    all_chunks: list[dict] = []

    # 1) Project overview
    project_chunk = chunk_project_overview(repo_root)
    all_chunks.append(project_chunk.__dict__)

    # 2) Python source files
    for py_file in repo_root.rglob("*.py"):
        for chunk in chunk_python_file(py_file):
            all_chunks.append(chunk.__dict__)

    # 3) Write to ASSISTANT DATA DIR
    chunks_path = get_chunks_path(repo_name)
    chunks_path.parent.mkdir(parents=True, exist_ok=True)
    chunks_path.write_text(
        json.dumps(all_chunks, indent=2),
        encoding="utf-8",
    )

    # 4) Mark active repo
    set_active_repo_name(repo_name)

    print(f"Indexed {len(all_chunks)} chunks.")
    print(f"Saved to {chunks_path}")
