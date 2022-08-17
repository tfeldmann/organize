import pytest
from fs.base import FS
from conftest import make_files

from organize import core


@pytest.mark.parametrize(
    ("mode", "newline", "result"),
    [
        ("append", "true", "a\nb\nc\n"),
        ("append", "false", "abc"),
        ("prepend", "true", "c\nb\na\n"),
        ("prepend", "false", "cba"),
        ("overwrite", "true", "c\n"),
        ("overwrite", "false", "c"),
    ],
)
def test_append(testfs: FS, mode, newline, result):
    files = ["a.txt", "b.txt", "c.txt"]
    make_files(testfs, files)
    config = """
    rules:
      - locations: "."
        filters:
          - name
        actions:
          - write:
              text: "{name}"
              path: "out.txt"
              mode: %s
              newline: %s
    """ % (
        mode,
        newline,
    )
    core.run(config, simulate=False, working_dir=testfs)
    assert testfs.readtext("out.txt") == result
