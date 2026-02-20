# tests/confest.py
# tests/conftest.py
import shutil
from pathlib import Path

import pytest

from ai_dev_assistant.tools.defaults import (
    get_repo_dir,
    repo_name_from_path,
    set_active_repo_name,
)

# --------------------------------------------------
# A) Repo under test (input)
# --------------------------------------------------


@pytest.fixture
def mini_repo(tmp_path) -> Path:
    """
    Copy the mini test repo into a temp directory.
    This is the INPUT repository.
    """
    src = Path(__file__).parent / "fixtures" / "mini_repo"
    dst = tmp_path / "mini_repo"
    shutil.copytree(src, dst)
    return dst


# --------------------------------------------------
# B) Isolated assistant workspace
# --------------------------------------------------


@pytest.fixture
def isolated_data_root(tmp_path, monkeypatch) -> Path:
    """Empty assistant workspace."""
    data_root = tmp_path / "data"
    data_root.mkdir(parents=True, exist_ok=True)

    monkeypatch.setenv("AI_DEV_ASSISTANT_DATA", str(data_root))
    monkeypatch.setenv("AI_DEV_ASSISTANT_DRY_RUN", "1")

    return data_root


# --------------------------------------------------
# C) Precomputed data installed (no OpenAI needed)
# --------------------------------------------------


@pytest.fixture
def precomputed_mini_repo(mini_repo, isolated_data_root):
    """
    Install precomputed assistant data for mini_repo.
    """
    repo_name = repo_name_from_path(mini_repo)
    set_active_repo_name(repo_name)

    src = Path(__file__).parent / "data" / repo_name
    dst = get_repo_dir(repo_name)
    shutil.copytree(src, dst, dirs_exist_ok=True)

    return repo_name


# --------------------------------------------------
# D) Active repository context
# --------------------------------------------------


@pytest.fixture
def active_repo_name(mini_repo, isolated_data_root) -> str:
    """
    Mark mini_repo as the active repository.
    """
    repo_name = repo_name_from_path(mini_repo)
    set_active_repo_name(repo_name)
    return repo_name
