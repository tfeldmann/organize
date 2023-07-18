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
        ("rename_new", ["test.txt", "test 2.txt"], "old"),
        ("rename_existing", ["test.txt", "test 2.txt"], "new"),
    ],
)
def test_move_conflict(testfs: FS, mode, files, test_txt_content):
    config = f"""
    rules:
      - locations: "/"
        filters:
          - name: file
        actions:
          - move:
              dest: "test.txt"
              on_conflict: {mode}
    """
    testfs.writetext("file.txt", "new")
    testfs.writetext("test.txt", "old")
    core.run(config, simulate=False, working_dir=testfs)
    assert set(testfs.listdir("/")) == set(files)
    assert testfs.readtext("test.txt") == test_txt_content
