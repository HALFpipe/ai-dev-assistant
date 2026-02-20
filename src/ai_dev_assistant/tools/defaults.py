"""
tools/defaults.py

Default paths for ai_dev_assistant artifacts.

Design:
- One global data workspace
- Located next to ai_dev_assistant repo by default
- Overrideable via environment variable
- Repo-scoped subdirectories
- Explicit active-repo tracking
"""


from pathlib import Path

# ============================================================
# ASSISTANT WORKSPACE (THIS REPO)
# ============================================================

ASSISTANT_ROOT = Path(__file__).resolve()

while not (ASSISTANT_ROOT / "pyproject.toml").exists():
    if ASSISTANT_ROOT.parent == ASSISTANT_ROOT:
        raise RuntimeError("Could not locate ai_dev_assistant repo root")
    ASSISTANT_ROOT = ASSISTANT_ROOT.parent

DATA_ROOT = ASSISTANT_ROOT / "data"


# ============================================================
# ACTIVE REPO STATE
# ============================================================

def get_active_repo_file() -> Path:
    return DATA_ROOT / "LAST_ACTIVE_REPO"


def set_active_repo_name(repo_name: str) -> None:
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    get_active_repo_file().write_text(repo_name)


def get_active_repo_name() -> str:
    f = get_active_repo_file()
    if not f.exists():
        raise RuntimeError(
            "No repository indexed yet.\n"
            "Run the index command first."
        )
    return f.read_text().strip()


# ============================================================
# REPO-SCOPED DIRECTORIES
# ============================================================

def get_repo_dir(repo_name: str | None = None) -> Path:
    """
    Return the data directory for a repository.

    If repo_name is None, uses the active repository.
    """
    if repo_name is None:
        repo_name = get_active_repo_name()

    return DATA_ROOT / repo_name


# ============================================================
# ARTIFACT PATHS
# ============================================================

def get_chunks_path(repo_name: str | None = None) -> Path:
    return get_repo_dir(repo_name) / "chunks.json"


def get_embeddings_path(repo_name: str | None = None) -> Path:
    return get_repo_dir(repo_name) / "embeddings.json"


def get_faiss_index_path(repo_name: str | None = None) -> Path:
    return get_repo_dir(repo_name) / "faiss.index"


def get_faiss_meta_path(repo_name: str | None = None) -> Path:
    return get_repo_dir(repo_name) / "faiss_meta.json"

def get_memory_db_path(repo_name: str | None = None) -> Path:
    return get_repo_dir(repo_name) / "memory.sqlite.db"

def repo_name_from_path(repo_root: Path) -> str:
    return repo_root.resolve().name

def get_yaml_preview_path(repo_name: str | None = None) -> Path:
    return get_repo_dir(repo_name) / "chunks.preview.yaml"
