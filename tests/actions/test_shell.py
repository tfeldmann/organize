from unittest.mock import patch

from organize.actions import Shell
from pathlib import Path


def test_shell_basic():
    with patch("subprocess.call") as m:
        shell = Shell("echo 'Hello World'")
        shell.run(path=Path.home(), simulate=False)
        m.assert_called_with("echo 'Hello World'", shell=True)


def test_shell_args():
    with patch("subprocess.call") as m:
        shell = Shell("echo {year}")
        shell.run(path=Path.home(), year=2017, simulate=False)
        m.assert_called_with("echo 2017", shell=True)


def test_shell_path():
    with patch("subprocess.call") as m:
        shell = Shell("echo {path.stem} for {year}")
        shell.run(path=Path("/") / "this" / "isafile.txt", year=2017, simulate=False)
        m.assert_called_with("echo isafile for 2017", shell=True)
