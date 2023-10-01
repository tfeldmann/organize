import os
from glob import glob
from pathlib import Path
from typing import Dict, List, Union
from unittest.mock import patch

import pytest

ORGANIZE_DIR = Path(__file__).parent.parent


@pytest.fixture
def mock_echo():
    with patch("organize.actions.Echo.print") as mck:
        yield mck


def make_files(structure: Union[Dict, List], path: Union[Path, str] = "."):
    """
    Example structure:

        {
            "folder": {
                "subfolder": {
                    "test.txt": "",
                    "other.pdf": b"binary",
                },
            },
            "file.txt": "Hello world\nAnother line",
        }
    """
    if isinstance(path, str):
        path = Path(path)
    path.mkdir(parents=True, exist_ok=True)

    # structure is a list of filenames
    if isinstance(structure, list):
        for name in structure:
            (path / name).touch()
        return

    # structure is a dict
    for name, content in structure.items():
        resource: Path = path / name

        # folders are dicts
        if isinstance(content, dict):
            make_files(structure=content, path=resource)

        # everything else is a file
        elif content is None:
            resource.touch()
        elif isinstance(content, bytes):
            resource.write_bytes(content)
        elif isinstance(content, str):
            resource.write_text(content)
        else:
            raise ValueError(f"Unknown file data {content}")


def read_files(path: Union[Path, str] = "."):
    if isinstance(path, str):
        path = Path(path)

    result = dict()
    for x in path.glob("*"):
        if x.is_file():
            result[x.name] = x.read_text()
        if x.is_dir():
            result[x.name] = read_files(x)
    return result
