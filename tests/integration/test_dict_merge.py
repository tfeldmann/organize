from unittest.mock import call

from conftest import create_filesystem
from organize.cli import main


def test_multiple_regex_placeholders(tmp_path, mock_echo):
    create_filesystem(
        tmp_path,
        files=["test-123.jpg", "other-456.pdf"],
        config=r"""
        rules:
        - folders: files
          filters:
            - regex: (?P<word>\w+)-(?P<number>\d+).*
            - regex: (?P<all>.+?)\.\w{3}
            - extension
          actions:
            - echo: '{regex.word} {regex.number} {regex.all} {extension}'
        """,
    )
    main(["run", "--config-file=%s" % (tmp_path / "config.yaml")])
    mock_echo.assert_has_calls(
        (
            call("test 123 test-123 jpg"),
            call("other 456 other-456 pdf"),
        ),
        any_order=True,
    )
