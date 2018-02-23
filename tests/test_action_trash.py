import os

from organize.actions import Trash
from organize.utils import Path

USER_DIR = os.path.expanduser('~')


def test_trash(mock_trash):
    trash = Trash()
    trash.run(Path('~/this/file.tar.gz'), {}, False)
    mock_trash.assert_called_with(os.path.join(USER_DIR, 'this', 'file.tar.gz'))
