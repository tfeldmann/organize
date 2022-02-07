from unittest.mock import call

import fs
from conftest import make_files, rules_shortcut
from organize import core


def test_multiple_regex_placeholders(mock_echo):
    files = {
        "files": {"test-123.jpg": "", "other-456.pdf": ""},
    }
    with fs.open_fs("mem://") as mem:
        rules = rules_shortcut(
            fs=mem,
            filters=r"""
                - regex: (?P<word>\w+)-(?P<number>\d+).*
                - regex: (?P<all>.+?)\.\w{3}
                - extension
            """,
            actions="""
                - echo: '{regex.word} {regex.number} {regex.all} {extension}'
            """,
        )
        make_files(mem, files)
        core.run(rules, simulate=False, validate=False)
        mock_echo.assert_has_calls(
            (
                call("test 123 test-123 jpg"),
                call("other 456 other-456 pdf"),
            ),
            any_order=True,
        )
