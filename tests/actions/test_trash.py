from unittest.mock import patch

from organize.actions import Trash


def test_trash():
    with patch("send2trash.send2trash") as mck:
        trash = Trash()
        trash.trash(path="~/Desktop/Test.zip", simulate=False)
        mck.assert_called_with("~/Desktop/Test.zip")
