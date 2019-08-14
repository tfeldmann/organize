import os

from organize.actions import Move
from organize.compat import Path
from organize.utils import DotDict

USER_DIR = os.path.expanduser("~")


def test_tilde_expansion(mock_exists, mock_samefile, mock_move, mock_trash, mock_mkdir):
    attrs = DotDict({"basedir": Path.home(), "path": Path.home() / "test.py"})
    mock_exists.return_value = False
    mock_samefile.return_value = False
    move = Move(dest="~/newname.py", overwrite=False)
    new_path = move.run(attrs, False)
    mock_mkdir.assert_called_with(exist_ok=True, parents=True)
    mock_exists.assert_called_with()
    mock_trash.assert_not_called()
    mock_move.assert_called_with(
        src=os.path.join(USER_DIR, "test.py"), dst=os.path.join(USER_DIR, "newname.py")
    )
    assert new_path == Path("~/newname.py").expanduser()


def test_into_folder(mock_exists, mock_samefile, mock_move, mock_trash, mock_mkdir):
    attrs = DotDict({"basedir": Path.home(), "path": Path.home() / "test.py"})
    mock_exists.return_value = False
    mock_samefile.return_value = False
    move = Move(dest="~/somefolder/", overwrite=False)
    new_path = move.run(attrs, False)
    mock_mkdir.assert_called_with(exist_ok=True, parents=True)
    mock_exists.assert_called_with()
    mock_trash.assert_not_called()
    mock_move.assert_called_with(
        src=os.path.join(USER_DIR, "test.py"),
        dst=os.path.join(USER_DIR, "somefolder", "test.py"),
    )
    assert new_path == Path(USER_DIR) / "somefolder" / "test.py"


def test_overwrite(mock_exists, mock_samefile, mock_move, mock_trash, mock_mkdir):
    attrs = DotDict({"basedir": Path.home(), "path": Path.home() / "test.py"})
    mock_exists.return_value = True
    mock_samefile.return_value = False
    move = Move(dest="~/somefolder/", overwrite=True)
    new_path = move.run(attrs, False)
    mock_mkdir.assert_called_with(exist_ok=True, parents=True)
    mock_exists.assert_called_with()
    mock_trash.assert_called_with(os.path.join(USER_DIR, "somefolder", "test.py"))
    mock_move.assert_called_with(
        src=os.path.join(USER_DIR, "test.py"),
        dst=os.path.join(USER_DIR, "somefolder", "test.py"),
    )
    assert new_path is not None


def test_already_exists(mock_exists, mock_samefile, mock_move, mock_trash, mock_mkdir):
    attrs = DotDict({"basedir": Path.home(), "path": Path.home() / "test.py"})
    mock_exists.side_effect = [True, False]
    mock_samefile.return_value = False
    move = Move(dest="~/folder/", overwrite=False)
    new_path = move.run(attrs, False)
    mock_mkdir.assert_called_with(exist_ok=True, parents=True)
    mock_exists.assert_called_with()
    mock_trash.assert_not_called()
    mock_move.assert_called_with(
        src=os.path.join(USER_DIR, "test.py"),
        dst=os.path.join(USER_DIR, "folder", "test 2.py"),
    )
    assert new_path is not None


def test_already_exists_multiple(
    mock_exists, mock_samefile, mock_move, mock_trash, mock_mkdir
):
    attrs = DotDict({"basedir": Path.home(), "path": Path.home() / "test.py"})
    mock_exists.side_effect = [True, True, True, False]
    mock_samefile.return_value = False
    move = Move(dest="~/folder/", overwrite=False)
    new_path = move.run(attrs, False)
    mock_mkdir.assert_called_with(exist_ok=True, parents=True)
    mock_exists.assert_called_with()
    mock_trash.assert_not_called()
    mock_move.assert_called_with(
        src=os.path.join(USER_DIR, "test.py"),
        dst=os.path.join(USER_DIR, "folder", "test 4.py"),
    )
    assert new_path is not None


