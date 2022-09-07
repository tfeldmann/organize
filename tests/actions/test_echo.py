from datetime import datetime
from unittest.mock import patch

from organize.actions import Echo


def test_echo_basic():
    with patch.object(Echo, "print") as m:
        echo = Echo("Hello World")
        echo.run(simulate=False)
        m.assert_called_with("Hello World")


def test_echo_args():
    with patch.object(Echo, "print") as m:
        echo = Echo('Date formatting: {now.strftime("%Y-%m-%d")}')
        echo.run(simulate=False, now=datetime(2019, 1, 5))
        m.assert_called_with("Date formatting: 2019-01-05")


def test_echo_path():
    with patch.object(Echo, "print") as m:
        echo = Echo("{year}")
        echo.run(simulate=False, year=2017)
        m.assert_called_with("2017")
