import os

from organize.actions import Rename
from pathlib import Path

USER_DIR = os.path.expanduser("~")

ARGS = {"basedir": Path.home(), "path": Path.home() / "test.py", "simulate": False}


def test_tilde_expansion(mock_exists, mock_samefile, mock_rename, mock_trash):
    mock_exists.return_value = False
    mock_samefile.return_value = False
    rename = Rename(name="newname.py", overwrite=False)
    new_path = rename.run(**ARGS)
    assert mock_exists.call_count > 0
    mock_trash.assert_not_called()
    expected_path = (Path.home() / "newname.py").expanduser()
    mock_rename.assert_called_with(expected_path)
    assert new_path == {'path': expected_path}


def test_overwrite(mock_exists, mock_samefile, mock_rename, mock_trash):
    mock_exists.return_value = True
    mock_samefile.return_value = False
    rename = Rename(name="{path.stem} Kopie.py", overwrite=True)
    new_path = rename.run(**ARGS)
    assert mock_exists.call_count > 0
    mock_trash.assert_called_with(os.path.join(USER_DIR, "test Kopie.py"))
    mock_rename.assert_called_with(Path("~/test Kopie.py").expanduser())
    assert new_path is not None


def test_already_exists(mock_exists, mock_samefile, mock_rename, mock_trash):
    mock_exists.side_effect = [True, False]
    mock_samefile.return_value = False
    rename = Rename(name="asd.txt", overwrite=False)
    new_path = rename.run(**ARGS)
    assert mock_exists.call_count > 0
    mock_trash.assert_not_called()
    mock_rename.assert_called_with(Path("~/asd 2.txt").expanduser())
    assert new_path is not None


def test_overwrite_samefile(mock_exists, mock_samefile, mock_rename, mock_trash):
    args = {"basedir": Path.home(), "path": Path.home() / "test.PDF", "simulate": False}
    mock_exists.return_value = True
    mock_samefile.return_value = True
    rename = Rename(name="{path.stem}.pdf", overwrite=False)
    new_path = rename.run(**args)
    assert mock_exists.call_count > 0
    mock_trash.assert_not_called()
    mock_rename.assert_called_with((Path.home() / "test.pdf").expanduser())
    assert new_path is not None


def test_keep_name(mock_exists, mock_samefile, mock_rename, mock_trash):
    args = {"basedir": Path.home(), "path": Path.home() / "test.pdf", "simulate": False}
    mock_exists.return_value = True
    mock_samefile.return_value = True
    rename = Rename(name="{path.stem}.pdf", overwrite=False)
    new_path = rename.run(**args)
    assert mock_exists.call_count > 0
    mock_trash.assert_not_called()
    mock_rename.assert_not_called()
    assert new_path is not None


def test_already_exists_multiple(mock_exists, mock_samefile, mock_rename, mock_trash):
    mock_exists.side_effect = [True, True, True, False]
    mock_samefile.return_value = False
    rename = Rename(name="asd.txt", overwrite=False)
    new_path = rename.run(**ARGS)
    assert mock_exists.call_count > 0
    mock_trash.assert_not_called()
    mock_rename.assert_called_with(Path("~/asd 4.txt").expanduser())
    assert new_path is not None


def test_already_exists_multiple_separator(
    mock_exists, mock_samefile, mock_rename, mock_trash
):
    mock_exists.side_effect = [True, True, True, False]
    mock_samefile.return_value = False
    rename = Rename(name="asd.txt", overwrite=False, counter_separator="-")
    new_path = rename.run(**ARGS)
    assert mock_exists.call_count > 0
    mock_trash.assert_not_called()
    mock_rename.assert_called_with(Path("~/asd-4.txt").expanduser())
    assert new_path is not None


def test_args(mock_exists, mock_samefile, mock_rename, mock_trash):
    args = {
        "basedir": Path.home(),
        "path": Path.home() / "test.py",
        "nr": {"upper": 1},
        "simulate": False,
    }

    mock_exists.return_value = False
    mock_samefile.return_value = False
    rename = Rename(name="{nr.upper}-{path.stem} Kopie.py")
    new_path = rename.run(**args)
    assert mock_exists.call_count > 0
    mock_trash.assert_not_called()
    mock_rename.assert_called_with(Path("~/1-test Kopie.py").expanduser())
    assert new_path is not None
