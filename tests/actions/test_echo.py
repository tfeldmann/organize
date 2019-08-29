from organize.actions import Echo
from organize.compat import Path

from mock import patch

def test_echo_basic():
    echo = Echo("Hello World")
    with patch.object(echo, "print") as m:
        echo.run(path=Path('~'), simulate=False)
        m.assert_called_with("Hello World")


def test_echo_args():
    echo = Echo("This is the year {year}")
    with patch.object(echo, "print") as m:
        echo.run(path=Path('~'), simulate=False, year=2017)
        m.assert_called_with("This is the year 2017")


def test_echo_path():
    echo = Echo("{path.stem} for {year}")
    with patch.object(echo, "print") as m:
        echo.run(simulate=False, path=Path("/this/isafile.txt"), year=2017)
        m.assert_called_with("isafile for 2017")
