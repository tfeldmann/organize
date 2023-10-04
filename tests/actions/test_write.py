import pytest
from conftest import make_files, read_files

from organize.config import Config


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
def test_write(fs, mode, newline, result):
    fs.create_file("test/a.txt")
    fs.create_file("test/b.txt")
    fs.create_file("test/c.txt")

    config = """
    rules:
      - locations: "test"
        filters:
          - name: "a"
        actions:
          - write:
              text: "{text}"
              path: "new/folder/out.txt"
              mode: {mode}
              newline: {newline}
      - locations: "test"
        filters:
          - name: "b"
        actions:
          - write:
              text: "{text}"
              path: "new/folder/out.txt"
              mode: {mode}
              newline: {newline}
      - locations: "test"
        filters:
          - name: "c"
        actions:
          - write:
              text: "{text}"
              path: "new/folder/out.txt"
              mode: {mode}
              newline: {newline}
    """.format(
        text="{name}", mode=mode, newline=newline
    )

    Config.from_string(config).execute(simulate=False)
    with open("new/folder/out.txt") as f:
        assert result == f.read()


def test_write_clearing(fs):
    make_files({"test1.txt": "content\n", "test2.txt": "Other"}, "test")
    Config.from_string(
        """
        rules:
            -   locations: "/test"
                actions:
                    - write:
                        text: "WRITE {path.name}"
                        path: "/out/for-{path.stem}.txt"
                        mode: append
                        clear_before_first_write: true
                        newline: false
        """
    ).execute(simulate=False)
    assert read_files("/out") == {
        "for-test1.txt": "WRITE test1.txt",
        "for-test2.txt": "WRITE test2.txt",
    }
