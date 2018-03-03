import os

from organize.actions import Rename
from organize.utils import DotDict, Path

USER_DIR = os.path.expanduser('~')


def test_tilde_expansion(mock_exists, mock_samefile, mock_rename, mock_trash):
    basedir = Path('~')
    path = Path('~') / 'test.py'
    mock_exists.return_value = False
    mock_samefile.return_value = False
    rename = Rename(name='newname.py', overwrite=False)
    new_path = rename.run(basedir, path, {}, False)
    mock_exists.assert_called()
    mock_trash.assert_not_called()
    expected_path = (Path('~') / 'newname.py').expanduser()
    mock_rename.assert_called_with(expected_path)
    assert new_path == expected_path


def test_overwrite(mock_exists, mock_samefile, mock_rename, mock_trash):
    basedir = Path('~')
    path = Path('~') / 'test.py'
    mock_exists.return_value = True
    mock_samefile.return_value = False
    rename = Rename(name='{path.stem} Kopie.py', overwrite=True)
    rename.run(basedir, path, {}, False)
    mock_exists.assert_called()
    mock_trash.assert_called_with(os.path.join(USER_DIR, 'test Kopie.py'))
    mock_rename.assert_called_with(Path('~/test Kopie.py').expanduser())


def test_already_exists(mock_exists, mock_samefile, mock_rename, mock_trash):
    basedir = Path('~')
    path = Path('~') / 'test.py'
    mock_exists.side_effect = [True, False]
    mock_samefile.return_value = False
    rename = Rename(name='asd.txt', overwrite=False)
    rename.run(basedir, path, {}, False)
    mock_exists.assert_called()
    mock_trash.assert_not_called()
    mock_rename.assert_called_with(Path('~/asd 2.txt').expanduser())


def test_overwrite_samefile(mock_exists, mock_samefile, mock_rename, mock_trash):
    basedir = Path('~')
    path = Path('~') / 'test.PDF'
    mock_exists.return_value = True
    mock_samefile.return_value = True
    rename = Rename(name='{path.stem}.pdf', overwrite=False)
    rename.run(basedir, path, {}, False)
    mock_exists.assert_called()
    mock_trash.assert_not_called()
    mock_rename.assert_called_with(Path('~/test.pdf').expanduser())


def test_already_exists_multiple(mock_exists, mock_samefile, mock_rename, mock_trash):
    basedir = Path('~')
    path = Path('~') / 'test.py'
    mock_exists.side_effect = [True, True, True, False]
    mock_samefile.return_value = False
    rename = Rename(name='asd.txt', overwrite=False)
    rename.run(basedir, path, {}, False)
    mock_exists.assert_called()
    mock_trash.assert_not_called()
    mock_rename.assert_called_with(Path('~/asd 4.txt').expanduser())


def test_attrs(mock_exists, mock_samefile, mock_rename, mock_trash):
    basedir = Path('~')
    path = Path('~') / 'test.py'
    mock_exists.return_value = False
    mock_samefile.return_value = False
    rename = Rename(name='{nr.upper}-{path.stem} Kopie.py')
    rename.run(basedir, path, {'nr': DotDict({'upper': 1})}, False)
    mock_exists.assert_called()
    mock_trash.assert_not_called()
    mock_rename.assert_called_with(Path('~/1-test Kopie.py').expanduser())
