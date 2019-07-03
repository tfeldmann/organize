from organize.actions import Echo
from organize.utils import Path

from mock import patch


def test_echo_basic():
    echo = Echo("Hello World")
    with patch.object(echo, "print") as m:
        echo.run({"path": Path("~")}, False)
        m.assert_called_with("Hello World")


def test_echo_attrs():
    echo = Echo("This is the year {year}")
    with patch.object(echo, "print") as m:
        echo.run({"path": Path("~"), "year": 2017}, False)
        m.assert_called_with("This is the year 2017")


def test_echo_path():
    attrs = {"path": Path("/this/isafile.txt"), "year": 2017}
    echo = Echo("{path.stem} for {year}")
    with patch.object(echo, "print") as m:
        echo.run(attrs, False)
        m.assert_called_with("isafile for 2017")
