from fs.base import FS
import pytest
from conftest import make_files, read_files

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
          - copy: "/"
    """
    core.run(config, simulate=True, working_dir=testfiles)
    result = read_files(testfiles)
    assert result == files


@pytest.mark.parametrize(
    "mode,files,test_txt_content",
    [
        ("skip", ["file.txt", "test.txt"], "old"),
        ("overwrite", ["file.txt", "test.txt"], "new"),
        ("rename_new", ["file.txt", "test.txt", "test 1.txt"], "old"),
        ("rename_existing", ["file.txt", "test.txt", "test 1.txt"], "new"),
    ],
)
def test_copy_on_conflict(tempfs: FS, mode, files, test_txt_content):
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
    tempfs.writetext("file.txt", "new")
    tempfs.writetext("test.txt", "old")
    core.run(config, simulate=False, working_dir=tempfs)
    assert set(tempfs.listdir("/")) == set(files)
    assert tempfs.readtext("file.txt") == "new"
    assert tempfs.readtext("test.txt") == test_txt_content


# def test_does_not_create_folder_in_simulation():
#     with fs.open_fs("mem://") as mem:
#         config = {
#             "rules": [
#                 {
#                     "locations": [
#                         {"path": "files", "filesystem": mem},
#                     ],
#                     "actions": [
#                         {"copy": {"dest": "files/new-subfolder/", "filesystem": mem}},
#                         {"copy": {"dest": "files/copyhere/", "filesystem": mem}},
#                     ],
#                 },
#             ]
#         }
#         make_files(mem, files)
#         core.run(config, simulate=True)
#         result = read_files(mem)
#         assert result == files

#         core.run(config, simulate=False, validate=False)
#         result = read_files(mem)

#         expected = deepcopy(files)
#         expected["files"]["new-subfolder"] = deepcopy(files["files"])
#         expected["files"]["new-subfolder"].pop("folder")
#         expected["files"]["copyhere"] = deepcopy(files["files"])
#         expected["files"]["copyhere"].pop("folder")

#         assert result == expected
