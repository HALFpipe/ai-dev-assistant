"""
tools/defaults.py
Default paths for manual and batch tooling.

These are developer-facing defaults, not runtime configuration.
Safe to change locally.
"""

from pathlib import Path

# Project root (repo root)
# Repo root = directory containing pyproject.toml
PROJECT_ROOT = Path(__file__).resolve()

while not (PROJECT_ROOT / "pyproject.toml").exists():
    if PROJECT_ROOT.parent == PROJECT_ROOT:
        raise RuntimeError("Could not find project root (pyproject.toml)")
    PROJECT_ROOT = PROJECT_ROOT.parent
# Canonical data directory
DATA_DIR = PROJECT_ROOT / "data"

# Repository to analyze (read-only)
DEFAULT_REPO_ROOT = Path("/home/tomas/github/HALFpipe/src/halfpipe")

# Derived artifacts
CHUNKS_FILE = DATA_DIR / "chunks.json"
EMBEDDINGS_FILE = DATA_DIR / "embeddings.json"
FAISS_INDEX_FILE = DATA_DIR / "faiss.index"
FAISS_META_FILE = DATA_DIR / "faiss_meta.json"
YAML_PREVIEW_FILE = DATA_DIR / "chunks.preview.yaml"

# Memory database
DB_PATH = DATA_DIR / "memory.sqlite.db"
