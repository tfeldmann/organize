import os
from unittest.mock import patch

from organize.actions import Move
from organize.utils import DotDict, Path

USER_DIR = os.path.expanduser('~')


def test_tilde_expansion():
    p = Path('~') / 'test.py'
    with patch.object(Path, 'exists') as mock_exists, \
            patch('shutil.move') as mock_move, \
            patch('os.remove') as mock_remove:
        mock_exists.return_value = False
        move = Move(dest='~/newname.py', overwrite=False)
        move.run(p, {}, False)

        mock_exists.assert_called_with()
        mock_remove.assert_not_called()
        mock_move.assert_called_with(
            src=os.path.join(USER_DIR, 'test.py'),
            dst=os.path.join(USER_DIR, 'newname.py'))


def test_into_folder():
    p = Path('~') / 'test.py'
    with patch.object(Path, 'exists') as mock_exists, \
            patch('shutil.move') as mock_move, \
            patch('os.remove') as mock_remove:
        mock_exists.return_value = False
        move = Move(dest='~/somefolder/', overwrite=False)
        move.run(p, {}, False)

        mock_exists.assert_called_with()
        mock_remove.assert_not_called()
        mock_move.assert_called_with(
            src=os.path.join(USER_DIR, 'test.py'),
            dst=os.path.join(USER_DIR, 'somefolder', 'test.py'))

def test_overwrite():
    p = Path('~') / 'test.py'
    with patch.object(Path, 'exists') as mock_exists, \
            patch('shutil.move') as mock_move, \
            patch('os.remove') as mock_remove:
        mock_exists.return_value = True
        move = Move(dest='~/somefolder/', overwrite=True)
        move.run(p, {}, False)

        mock_exists.assert_called_with()
        mock_remove.assert_called_with(
            os.path.join(USER_DIR, 'somefolder', 'test.py'))
        mock_move.assert_called_with(
            src=os.path.join(USER_DIR, 'test.py'),
            dst=os.path.join(USER_DIR, 'somefolder', 'test.py'))

def test_already_exists():
    p = Path('~') / 'test.py'
    with patch.object(Path, 'exists') as mock_exists, \
            patch('shutil.move') as mock_move, \
            patch('os.remove') as mock_remove:
        mock_exists.side_effect = [True, False]
        move = Move(dest='~/folder/', overwrite=False)
        move.run(p, {}, False)

        mock_exists.assert_called_with()
        mock_remove.assert_not_called()
        mock_move.assert_called_with(
            src=os.path.join(USER_DIR, 'test.py'),
            dst=os.path.join(USER_DIR, 'folder', 'test 2.py'))


def test_already_exists_multiple():
    p = Path('~') / 'test.py'
    with patch.object(Path, 'exists') as mock_exists, \
            patch('shutil.move') as mock_move, \
            patch('os.remove') as mock_remove:
        mock_exists.side_effect = [True, True, True, False]
        move = Move(dest='~/folder/', overwrite=False)
        move.run(p, {}, False)

        mock_exists.assert_called_with()
        mock_remove.assert_not_called()
        mock_move.assert_called_with(
            src=os.path.join(USER_DIR, 'test.py'),
            dst=os.path.join(USER_DIR, 'folder', 'test 4.py'))


def test_makedirs():
    p = Path('~') / 'test.py'
    with patch.object(Path, 'parent') as mock_parent, \
            patch('shutil.move') as mock_move, \
            patch('os.remove') as mock_remove:
        move = Move(dest='~/some/new/folder/', overwrite=False)
        move.run(p, {}, False)

        mock_parent.mkdir.assert_called_with(parents=True, exist_ok=True)
        mock_remove.assert_not_called()
        mock_move.assert_called_with(
            src=os.path.join(USER_DIR, 'test.py'),
            dst=os.path.join(USER_DIR, 'some', 'new', 'folder', 'test.py'))


def test_attrs():
    p = Path('~') / 'test.py'
    with patch.object(Path, 'exists') as mock_exists, \
            patch('shutil.move') as mock_move, \
            patch('os.remove') as mock_remove:
        mock_exists.return_value = False
        move = Move(dest='~/{nr.upper}-name.py', overwrite=False)
        move.run(p, {'nr': DotDict({'upper': 1})}, False)

        mock_exists.assert_called_with()
        mock_remove.assert_not_called()
        mock_move.assert_called_with(
            src=os.path.join(USER_DIR, 'test.py'),
            dst=os.path.join(USER_DIR, '1-name.py'))


def test_path():
    p = Path('~') / 'test.py'
    with patch.object(Path, 'exists') as mock_exists, \
            patch('shutil.move') as mock_move, \
            patch('os.remove') as mock_remove:
        mock_exists.return_value = False
        move = Move(
            dest='~/{path.stem}/{path.suffix}/{path.name}',
            overwrite=False)
        move.run(p, {}, False)

        mock_exists.assert_called_with()
        mock_remove.assert_not_called()
        mock_move.assert_called_with(
            src=os.path.join(USER_DIR, 'test.py'),
            dst=os.path.join(USER_DIR, 'test', '.py', 'test.py'))
