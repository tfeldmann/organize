import fs
from unittest.mock import patch

from organize.actions import Trash
from organize.core import run


def test_trash_mocked():
    with patch("send2trash.send2trash") as mck:
        trash = Trash()
        trash.trash(path="~/Desktop/Test.zip", simulate=False)
        mck.assert_called_with("~/Desktop/Test.zip")


def test_trash_file():
    config = """
    rules:
      - locations: "."
        filters:
          - name: "test-trash-209318123"
        actions:
          - trash
    """
    with fs.open_fs("temp://") as tmp:
        tmp.writetext("test-trash-209318123.txt", "Content")
        assert tmp.exists("test-trash-209318123.txt")
        run(config, simulate=False, working_dir=tmp.getsyspath("/"))
        assert not tmp.exists("test-trash-209318123.txt")


def test_trash_folder():
    config = """
    rules:
      - locations: "."
        targets: dirs
        filters:
          - name: "test-trash-209318123"
        actions:
          - trash
    """
    with fs.open_fs("temp://") as tmp:
        tmp_dir = tmp.makedir("test-trash-209318123")
        tmp_dir.touch("file.txt")
        assert tmp.exists("test-trash-209318123/file.txt")
        run(config, simulate=False, working_dir=tmp.getsyspath("/"))
        assert not tmp.exists("test-trash-209318123/file.txt")
        assert not tmp.exists("test-trash-209318123")
