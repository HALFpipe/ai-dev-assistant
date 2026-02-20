"""
tools/build_vector_store.py

Build a FAISS vector store from embedded code chunks.

Pure pipeline step:
- no CLI
- no env parsing
- no interactive defaults
"""

from __future__ import annotations

import json

from ai_dev_assistant.infra.vector_store import VectorStore
from ai_dev_assistant.rag.config import VECTOR_DIM
from ai_dev_assistant.tools.defaults import (
    get_active_repo_name,
    get_embeddings_path,
    get_faiss_index_path,
    get_faiss_meta_path,
)


def main() -> None:
    print(f"Building vector store for '{get_active_repo_name()}'")

    embeddings_path = get_embeddings_path()

    if not embeddings_path.exists():
        raise RuntimeError("Embeddings file not found.\nRun rebuild_embeddings first.")

    records = json.loads(embeddings_path.read_text())

    store = VectorStore(dim=VECTOR_DIM)
    store.build(records)

    # Ensure repo data directory exists
    get_faiss_index_path().parent.mkdir(parents=True, exist_ok=True)

    store.save()

    print("FAISS index built and saved")
    print(f"Index: {get_faiss_index_path()}")
    print(f"Meta:  {get_faiss_meta_path()}")


if __name__ == "__main__":
    main()
