from mock import patch

from organize.actions import Python
from organize.compat import Path


def test_print_substitution():
    python = Python("print('Hello World')")
    with patch.object(python, "print") as mock_print:
        python.run({"path": Path.home()}, False)
        mock_print.assert_called_with("Hello World")


def test_code_execution():
    path = Path("/some/folder")
    python = Python("print(x)\nprint(path)")
    with patch.object(python, "print") as mock_print:
        python.run({"path": path, "x": 42}, False)
        mock_print.assert_any_call(42)
        mock_print.assert_any_call(path)
