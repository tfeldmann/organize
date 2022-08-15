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
def testfiles(tempfs) -> FS:
    make_files(tempfs, files)
    yield tempfs


def test_copy_on_itself(testfiles):
    config = """
    rules:
      - locations: "/"
        actions:
          - move: "/"
    """
    core.run(config, simulate=True, working_dir=testfiles)
    result = read_files(testfiles)
    assert result == files


@pytest.mark.parametrize(
    "mode,files,test_txt_content",
    [
        ("skip", ["file.txt", "test.txt"], "old"),
        ("overwrite", ["test.txt"], "new"),
        ("rename_new", ["test.txt", "test 1.txt"], "old"),
        ("rename_existing", ["test.txt", "test 1.txt"], "new"),
    ],
)
def test_move_conflict(tempfs: FS, mode, files, test_txt_content):
    config = """
    rules:
      - locations: "/"
        filters:
          - name: file
        actions:
          - move:
              dest: "test.txt"
              on_conflict: {}
    """.format(
        mode
    )
    tempfs.writetext("file.txt", "new")
    tempfs.writetext("test.txt", "old")
    core.run(config, simulate=False, working_dir=tempfs)
    assert set(tempfs.listdir("/")) == set(files)
    assert tempfs.readtext("test.txt") == test_txt_content
