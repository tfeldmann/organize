from mock import patch

from organize.actions import Python
from organize.compat import Path


def test_print_substitution():
    with patch.object(Python, "print") as mock_print:
        python = Python("print('Hello World')")
        python.run(path=Path.home(), simulate=False)
        mock_print.assert_called_with("Hello World")


def test_code_execution():
    with patch.object(Python, "print") as mock_print:
        path = Path("/some/folder")
        python = Python("print(args.x)\nprint(args.path)")
        python.run(path=path, x=42, simulate=False)
        mock_print.assert_any_call(42)
        mock_print.assert_any_call(path)
