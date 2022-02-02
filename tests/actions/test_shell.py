from unittest.mock import patch

from organize.actions import Shell
from pathlib import Path


def test_shell_basic():
    shell = Shell("echo 'Hello World'")
    result = shell.run(simulate=True)
    assert not result

    result = shell.run(simulate=False)
    assert result["shell"] == {"output": "Hello World\n", "returncode": 0}


def test_shell_template_simulation():
    shell = Shell("echo '{msg}'", run_in_simulation=True)
    result = shell.run(msg="Hello", simulate=True)
    assert result["shell"] == {"output": "Hello\n", "returncode": 0}
