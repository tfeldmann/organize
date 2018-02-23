import os

from organize.actions import Move
from organize.utils import DotDict, Path

USER_DIR = os.path.expanduser('~')


def test_tilde_expansion(mock_exists, mock_samefile, mock_move, mock_trash, mock_mkdir):
    path = Path('~') / 'test.py'
    mock_exists.return_value = False
    mock_samefile.return_value = False
    move = Move(dest='~/newname.py', overwrite=False)
    move.run(path, {}, False)
    mock_mkdir.assert_called_with(exist_ok=True, parents=True)
    mock_exists.assert_called_with()
    mock_trash.assert_not_called()
    mock_move.assert_called_with(
        src=os.path.join(USER_DIR, 'test.py'),
        dst=os.path.join(USER_DIR, 'newname.py'))


def test_into_folder(mock_exists, mock_samefile, mock_move, mock_trash, mock_mkdir):
    path = Path('~') / 'test.py'
    mock_exists.return_value = False
    mock_samefile.return_value = False
    move = Move(dest='~/somefolder/', overwrite=False)
    move.run(path, {}, False)
    mock_mkdir.assert_called_with(exist_ok=True, parents=True)
    mock_exists.assert_called_with()
    mock_trash.assert_not_called()
    mock_move.assert_called_with(
        src=os.path.join(USER_DIR, 'test.py'),
        dst=os.path.join(USER_DIR, 'somefolder', 'test.py'))


def test_overwrite(mock_exists, mock_samefile, mock_move, mock_trash, mock_mkdir):
    path = Path('~') / 'test.py'
    mock_exists.return_value = True
    mock_samefile.return_value = False
    move = Move(dest='~/somefolder/', overwrite=True)
    move.run(path, {}, False)
    mock_mkdir.assert_called_with(exist_ok=True, parents=True)
    mock_exists.assert_called_with()
    mock_trash.assert_called_with(
        os.path.join(USER_DIR, 'somefolder', 'test.py'))
    mock_move.assert_called_with(
        src=os.path.join(USER_DIR, 'test.py'),
        dst=os.path.join(USER_DIR, 'somefolder', 'test.py'))


def test_already_exists(mock_exists, mock_samefile, mock_move, mock_trash, mock_mkdir):
    path = Path('~') / 'test.py'
    mock_exists.side_effect = [True, False]
    mock_samefile.return_value = False
    move = Move(dest='~/folder/', overwrite=False)
    move.run(path, {}, False)
    mock_mkdir.assert_called_with(exist_ok=True, parents=True)
    mock_exists.assert_called_with()
    mock_trash.assert_not_called()
    mock_move.assert_called_with(
        src=os.path.join(USER_DIR, 'test.py'),
        dst=os.path.join(USER_DIR, 'folder', 'test 2.py'))


def test_already_exists_multiple(mock_exists, mock_samefile, mock_move, mock_trash, mock_mkdir):
    path = Path('~') / 'test.py'
    mock_exists.side_effect = [True, True, True, False]
    mock_samefile.return_value = False
    move = Move(dest='~/folder/', overwrite=False)
    move.run(path, {}, False)
    mock_mkdir.assert_called_with(exist_ok=True, parents=True)
    mock_exists.assert_called_with()
    mock_trash.assert_not_called()
    mock_move.assert_called_with(
        src=os.path.join(USER_DIR, 'test.py'),
        dst=os.path.join(USER_DIR, 'folder', 'test 4.py'))


def test_makedirs(mock_parent, mock_move, mock_trash):
    path = Path('~') / 'test.py'
    move = Move(dest='~/some/new/folder/', overwrite=False)
    move.run(path, {}, False)
    mock_parent.mkdir.assert_called_with(parents=True, exist_ok=True)
    mock_trash.assert_not_called()
    mock_move.assert_called_with(
        src=os.path.join(USER_DIR, 'test.py'),
        dst=os.path.join(USER_DIR, 'some', 'new', 'folder', 'test.py'))


def test_attrs(mock_exists, mock_samefile, mock_move, mock_trash, mock_mkdir):
    path = Path('~') / 'test.py'
    mock_exists.return_value = False
    mock_samefile.return_value = False
    move = Move(dest='~/{nr.upper}-name.py', overwrite=False)
    move.run(path, {'nr': DotDict({'upper': 1})}, False)
    mock_mkdir.assert_called_with(exist_ok=True, parents=True)
    mock_exists.assert_called_with()
    mock_trash.assert_not_called()
    mock_move.assert_called_with(
        src=os.path.join(USER_DIR, 'test.py'),
        dst=os.path.join(USER_DIR, '1-name.py'))


def test_path(mock_exists, mock_samefile, mock_move, mock_trash, mock_mkdir):
    path = Path('~') / 'test.py'
    mock_exists.return_value = False
    mock_samefile.return_value = False
    move = Move(
        dest='~/{path.stem}/{path.suffix}/{path.name}',
        overwrite=False)
    move.run(path, {}, False)
    mock_mkdir.assert_called_with(exist_ok=True, parents=True)
    mock_exists.assert_called_with()
    mock_trash.assert_not_called()
    mock_move.assert_called_with(
        src=os.path.join(USER_DIR, 'test.py'),
        dst=os.path.join(USER_DIR, 'test', '.py', 'test.py'))
