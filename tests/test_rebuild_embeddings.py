# tests/test_rebuild_embeddings.py

from ai_dev_assistant.tools.rebuild_embeddings import main as rebuild_embeddings


def test_rebuild_embeddings(precomputed_mini_repo):
    """
    Rebuild embeddings from precomputed chunks.

    Uses golden test data and runs in DRY_RUN mode,
    verifying the pipeline stage executes without errors.
    """
    rebuild_embeddings()
