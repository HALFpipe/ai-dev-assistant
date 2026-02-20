"""
tools.export_yaml_preview

Convert chunks.json into a human-readable YAML preview
with proper multiline rendering.

Pure pipeline step:
- no CLI
- no env parsing
- repo context resolved via defaults
"""

from __future__ import annotations

import json
import yaml

from ai_dev_assistant.tools.defaults import (
    get_chunks_path,
    get_yaml_preview_path,
    get_active_repo_name
)


class LiteralString(str):
    """Marker class for multiline YAML literals."""


def literal_str_representer(dumper, data):
    return dumper.represent_scalar(
        "tag:yaml.org,2002:str",
        data,
        style="|",
    )


# Register for SafeDumper
yaml.SafeDumper.add_representer(LiteralString, literal_str_representer)


def convert_multiline_strings(obj):
    """
    Recursively wrap multiline strings so PyYAML
    renders them using literal block style.
    """
    if isinstance(obj, dict):
        return {k: convert_multiline_strings(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_multiline_strings(v) for v in obj]
    if isinstance(obj, str) and "\n" in obj:
        return LiteralString(obj)
    return obj


def main() -> None:
    """
    Export YAML preview for the active repository.
    """
    print(f"Currently active repo:'{get_active_repo_name()}'")

    chunks_path = get_chunks_path()
    yaml_path = get_yaml_preview_path()

    if not chunks_path.exists():
        raise RuntimeError(
            f"No chunks.json found for active repo.\n"
            f"Expected at: {chunks_path}\n"
            f"Run index_repo first."
        )

    data = json.loads(chunks_path.read_text(encoding="utf-8"))
    data = convert_multiline_strings(data)

    yaml_path.parent.mkdir(parents=True, exist_ok=True)
    yaml_path.write_text(
        yaml.safe_dump(
            data,
            sort_keys=False,
            allow_unicode=True,
            width=120,
        ),
        encoding="utf-8",
    )

    print(f"YAML preview written to {yaml_path}")

if __name__ == "__main__":
    main()