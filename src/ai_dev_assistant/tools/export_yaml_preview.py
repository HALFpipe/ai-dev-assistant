"""
export_yaml_preview.py

Convert chunks.json into a human-readable YAML preview
with proper multiline rendering.
"""

import json
from pathlib import Path

import yaml

JSON_INPUT = Path("../../../data/chunks.json")
YAML_OUTPUT = Path("../../../data/chunks.preview.yaml")


class LiteralString(str):
    """Marker class for multiline YAML literals."""


def literal_str_representer(dumper, data):
    return dumper.represent_scalar(
        "tag:yaml.org,2002:str",
        data,
        style="|",
    )


# IMPORTANT: register for SafeDumper, not default dumper
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
    data = json.loads(JSON_INPUT.read_text(encoding="utf-8"))

    data = convert_multiline_strings(data)

    YAML_OUTPUT.write_text(
        yaml.safe_dump(
            data,
            sort_keys=False,
            allow_unicode=True,
            width=120,
        ),
        encoding="utf-8",
    )

    print(f"YAML preview written to {YAML_OUTPUT}")


if __name__ == "__main__":
    main()
