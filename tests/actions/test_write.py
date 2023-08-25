import pytest
from conftest import make_files
from fs.base import FS

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
def test_write(testfs: FS, mode, newline, result):
    files = ["a.txt", "b.txt", "c.txt"]
    make_files(testfs, files)
    config = """
    rules:
      - locations: "."
        filters:
          - name: "a"
        actions:
          - write:
              text: "{text}"
              path: "out.txt"
              mode: {mode}
              newline: {newline}
      - locations: "."
        filters:
          - name: "b"
        actions:
          - write:
              text: "{text}"
              path: "out.txt"
              mode: {mode}
              newline: {newline}
      - locations: "."
        filters:
          - name: "c"
        actions:
          - write:
              text: "{text}"
              path: "out.txt"
              mode: {mode}
              newline: {newline}
    """.format(
        text="{name}", mode=mode, newline=newline
    )
    core.run(config, simulate=False, working_dir=testfs)
    assert testfs.readtext("out.txt") == result
