import os

from organize.actions import Copy
from organize.utils import Path

USER_DIR = os.path.expanduser("~")


def test_tilde_expansion(mock_exists, mock_samefile, mock_copy, mock_trash, mock_mkdir):
    attrs = {"basedir": Path.home(), "path": Path.home() / "test.py"}
    mock_exists.return_value = False
    mock_samefile.return_value = False
    copy = Copy(dest="~/newname.py", overwrite=False)
    new_path = copy.run(attrs, False)
    mock_mkdir.assert_called_with(exist_ok=True, parents=True)
    mock_exists.assert_called_with()
    mock_trash.assert_not_called()
    mock_copy.assert_called_with(
        src=os.path.join(USER_DIR, "test.py"), dst=os.path.join(USER_DIR, "newname.py")
    )
    # keep old file path
    assert new_path == None


def test_into_folder(mock_exists, mock_samefile, mock_copy, mock_trash, mock_mkdir):
    attrs = {"basedir": Path.home(), "path": Path.home() / "test.py"}
    mock_exists.return_value = False
    mock_samefile.return_value = False
    copy = Copy(dest="~/somefolder/", overwrite=False)
    copy.run(attrs, False)
    mock_mkdir.assert_called_with(exist_ok=True, parents=True)
    mock_exists.assert_called_with()
    mock_trash.assert_not_called()
    mock_copy.assert_called_with(
        src=os.path.join(USER_DIR, "test.py"),
        dst=os.path.join(USER_DIR, "somefolder", "test.py"),
    )


def test_overwrite(mock_exists, mock_samefile, mock_copy, mock_trash, mock_mkdir):
    attrs = {"basedir": Path.home(), "path": Path.home() / "test.py"}
    mock_exists.return_value = True
    mock_samefile.return_value = False
    copy = Copy(dest="~/somefolder/", overwrite=True)
    copy.run(attrs, False)
    mock_mkdir.assert_called_with(exist_ok=True, parents=True)
    mock_exists.assert_called_with()
    mock_trash.assert_called_with(os.path.join(USER_DIR, "somefolder", "test.py"))
    mock_copy.assert_called_with(
        src=os.path.join(USER_DIR, "test.py"),
        dst=os.path.join(USER_DIR, "somefolder", "test.py"),
    )


def test_already_exists(mock_exists, mock_samefile, mock_copy, mock_trash, mock_mkdir):
    attrs = {"basedir": Path.home(), "path": Path.home() / "test.py"}
    mock_exists.side_effect = [True, False]
    mock_samefile.return_value = False
    copy = Copy(dest="~/folder/", overwrite=False)
    copy.run(attrs, False)
    mock_mkdir.assert_called_with(exist_ok=True, parents=True)
    mock_exists.assert_called_with()
    mock_trash.assert_not_called()
    mock_copy.assert_called_with(
        src=os.path.join(USER_DIR, "test.py"),
        dst=os.path.join(USER_DIR, "folder", "test 2.py"),
    )


def test_already_exists_multiple(
    mock_exists, mock_samefile, mock_copy, mock_trash, mock_mkdir
):
    attrs = {"basedir": Path.home(), "path": Path.home() / "test.py"}
    mock_exists.side_effect = [True, True, True, False]
    mock_samefile.return_value = False
    copy = Copy(dest="~/folder/", overwrite=False)
    copy.run(attrs, False)
    mock_mkdir.assert_called_with(exist_ok=True, parents=True)
    mock_exists.assert_called_with()
    mock_trash.assert_not_called()
    mock_copy.assert_called_with(
        src=os.path.join(USER_DIR, "test.py"),
        dst=os.path.join(USER_DIR, "folder", "test 4.py"),
    )


def test_already_exists_multiple_with_separator(
    mock_exists, mock_samefile, mock_copy, mock_trash, mock_mkdir
):
    attrs = {"basedir": Path.home(), "path": Path.home() / "test_2.py"}
    mock_exists.side_effect = [True, True, True, False]
    mock_samefile.return_value = False
    copy = Copy(dest="~/folder/", overwrite=False, counter_separator="_")
    copy.run(attrs, False)
    mock_mkdir.assert_called_with(exist_ok=True, parents=True)
    mock_exists.assert_called_with()
    mock_trash.assert_not_called()
    mock_copy.assert_called_with(
        src=os.path.join(USER_DIR, "test_2.py"),
        dst=os.path.join(USER_DIR, "folder", "test_5.py"),
    )


def test_makedirs(mock_parent, mock_copy, mock_trash):
    attrs = {"basedir": Path.home(), "path": Path.home() / "test.py"}
    copy = Copy(dest="~/some/new/folder/", overwrite=False)
    copy.run(attrs, False)
    mock_parent.mkdir.assert_called_with(parents=True, exist_ok=True)
    mock_trash.assert_not_called()
    mock_copy.assert_called_with(
        src=os.path.join(USER_DIR, "test.py"),
        dst=os.path.join(USER_DIR, "some", "new", "folder", "test.py"),
    )


def test_attrs(mock_exists, mock_samefile, mock_copy, mock_trash, mock_mkdir):
    attrs = {
        "basedir": Path.home(),
        "path": Path.home() / "test.py",
        "nr": {"upper": 1},
    }
    mock_exists.return_value = False
    mock_samefile.return_value = False
    copy = Copy(dest="~/{nr.upper}-name.py", overwrite=False)
    copy.run(attrs, False)
    mock_mkdir.assert_called_with(exist_ok=True, parents=True)
    mock_exists.assert_called_with()
    mock_trash.assert_not_called()
    mock_copy.assert_called_with(
        src=os.path.join(USER_DIR, "test.py"), dst=os.path.join(USER_DIR, "1-name.py")
    )


def test_path(mock_exists, mock_samefile, mock_copy, mock_trash, mock_mkdir):
    attrs = {"basedir": Path.home(), "path": Path.home() / "test.py"}
    mock_exists.return_value = False
    mock_samefile.return_value = False
    copy = Copy(dest="~/{path.stem}/{path.suffix}/{path.name}", overwrite=False)
    copy.run(attrs, False)
    mock_mkdir.assert_called_with(exist_ok=True, parents=True)
    mock_exists.assert_called_with()
    mock_trash.assert_not_called()
    mock_copy.assert_called_with(
        src=os.path.join(USER_DIR, "test.py"),
        dst=os.path.join(USER_DIR, "test", ".py", "test.py"),
    )
