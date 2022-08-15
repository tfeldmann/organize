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
        ("rename_new", ["file.txt", "test.txt", "test 1.txt"], "old"),
        ("rename_existing", ["file.txt", "test.txt", "test 1.txt"], "new"),
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
