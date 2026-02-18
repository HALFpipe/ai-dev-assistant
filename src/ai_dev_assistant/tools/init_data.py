"""
tools/init_data
Run the full HALFpipe indexing pipeline:

1. Chunk repository
2. Build embeddings
3. Build vector store
4. Export YAML preview

This is the canonical entrypoint for (re)indexing.
"""

from .index_repo import main as index_repo
# from tools.generate_docstrings import main as generate_docstrings
from .rebuild_embeddings import main as rebuild_embeddings
from .build_vector_store import main as build_vector_store
from .export_yaml_preview import main as export_yaml_preview


def main():
    index_repo()
    rebuild_embeddings()
    build_vector_store()
    export_yaml_preview()


if __name__ == "__main__":
    main()
