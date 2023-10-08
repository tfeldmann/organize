from copy import deepcopy

import pytest
from conftest import make_files, read_files

from organize import Config

FILES = {
    "test.txt": "",
    "file.txt": "Hello world\nAnother line",
    "another.txt": "",
    "folder": {
        "x.txt": "",
    },
}


def test_copy_on_itself(fs):
    make_files(FILES, "test")
    config = """
    rules:
      - locations: "test"
        actions:
          - copy: "test"
    """
    Config.from_string(config).execute(simulate=False)
    result = read_files("test")
    assert result == FILES


def test_copy_basic(fs):
    config = """
    rules:
      - locations: "test"
        filters:
          - name: test
        actions:
          - copy: test/newname.pdf
    """
    make_files(["asd.txt", "newname 2.pdf", "newname.pdf", "test.pdf"], "test")
    Config.from_string(config).execute(simulate=False)
    assert read_files("test") == {
        "newname.pdf": "",
        "newname 2.pdf": "",
        "newname 3.pdf": "",
        "test.pdf": "",
        "asd.txt": "",
    }


def test_copy_into_dir(fs):
    make_files(FILES, "test")
    config = """
    rules:
      - locations: "test"
        actions:
          - copy: "test/a brand/new/folder/"
    """
    Config.from_string(config).execute(simulate=False)
    result = read_files("test")
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


def test_copy_into_dir_subfolders(fs):
    make_files(FILES, "test")
    config = """
    rules:
      - locations: "/test"
        subfolders: true
        actions:
          - copy: "/test/a brand/new/folder/"
    """
    Config.from_string(config).execute(simulate=False)
    result = read_files("test")
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
def test_copy_conflict(fs, mode, files, test_txt_content):
    make_files(
        {
            "file.txt": "new",
            "test.txt": "old",
        },
        "test",
    )
    config = f"""
    rules:
      - locations: "/test"
        filters:
          - name: file
        actions:
          - copy:
              dest: "test.txt"
              on_conflict: {mode}
    """
    Config.from_string(config).execute(simulate=False)
    assert read_files("test") == {
        "file.txt": "new",
        "test.txt": test_txt_content,
    }


def test_does_not_create_folder_in_simulation(fs):
    config = """
        rules:
          - locations: "/test"
            actions:
              - copy: "/test/new-subfolder/"
              - copy: "/test/copyhere/"
        """
    make_files(FILES, "test")
    Config.from_string(config).execute(simulate=True)
    result = read_files("test")
    assert result == FILES

    # core.run(config, simulate=False, working_dir=testfs)
    # result = read_files(testfs)

    # expected = deepcopy(files)
    # expected["new-subfolder"] = deepcopy(files)
    # expected["new-subfolder"].pop("folder")
    # expected["copyhere"] = deepcopy(files)
    # expected["copyhere"].pop("folder")

    # assert result == expected
