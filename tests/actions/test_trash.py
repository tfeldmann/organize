import os

from organize.actions import Trash
from pathlib import Path

USER_DIR = os.path.expanduser("~")


def test_trash(mock_trash):
    trash = Trash()
    trash.run(path=Path.home() / "this" / "file.tar.gz", simulate=False)
    mock_trash.assert_called_with(os.path.join(USER_DIR, "this", "file.tar.gz"))
