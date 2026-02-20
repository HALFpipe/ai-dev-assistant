# tests/test_index_repo.py
from ai_dev_assistant.tools.index_repo import index_repo
from ai_dev_assistant.tools.defaults import (
    repo_name_from_path,
    get_chunks_path,
    get_active_repo_name,
)


def test_index_repo_creates_chunks(
    mini_repo,
    isolated_data_root,
):
    """
    Index a repository into structural chunks.

    Verifies that:
    - chunks.json is created in the assistant data workspace
    - the active repository is recorded
    """
    index_repo(repo_root=mini_repo)

    repo_name = repo_name_from_path(mini_repo)
    chunks_path = get_chunks_path(repo_name)

    assert chunks_path.exists()
    assert chunks_path.stat().st_size > 0

    # Active repo should be set
    assert get_active_repo_name() == repo_name

