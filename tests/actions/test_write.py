import os
import subprocess
import sys
from pathlib import Path

import pytest
from conftest import make_files, read_files

from organize.config import Config


@pytest.mark.skipif(
    sys.platform != "linux" or sys.getfilesystemencoding() != "utf-8",
    reason="requires Linux filenames with undecodable UTF-8 bytes",
)
def test_write_filename_with_undecodable_byte(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    undecodable = source / os.fsdecode(b"track-\xf6.mp3")
    undecodable.touch()
    (source / "z-caf\u00e9.mp3").touch()
    result = subprocess.run(
        [sys.executable, "-m", "organize.cli", "run", "--stdin"],
        cwd=tmp_path,
        input=b"""
        rules:
          - locations: source
            actions:
              - write:
                  text: "{path.name}"
                  outfile: output.txt
        """,
        capture_output=True,
        check=False,
        timeout=30,
        env={
            **os.environ,
            "PYTHONIOENCODING": "utf-8:strict",
            "XDG_STATE_HOME": str(tmp_path / "state"),
        },
    )
    assert result.returncode == 0, result.stderr.decode("utf-8")
    stdout = result.stdout.decode("utf-8")
    assert r"track-\udcf6.mp3" in stdout
    assert "success 2 / fail 0" in stdout
    assert (tmp_path / "output.txt").read_text(encoding="utf-8") == (
        "track-\\udcf6.mp3\nz-caf\u00e9.mp3\n"
    )
    assert undecodable.is_file()


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
        -   locations: "test"
            filters:
                - name: "a"
            actions:
                - write:
                    text: "{text}"
                    outfile: "new/folder/out.txt"
                    mode: {mode}
                    newline: {newline}
        -   locations: "test"
            filters:
                - name: "b"
            actions:
                - write:
                    text: "{text}"
                    outfile: "new/folder/out.txt"
                    mode: {mode}
                    newline: {newline}
        -   locations: "test"
            filters:
                - name: "c"
            actions:
                - write:
                    text: "{text}"
                    outfile: "new/folder/out.txt"
                    mode: {mode}
                    newline: {newline}
    """.format(text="{name}", mode=mode, newline=newline)

    Config.from_string(config).execute(simulate=False)
    with open("new/folder/out.txt") as f:
        assert result == f.read()


def test_write_manyfiles(fs):
    make_files({"test1.txt": "content\n", "test2.txt": "Other"}, "test")
    Config.from_string(
        """
        rules:
            -   locations: "/test"
                actions:
                    - write:
                        text: "WRITE {path.name}"
                        outfile: "/out/for-{path.stem}.txt"
                        mode: overwrite
                        clear_before_first_write: true
                        newline: false
        """
    ).execute(simulate=False)
    assert read_files("/out") == {
        "for-test1.txt": "WRITE test1.txt",
        "for-test2.txt": "WRITE test2.txt",
    }


def test_write_clear_then_append(fs):
    make_files({"test1.txt": "", "test2.txt": ""}, "loc1")
    make_files({"test1.txt": "", "test2.txt": ""}, "loc2")
    make_files(
        {
            "test1": {
                "test1.log": "Previous output",
            },
            "test2": {
                "test2.log": "Other previous output",
            },
        },
        "out",
    )
    Config.from_string(
        """
        rules:
            -   locations:
                    - "loc1"
                    - "loc2"
                actions:
                    - write:
                        text: "FOUND {path}"
                        outfile: "/out/{path.stem}/{path.stem}.log"
                        mode: append
                        clear_before_first_write: true
                        newline: true
        """
    ).execute(simulate=False)
    assert read_files("/out") == {
        "test1": {
            "test1.log": f"FOUND {Path('loc1/test1.txt')}\nFOUND {Path('loc2/test1.txt')}\n"
        },
        "test2": {
            "test2.log": f"FOUND {Path('loc1/test2.txt')}\nFOUND {Path('loc2/test2.txt')}\n"
        },
    }
