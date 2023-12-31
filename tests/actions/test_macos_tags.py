import sys
from pathlib import Path

import pytest

from organize import Config
from organize.filters.macos_tags import list_tags


@pytest.mark.skipif(sys.platform != "darwin", reason="runs only on macOS")
def test_macos_action(tmp_path: Path):
    (tmp_path / "file.txt").touch()
    (tmp_path / "test.txt").touch()

    tag_param = "{name} ({% if name == 'file' %}GREEN{% else %}RED{% endif %})"
    Config.from_string(
        f"""
        rules:
          - locations: {tmp_path}
            filters:
              - name
            actions:
              - macos_tags: "{tag_param}"
        """
    ).execute(simulate=False)

    assert list_tags(tmp_path / "file.txt") == ["file (green)"]
    assert list_tags(tmp_path / "test.txt") == ["test (red)"]
