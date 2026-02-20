"""
cli.index_repo

CLI entrypoint for indexing a repository into structural code chunks.

Run:

    python -m ai_dev_assistant.cli.index_repo --repo /path/to/repo

The indexed artifacts will be written to:

    <data_root>/<repo_name>/chunks.json
"""

from __future__ import annotations

import argparse
from pathlib import Path

from ai_dev_assistant.tools.index_repo import index_repo


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Index a Python repository into structural code chunks."
    )

    parser.add_argument(
        "--repo",
        type=Path,
        required=True,
        help="Path to the repository root to index",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    index_repo(
        repo_root=args.repo,
    )


if __name__ == "__main__":
    main()