def test_already_exists_multiple_separator(
    mock_exists, mock_samefile, mock_move, mock_trash, mock_mkdir
):
    attrs = DotDict({"basedir": Path.home(), "path": Path.home() / "test.py"})
    mock_exists.side_effect = [True, True, True, False]
    mock_samefile.return_value = False
    move = Move(dest="~/folder/", overwrite=False, counter_separator="_")
    new_path = move.run(attrs, False)
    mock_mkdir.assert_called_with(exist_ok=True, parents=True)
    mock_exists.assert_called_with()
    mock_trash.assert_not_called()
    mock_move.assert_called_with(
        src=os.path.join(USER_DIR, "test.py"),
        dst=os.path.join(USER_DIR, "folder", "test_4.py"),
    )
    assert new_path is not None


def test_makedirs(mock_parent, mock_move, mock_trash):
    attrs = DotDict({"basedir": Path.home(), "path": Path.home() / "test.py"})
    move = Move(dest="~/some/new/folder/", overwrite=False)
    new_path = move.run(attrs, False)
    mock_parent.mkdir.assert_called_with(parents=True, exist_ok=True)
    mock_trash.assert_not_called()
    mock_move.assert_called_with(
        src=os.path.join(USER_DIR, "test.py"),
        dst=os.path.join(USER_DIR, "some", "new", "folder", "test.py"),
    )
    assert new_path is not None


def test_attrs(mock_exists, mock_samefile, mock_move, mock_trash, mock_mkdir):
    attrs = DotDict({
        "basedir": Path.home(),
        "path": Path.home() / "test.py",
        "nr": {"upper": 1},
    })
    mock_exists.return_value = False
    mock_samefile.return_value = False
    move = Move(dest="~/{nr.upper}-name.py", overwrite=False)
    new_path = move.run(attrs, False)
    mock_mkdir.assert_called_with(exist_ok=True, parents=True)
    mock_exists.assert_called_with()
    mock_trash.assert_not_called()
    mock_move.assert_called_with(
        src=os.path.join(USER_DIR, "test.py"), dst=os.path.join(USER_DIR, "1-name.py")
    )
    assert new_path is not None


def test_path(mock_exists, mock_samefile, mock_move, mock_trash, mock_mkdir):
    attrs = DotDict({"basedir": Path.home(), "path": Path.home() / "test.py"})
    mock_exists.return_value = False
    mock_samefile.return_value = False
    move = Move(dest="~/{path.stem}/{path.suffix}/{path.name}", overwrite=False)
    new_path = move.run(attrs, False)
    mock_mkdir.assert_called_with(exist_ok=True, parents=True)
    mock_exists.assert_called_with()
    mock_trash.assert_not_called()
    mock_move.assert_called_with(
        src=os.path.join(USER_DIR, "test.py"),
        dst=os.path.join(USER_DIR, "test", ".py", "test.py"),
    )
    assert new_path is not None


def test_keep_location(mock_exists, mock_samefile, mock_move, mock_trash, mock_mkdir):
    attrs = DotDict({"basedir": Path.home(), "path": Path.home() / "test.py"})
    mock_exists.return_value = True
    mock_samefile.return_value = True
    move = Move(dest="~/test.py")
    new_path = move.run(attrs, False)
    mock_mkdir.assert_not_called()
    mock_exists.assert_called_with()
    mock_trash.assert_not_called()
    mock_move.assert_not_called()
    assert new_path is not None


def test_dont_keep_case_sensitive(
    mock_exists, mock_samefile, mock_move, mock_trash, mock_mkdir
):
    attrs = DotDict({"basedir": Path.home(), "path": Path.home() / "test.py"})
    mock_exists.return_value = True
    mock_samefile.return_value = True
    move = Move(dest="~/TEST.PY")
    new_path = move.run(attrs, False)
    mock_mkdir.assert_called()
    mock_exists.assert_called_with()
    mock_trash.assert_not_called()
    mock_move.assert_called()
    assert new_path is not None
