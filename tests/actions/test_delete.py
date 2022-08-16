import pytest
from conftest import make_files, read_files
from fs.base import FS

from organize import core

FILES = {
    "test.txt": "",
    "file.txt": "Hello world\nAnother line",
    "another.txt": "",
    "folder": {
        "x.txt": "",
        "empty_sub": {},
    },
    "empty_folder": {},
}


@pytest.fixture
def testfiles(testfs) -> FS:
    make_files(testfs, FILES)
    yield testfs


def test_delete_empty_files(testfiles):
    config = """
    rules:
      - name: "Recursively delete all empty files"
        locations:
          - path: "/"
        subfolders: true
        filters:
          - empty
        actions:
          - delete
    """
    core.run(config, simulate=False, working_dir=testfiles)
    result = read_files(testfiles)
    assert result == {
        "file.txt": "Hello world\nAnother line",
        "folder": {
            "empty_sub": {},
        },
        "empty_folder": {},
    }


def test_delete_empty_dirs(testfiles):
    config = """
    rules:
    - name: "Recursively delete all empty directories"
      locations: "/"
      subfolders: true
      targets: dirs
      filters:
        - empty
      actions:
        - delete
    """
    core.run(config, simulate=False, working_dir=testfiles)
    result = read_files(testfiles)
    assert result == {
        "test.txt": "",
        "file.txt": "Hello world\nAnother line",
        "another.txt": "",
        "folder": {
            "x.txt": "",
        },
    }
