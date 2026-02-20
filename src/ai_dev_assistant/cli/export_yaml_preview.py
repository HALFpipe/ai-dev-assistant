"""
cli.export_yaml_preview

CLI entrypoint for exporting a YAML preview of indexed chunks.

Usage:
    python -m ai_dev_assistant.cli.export_yaml_preview
"""

from __future__ import annotations

from ai_dev_assistant.tools.export_yaml_preview import main as export_yaml_preview

def main() -> None:
    export_yaml_preview()


if __name__ == "__main__":
    main()
