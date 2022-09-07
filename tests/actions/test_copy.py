from copy import deepcopy

import pytest
from conftest import make_files, read_files
from fs.base import FS

from organize import core

files = {
    "test.txt": "",
    "file.txt": "Hello world\nAnother line",
    "another.txt": "",
    "folder": {
        "x.txt": "",
    },
}


@pytest.fixture
def testfiles(testfs) -> FS:
    make_files(testfs, files)
    yield testfs


def test_copy_on_itself(testfiles):
    config = """
    rules:
      - locations: "/"
        actions:
          - copy: "/"
    """
    core.run(config, simulate=False, working_dir=testfiles)
    result = read_files(testfiles)
    assert result == files


def test_copy_basic(testfs):
    config = """
    rules:
      - locations: "."
        filters:
          - name: test
        actions:
          - copy: newname.pdf
    """
    make_files(testfs, ["asd.txt", "newname 2.pdf", "newname.pdf", "test.pdf"])
    core.run(config, simulate=False, working_dir=testfs)
    assert read_files(testfs) == {
        "newname.pdf": "",
        "newname 2.pdf": "",
        "newname 3.pdf": "",
        "test.pdf": "",
        "asd.txt": "",
    }


def test_copy_into_dir(testfiles):
    config = """
    rules:
      - locations: "/"
        actions:
          - copy: "a brand/new/folder/"
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
        "a brand": {
            "new": {
                "folder": {
                    "test.txt": "",
                    "file.txt": "Hello world\nAnother line",
                    "another.txt": "",
                }
            }
        },
    }


def test_copy_into_dir_subfolders(testfiles):
    config = """
    rules:
      - locations: "/"
        subfolders: true
        actions:
          - copy: "a brand/new/folder/"
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
        "a brand": {
            "new": {
                "folder": {
                    "test.txt": "",
                    "file.txt": "Hello world\nAnother line",
                    "another.txt": "",
                    "x.txt": "",
                }
            }
        },
    }


@pytest.mark.parametrize(
    "mode,files,test_txt_content",
    [
        ("skip", ["file.txt", "test.txt"], "old"),
        ("overwrite", ["file.txt", "test.txt"], "new"),
        ("rename_new", ["file.txt", "test.txt", "test 2.txt"], "old"),
        ("rename_existing", ["file.txt", "test.txt", "test 2.txt"], "new"),
    ],
)
def test_copy_conflict(testfs: FS, mode, files, test_txt_content):
    config = """
    rules:
      - locations: "/"
        filters:
          - name: file
        actions:
          - copy:
              dest: "test.txt"
              on_conflict: {}
    """.format(
        mode
    )
    testfs.writetext("file.txt", "new")
    testfs.writetext("test.txt", "old")
    core.run(config, simulate=False, working_dir=testfs)
    assert set(testfs.listdir("/")) == set(files)
    assert testfs.readtext("file.txt") == "new"
    assert testfs.readtext("test.txt") == test_txt_content


def test_does_not_create_folder_in_simulation(testfs):
    config = """
        rules:
          - locations: "."
            actions:
              - copy: "new-subfolder/"
              - copy: "copyhere/"
        """
    make_files(testfs, files)
    core.run(config, simulate=True, working_dir=testfs)
    result = read_files(testfs)
    assert result == files

    core.run(config, simulate=False, working_dir=testfs)
    result = read_files(testfs)

    expected = deepcopy(files)
    expected["new-subfolder"] = deepcopy(files)
    expected["new-subfolder"].pop("folder")
    expected["copyhere"] = deepcopy(files)
    expected["copyhere"].pop("folder")

    assert result == expected
