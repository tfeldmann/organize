from pathlib import Path

import pytest
from conftest import make_files, read_files

from organize.config import Config

FILES = {
    "test.txt": "",
    "file.txt": "Hello world\nAnother line",
    "another.txt": "",
    "folder": {
        "x.txt": "",
    },
}


@pytest.fixture
def testfiles(fs):
    make_files(FILES, path="test")
    yield


def test_copy_on_itself(testfiles):
    config = """
    rules:
      - locations: "test"
        actions:
          - move: "test"
    """
    Config.from_string(config).execute(simulate=False)
    assert read_files("test") == FILES


@pytest.mark.parametrize(
    "mode,files,test_txt_content",
    [
        ("skip", ["file.txt", "test.txt"], "old"),
        ("overwrite", ["test.txt"], "new"),
        ("rename_new", ["test.txt", "test 2.txt"], "old"),
        ("rename_existing", ["test.txt", "test 2.txt"], "new"),
    ],
)
def test_move_conflict(fs, mode, files, test_txt_content):
    config = """
    rules:
      - locations: "test"
        filters:
          - name: file
        actions:
          - move:
              dest: "test.txt"
              on_conflict: {}
    """.format(
        mode
    )
    fs.create_file("test/file.txt", contents="new")
    fs.create_file("test/test.txt", contents="old")
    Config.from_string(config).execute(simulate=False)
    testdir = Path("test")
    assert set(testdir.iterdir()) == set(files)
    assert (testdir / "test.txt").read_text() == test_txt_content
