from pathlib import Path
from unittest.mock import patch

from organize.actions import Trash


def test_trash():
    with patch('send2trash.send2trash') as m:
        trash = Trash()
        trash.run(Path('~/this/file.tar.gz'), {}, False)
        m.assert_called_with(Path('~/this/file.tar.gz'))
