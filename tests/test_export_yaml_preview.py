# tests/test_export_yaml_preview
# tests/test_export_yaml_preview.py

from ai_dev_assistant.tools.export_yaml_preview import main as export_yaml_preview
from ai_dev_assistant.tools.defaults import (
    get_yaml_preview_path,
)


def test_export_yaml_preview(precomputed_mini_repo):
    """
    Export YAML preview from precomputed chunks.json.

    This test assumes:
    - chunks.json already exists in the workspace
    - no indexing is performed here
    """

    # Act
    export_yaml_preview()

    # Assert (existence only; crash-free == success)
    yaml_path = get_yaml_preview_path()
    assert yaml_path.exists()
