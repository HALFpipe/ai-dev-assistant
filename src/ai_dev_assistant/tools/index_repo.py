"""
index_repo.py

Extract structural code chunks from a repository
and write them to a JSON file.

This is the FIRST script running in the pipeline.

"""

import json
from pathlib import Path

from ai_dev_assistant.rag.chunking import (
    chunk_project_overview,
    chunk_python_file,
)
from ai_dev_assistant.tools.defaults import CHUNKS_FILE, DEFAULT_REPO_ROOT


def index_repo(
    *,
    repo_root: Path,
    output_file: Path,
) -> None:
    all_chunks: list[dict] = []

    # 1) PROJECT OVERVIEW
    project_chunk = chunk_project_overview(repo_root)
    all_chunks.append(project_chunk.__dict__)

    # 2) PYTHON SOURCE FILES
    for py_file in repo_root.rglob("*.py"):
        for chunk in chunk_python_file(py_file):
            all_chunks.append(chunk.__dict__)

    # 3) WRITE TO DISK
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(
        json.dumps(all_chunks, indent=2),
        encoding="utf-8",
    )

    print(f"Indexed {len(all_chunks)} chunks.")
    print(f"Saved to {output_file}")


# ------------------------------------------------------------
# DIRECT EXECUTION (HUMAN DEFAULTS)
# ------------------------------------------------------------


def main() -> None:
    index_repo(
        repo_root=DEFAULT_REPO_ROOT,
        output_file=CHUNKS_FILE,
    )


if __name__ == "__main__":
    main()
