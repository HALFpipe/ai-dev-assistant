# tools/rebuild_embeddings.py
"""
Rebuild embeddings for the currently active repository.

Pipeline step:
- loads chunks.json
- computes embeddings
- writes embeddings.json

Repo context is resolved via LAST_ACTIVE_REPO.
"""

from __future__ import annotations

import json
from pathlib import Path

from ai_dev_assistant.infra.config import is_dry_run
from ai_dev_assistant.rag.embedding_pipeline import embed_chunks
from ai_dev_assistant.rag.schema import CodeChunk
from ai_dev_assistant.tools.defaults import (
    get_active_repo_name,
    get_chunks_path,
    get_embeddings_path,
)


def load_chunks(path: Path) -> list[CodeChunk]:
    if not path.exists():
        raise RuntimeError(f"Chunks file not found: {path}\nDid you run index_repo first?")

    raw = json.loads(path.read_text())
    return [CodeChunk(**item) for item in raw]


def main() -> None:
    chunks_path = get_chunks_path()
    embeddings_path = get_embeddings_path()

    chunks = load_chunks(chunks_path)

    print(f"Loaded {len(chunks)} chunks from repo '{get_active_repo_name()}'")

    records = embed_chunks(chunks, dry_run=is_dry_run())

    if not records:
        print("No embeddings generated (dry run?)")
        return

    embeddings_path.parent.mkdir(parents=True, exist_ok=True)
    embeddings_path.write_text(
        json.dumps(records, indent=2),
        encoding="utf-8",
    )

    print(f"Embedded {len(records)} chunks")
    print(f"Wrote embeddings to {embeddings_path}")
