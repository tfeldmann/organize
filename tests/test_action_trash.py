import os
from mock import patch

from organize.actions import Trash
from organize.utils import Path

USER_DIR = os.path.expanduser('~')

def test_trash():
    with patch('send2trash.send2trash') as m:
        trash = Trash()
        trash.run(Path('~/this/file.tar.gz'), {}, False)
        m.assert_called_with(os.path.join(USER_DIR, 'this', 'file.tar.gz'))
