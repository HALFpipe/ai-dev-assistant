# tests/test_build_vector_store.py

from ai_dev_assistant.tools.build_vector_store import main as build_vector_store


def test_build_vector_store(precomputed_mini_repo):
    """
    Build the FAISS vector store from precomputed embeddings.

    Uses:
    - precomputed test data (tests/data/mini_repo)
    - isolated assistant data workspace

    Does NOT:
    - call OpenAI
    - compute embeddings
    - index a repository
    """
    build_vector_store()
