from conftest import make_files, read_files

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


def test_delete_empty_files(testfs):
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
    make_files(testfs, FILES)
    core.run(config, simulate=False, working_dir=testfs)
    result = read_files(testfs)
    assert result == {
        "file.txt": "Hello world\nAnother line",
        "folder": {
            "empty_sub": {},
        },
        "empty_folder": {},
    }


def test_delete_empty_dirs(testfs):
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
    make_files(testfs, FILES)
    core.run(config, simulate=False, working_dir=testfs)
    result = read_files(testfs)
    assert result == {
        "test.txt": "",
        "file.txt": "Hello world\nAnother line",
        "another.txt": "",
        "folder": {
            "x.txt": "",
        },
    }


def test_delete_deep(testfs):
    files = {
        "files": {
            "folder": {
                "subfolder": {
                    "test.txt": "",
                    "other.pdf": "binary",
                },
                "file.txt": "Hello world\nAnother line",
            },
        }
    }
    make_files(testfs, files)
    config = """
    rules:
      - locations: "."
        actions:
          - delete
      - locations: "."
        targets: dirs
        actions:
          - delete
    """
    # sim
    core.run(config, simulate=True, working_dir=testfs)
    result = read_files(testfs)
    assert result == files

    # run
    core.run(config, simulate=False, working_dir=testfs)
    result = read_files(testfs)
    assert result == {}
